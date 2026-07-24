#!/usr/bin/env python3
"""
将文章正文中的公众号链接替换为博客内部链接。
策略：
1. 构建 标题 → 内部链接 的映射
2. 遍历所有文章，找到 [标题](http://mp.weixin.qq.com/s?...) 格式的链接
3. 如果标题能匹配到内部文章，替换为 [标题](/posts/slug/)
4. 不能匹配的保留原链接（外部链接）
"""

import os
import re
import unicodedata

POSTS_DIR = "/Users/xw/Downloads/公众号数据/blog-converter/content/posts"

def normalize_title(title):
    """标准化标题用于模糊匹配"""
    # 去掉空格、标点、特殊字符
    t = re.sub(r'[\s\u3000\x00-\x1f]', '', title)
    t = re.sub(r'[，。！？、；：""''（）【】《》〈〉「」『』·…—\-_\[\](){}"\'.,!?:;|/\\@#$%^&*+=~`<>]', '', t)
    return t.lower()

def build_title_index():
    """构建标题 → permalink 映射"""
    index = {}  # normalized_title -> relative permalink
    raw_index = {}  # original_title -> relative permalink
    
    for filename in os.listdir(POSTS_DIR):
        if not filename.endswith('.md'):
            continue
        
        filepath = os.path.join(POSTS_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取标题
        title_match = re.search(r'^title:\s*"(.+?)"', content, re.MULTILINE)
        if not title_match:
            continue
        title = title_match.group(1)
        
        # 从文件名推断 permalink (Hugo 的 slug 格式)
        # 文件名格式: 2025-01-01-title-slug.md
        # permalink: /posts/title-slug/
        slug = filename[:-3]  # 去掉 .md
        permalink = f"/posts/{slug}/"
        
        norm = normalize_title(title)
        index[norm] = permalink
        raw_index[title] = permalink
    
    return index, raw_index

def replace_links(filepath, title_index):
    """替换文件中的公众号链接为内部链接"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    replaced_count = 0
    unmatched_count = 0
    
    # 匹配 [标题](http://mp.weixin.qq.com/s?...) 格式
    # URL 中可能有各种参数，以 #wechat_redirect 结尾
    pattern = r'\[([^\]]+)\]\(http[s]?://mp\.weixin\.qq\.com/s\?[^)]+\)'
    
    def replacer(match):
        nonlocal replaced_count, unmatched_count
        link_text = match.group(1)
        norm = normalize_title(link_text)
        
        if norm in title_index:
            replaced_count += 1
            return f'[{link_text}]({title_index[norm]})'
        else:
            # 尝试模糊匹配 - 检查是否有包含关系
            for indexed_title, permalink in title_index.items():
                # 如果链接文本包含在某个标题中，或标题包含在链接文本中
                if norm and indexed_title and (norm in indexed_title or indexed_title in norm):
                    replaced_count += 1
                    return f'[{link_text}]({permalink})'
            
            unmatched_count += 1
            return match.group(0)  # 保留原链接
    
    content = re.sub(pattern, replacer, content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return replaced_count, unmatched_count

def main():
    print("构建标题索引...")
    title_index, raw_index = build_title_index()
    print(f"索引包含 {len(title_index)} 篇文章\n")
    
    total_replaced = 0
    total_unmatched = 0
    files_changed = 0
    
    for filename in sorted(os.listdir(POSTS_DIR)):
        if not filename.endswith('.md'):
            continue
        
        filepath = os.path.join(POSTS_DIR, filename)
        replaced, unmatched = replace_links(filepath, title_index)
        
        if replaced > 0:
            files_changed += 1
            print(f"  {filename[:50]}: 替换 {replaced} 个链接" + (f", 未匹配 {unmatched}" if unmatched else ""))
        
        total_replaced += replaced
        total_unmatched += unmatched
    
    print(f"\n{'='*50}")
    print(f"完成！")
    print(f"修改文件: {files_changed}")
    print(f"替换链接: {total_replaced}")
    print(f"未匹配(保留原链接): {total_unmatched}")

if __name__ == "__main__":
    main()
