#!/usr/bin/env python3
"""
第二轮：用文件名slug也做匹配，处理第一轮未匹配的公众号链接
"""

import os
import re

POSTS_DIR = "/Users/xw/Downloads/公众号数据/blog-converter/content/posts"

def normalize(text):
    """标准化用于匹配"""
    t = re.sub(r'[\s\u3000\x00-\x1f]', '', text)
    t = re.sub(r'[，。！？、；：""''（）【】《》〈〉「」『』·…—\-_\[\](){}"\'.,!?:;|/\\@#$%^&*+=~`<>]', '', t)
    return t.lower()

def build_index():
    """构建多种匹配索引"""
    # normalized_title -> permalink
    title_map = {}
    # normalized_filename_keywords -> permalink
    filename_map = {}
    # 所有标题的 normalized 列表
    all_titles = []
    
    for filename in os.listdir(POSTS_DIR):
        if not filename.endswith('.md'):
            continue
        
        filepath = os.path.join(POSTS_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        title_match = re.search(r'^title:\s*"(.+?)"', content, re.MULTILINE)
        if not title_match:
            continue
        title = title_match.group(1)
        
        slug = filename[:-3]
        permalink = f"/posts/{slug}/"
        
        norm_title = normalize(title)
        title_map[norm_title] = permalink
        all_titles.append((norm_title, permalink, title))
        
        # 从文件名提取关键词
        # 格式: 2025-01-01-关键词-更多关键词
        parts = slug.split('-', 3)
        if len(parts) >= 4:
            keywords = parts[3]
            norm_kw = normalize(keywords)
            if norm_kw:
                filename_map[norm_kw] = permalink
    
    return title_map, filename_map, all_titles

def replace_remaining(filepath, title_map, filename_map, all_titles):
    """第二轮替换"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    replaced = 0
    still_unmatched = 0
    
    pattern = r'\[([^\]]+)\]\(http[s]?://mp\.weixin\.qq\.com/s\?[^)]+\)'
    
    def replacer(match):
        nonlocal replaced, still_unmatched
        link_text = match.group(1)
        norm = normalize(link_text)
        
        # 1. 精确匹配
        if norm in title_map:
            replaced += 1
            return f'[{link_text}]({title_map[norm]})'
        
        # 2. 模糊包含匹配
        for indexed_title, permalink, _ in all_titles:
            if norm and indexed_title and (norm in indexed_title or indexed_title in norm):
                replaced += 1
                return f'[{link_text}]({permalink})'
        
        # 3. 尝试关键词匹配 - 取链接文本的关键部分
        # 比如 "1.1 比特币继续面对不确定性" -> 匹配包含 "比特币继续面对不确定性" 的文章
        # 去掉开头的编号
        stripped = re.sub(r'^[\d.]+\s*', '', link_text)
        stripped_norm = normalize(stripped)
        if stripped_norm and stripped_norm != norm:
            if stripped_norm in title_map:
                replaced += 1
                return f'[{link_text}]({title_map[stripped_norm]})'
            for indexed_title, permalink, _ in all_titles:
                if stripped_norm and indexed_title and (stripped_norm in indexed_title or indexed_title in stripped_norm):
                    replaced += 1
                    return f'[{link_text}]({permalink})'
        
        # 4. 尝试取核心词匹配
        # 去掉编号和常见前缀后，取最长的几个字做子串匹配
        core = stripped_norm
        if len(core) > 4:
            for indexed_title, permalink, orig_title in all_titles:
                if core and indexed_title and core in indexed_title:
                    replaced += 1
                    return f'[{link_text}]({permalink})'
        
        still_unmatched += 1
        return match.group(0)
    
    content = re.sub(pattern, replacer, content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return replaced, still_unmatched

def main():
    print("构建索引...")
    title_map, filename_map, all_titles = build_index()
    print(f"索引: {len(title_map)} 标题, {len(filename_map)} 文件名关键词\n")
    
    total_replaced = 0
    total_unmatched = 0
    files_changed = 0
    
    for filename in sorted(os.listdir(POSTS_DIR)):
        if not filename.endswith('.md'):
            continue
        
        filepath = os.path.join(POSTS_DIR, filename)
        replaced, unmatched = replace_remaining(filepath, title_map, filename_map, all_titles)
        
        if replaced > 0:
            files_changed += 1
            total_replaced += replaced
        total_unmatched += unmatched
    
    print(f"{'='*50}")
    print(f"第二轮完成！")
    print(f"修改文件: {files_changed}")
    print(f"替换链接: {total_replaced}")
    print(f"仍未匹配: {total_unmatched}")

if __name__ == "__main__":
    main()
