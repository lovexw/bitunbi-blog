#!/usr/bin/env python3
"""
将微信公众号导出的HTML文章批量转换为Markdown，用于Hugo博客。
支持多个数据源（公众号），输出到同一个Hugo项目。
"""

import os
import re
import html
import shutil
from html.parser import HTMLParser

# 多个数据源：文件夹路径 + 分类标签
SOURCES = [
    {
        "dir": "/Users/xw/Downloads/公众号数据/比特囤币",
        "category": "比特币",
        "tags": ["比特币", "囤币", "加密货币"],
    },
    {
        "dir": "/Users/xw/Downloads/公众号数据/比特囤币02",
        "category": "比特币",
        "tags": ["比特币", "囤币", "加密货币"],
    },
    {
        "dir": "/Users/xw/Downloads/公众号数据/小吴乐意",
        "category": "生活随笔",
        "tags": ["小吴乐意", "生活", "随笔"],
    },
]

OUTPUT_DIR = "/Users/xw/Downloads/公众号数据/blog-converter/content/posts"
IMAGE_OUTPUT_DIR = "/Users/xw/Downloads/公众号数据/blog-converter/static/images"


class WeChatHTMLParser(HTMLParser):
    def __init__(self, article_dir, image_subdir):
        super().__init__()
        self.article_dir = article_dir
        self.image_subdir = image_subdir
        self.in_content = False
        self.in_title = False
        self.in_publish_time = False
        self.in_blockquote = False
        self.in_link = False
        self.link_href = ""
        self.link_text = ""
        self.title = ""
        self.publish_time = ""
        self.content_parts = []
        self.current_text = ""
        self.img_counter = 0
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == "h1" and "rich_media_title" in attrs_dict.get("class", ""):
            self.in_title = True
            return
            
        if tag == "em" and attrs_dict.get("id") == "publish_time":
            self.in_publish_time = True
            return
            
        if tag == "div" and attrs_dict.get("id") == "js_content":
            self.in_content = True
            return
            
        if not self.in_content:
            return
            
        if tag == "section":
            if self.current_text.strip():
                self.content_parts.append(("text", self.current_text.strip()))
                self.current_text = ""
        elif tag == "p":
            if self.current_text.strip():
                self.content_parts.append(("text", self.current_text.strip()))
                self.current_text = ""
        elif tag == "blockquote":
            self.in_blockquote = True
            if self.current_text.strip():
                self.content_parts.append(("text", self.current_text.strip()))
                self.current_text = ""
        elif tag == "img":
            src = attrs_dict.get("src", "")
            if src.startswith("./assets/"):
                img_filename = os.path.basename(src)
                src_path = os.path.join(self.article_dir, "assets", img_filename)
                if os.path.exists(src_path):
                    self.img_counter += 1
                    dest_filename = f"{self.image_subdir}_{self.img_counter}_{img_filename}"
                    dest_path = os.path.join(IMAGE_OUTPUT_DIR, dest_filename)
                    shutil.copy2(src_path, dest_path)
                    self.content_parts.append(("image", f"/images/{dest_filename}"))
        elif tag == "a":
            self.in_link = True
            self.link_href = attrs_dict.get("href", "")
            self.link_text = ""
        elif tag == "br":
            pass
            
    def handle_endtag(self, tag):
        if tag == "h1" and self.in_title:
            self.in_title = False
        elif tag == "em" and self.in_publish_time:
            self.in_publish_time = False
        elif tag == "div" and self.in_content:
            if self.current_text.strip():
                self.content_parts.append(("text", self.current_text.strip()))
                self.current_text = ""
            self.in_content = False
        elif tag == "blockquote" and self.in_blockquote:
            self.in_blockquote = False
        elif tag == "a" and self.in_link:
            self.in_link = False
            link_t = self.link_text.strip()
            if link_t and self.link_href:
                self.content_parts.append(("link", (link_t, self.link_href)))
            self.link_text = ""
            self.link_href = ""
        elif tag == "section" and self.in_content:
            if self.current_text.strip():
                self.content_parts.append(("text", self.current_text.strip()))
                self.current_text = ""
                self.content_parts.append(("break", ""))
        elif tag == "p" and self.in_content:
            if self.current_text.strip():
                self.content_parts.append(("text", self.current_text.strip()))
                self.current_text = ""
                self.content_parts.append(("break", ""))
                
    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif self.in_publish_time:
            self.publish_time += data
        elif self.in_link:
            self.link_text += data
        elif self.in_content:
            self.current_text += data


def parse_date(date_str):
    if not date_str:
        return ""
    match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date_str)
    if match:
        return f"{match.group(1)}-{int(match.group(2)):02d}-{int(match.group(3)):02d}"
    return ""


def slugify(title, date_str):
    slug = re.sub(r'[^\w\u4e00-\u9fff\-]', '-', title.strip())
    slug = re.sub(r'-+', '-', slug).strip('-')
    if date_str:
        slug = f"{date_str}-{slug}"
    return slug[:80]


def convert_to_markdown(parser):
    lines = []
    for part_type, content in parser.content_parts:
        if part_type == "text":
            text = html.unescape(content).strip()
            if text:
                lines.append(text)
                lines.append("")
        elif part_type == "image":
            lines.append(f"![图片]({content})")
            lines.append("")
        elif part_type == "link":
            link_text, link_href = content
            link_text = html.unescape(link_text).strip()
            if link_href.startswith("http"):
                lines.append(f"[{link_text}]({link_href})")
                lines.append("")
        elif part_type == "break":
            pass
    return "\n".join(lines)


def process_article(article_dir_name, source):
    article_path = os.path.join(source["dir"], article_dir_name)
    html_path = os.path.join(article_path, "index.html")
    
    if not os.path.exists(html_path):
        return None, "no_html"
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    if 'rich_media_content' not in html_content:
        return None, "no_content"
    
    article_slug = re.sub(r'[^\w\u4e00-\u9fff\-]', '-', article_dir_name)[:60]
    
    parser = WeChatHTMLParser(article_path, article_slug)
    parser.feed(html_content)
    
    title = parser.title.strip() if parser.title else article_dir_name
    date_str = parse_date(parser.publish_time)
    
    if not date_str:
        m = re.match(r'^(\d{1,2})_(\d{1,2})', article_dir_name)
        if m:
            date_str = f"2025-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
        else:
            date_str = "2025-01-01"
    
    slug = slugify(title, date_str)
    markdown_content = convert_to_markdown(parser)
    
    if not markdown_content.strip():
        return None, "empty_content"
    
    # 处理标题中的引号
    safe_title = title.replace('"', '\\"')
    
    tags_str = ", ".join(f'"{t}"' for t in source["tags"])
    
    front_matter = f"""---
title: "{safe_title}"
date: {date_str}
draft: false
categories: ["{source['category']}"]
tags: [{tags_str}]
---

"""
    
    full_content = front_matter + markdown_content
    output_filename = f"{slug}.md"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    # 如果文件名冲突（两个公众号同名），加后缀
    if os.path.exists(output_path):
        output_filename = f"{slug}_{source['category']}.md"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    return {
        "title": title,
        "date": date_str,
        "filename": output_filename,
        "images": parser.img_counter,
        "source": source["category"],
    }, "ok"


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(IMAGE_OUTPUT_DIR, exist_ok=True)
    
    grand_total = 0
    grand_ok = 0
    grand_skipped = {}
    all_results = []
    
    for source in SOURCES:
        all_dirs = sorted(os.listdir(source["dir"]))
        all_dirs = [d for d in all_dirs if os.path.isdir(os.path.join(source["dir"], d))]
        
        print(f"\n{'='*50}")
        print(f"来源: {source['category']} ({source['dir'].split('/')[-1]})")
        print(f"发现 {len(all_dirs)} 个文章文件夹")
        print(f"{'='*50}")
        
        count = 0
        source_ok = 0
        source_skipped = {}
        
        for article in all_dirs:
            count += 1
            result, status = process_article(article, source)
            
            if status == "ok":
                all_results.append(result)
                source_ok += 1
                if count % 50 == 0:
                    print(f"  [{count}/{len(all_dirs)}] 已处理 {source_ok} 篇...")
            else:
                source_skipped[status] = source_skipped.get(status, 0) + 1
        
        grand_total += count
        grand_ok += source_ok
        for k, v in source_skipped.items():
            grand_skipped[k] = grand_skipped.get(k, 0) + v
        
        print(f"  完成: {source_ok}/{count} 篇，跳过: {source_skipped}")
    
    print(f"\n{'='*50}")
    print(f"全部完成！")
    print(f"总文件夹: {grand_total}")
    print(f"成功转换: {grand_ok} 篇")
    print(f"跳过: {grand_skipped}")
    print(f"图片总数: {sum(r['images'] for r in all_results)}")
    
    # 按来源统计
    from collections import Counter
    source_counts = Counter(r["source"] for r in all_results)
    for s, c in source_counts.items():
        print(f"  {s}: {c} 篇")
    
    # 最新和最早
    all_results.sort(key=lambda x: x['date'], reverse=True)
    print(f"\n最新5篇:")
    for r in all_results[:5]:
        print(f"  {r['date']} | [{r['source']}] {r['title'][:30]} | {r['images']}图")
    print(f"\n最早5篇:")
    for r in all_results[-5:]:
        print(f"  {r['date']} | [{r['source']}] {r['title'][:30]} | {r['images']}图")


if __name__ == "__main__":
    main()
