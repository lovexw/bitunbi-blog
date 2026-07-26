#!/usr/bin/env python3
"""
通用表格检测和修复脚本
扫描所有 markdown 文章，检测纯文本表格并转为 markdown 表格格式

检测逻辑：
1. 找到"表头模式"：多列名称行（如：月份 / 月度收益率 / 月末资产）
2. 后面跟着多组数据行
3. 每行之间可能有空行

支持的模式：
- 月份/百分比/数字
- 日期/数字/数字
- 任意3列短文本数据
"""
import os
import re
import glob

POSTS_DIR = "content/posts"

def find_table_headers(text):
    """找到可能的表格头位置"""
    # 常见表头模式
    header_patterns = [
        (r'月份\s*\n\s*月度收益率\s*\n\s*月末资产', 3),  # 已知模式
        (r'月份\s*\n\s*收益率\s*\n\s*资产', 3),
    ]
    results = []
    for pattern, ncols in header_patterns:
        for m in re.finditer(pattern, text):
            results.append((m.start(), m.end(), ncols))
    return results

def parse_table_rows(text, start, ncols):
    """从 start 位置开始解析数据行"""
    # 跳过表头
    pos = start
    # 找到表头结束位置
    lines = text[start:].split('\n')
    
    # 跳过表头行（ncols 行）
    header_count = 0
    idx = 0
    while idx < len(lines) and header_count < ncols:
        if lines[idx].strip():
            header_count += 1
        idx += 1
    
    # 现在解析数据行
    rows = []
    while idx < len(lines):
        vals = []
        while idx < len(lines) and len(vals) < ncols:
            line = lines[idx].strip()
            if line:
                vals.append(line)
            idx += 1
        
        if len(vals) == ncols:
            # 验证是否是数据行
            v1 = vals[0]
            v2 = vals[1] if ncols > 1 else ''
            v3 = vals[2] if ncols > 2 else ''
            
            # 数据行验证：月份+百分比+数字
            if re.match(r'^\d+\s*月$', v1) and re.match(r'^-?\d+\.?\d*%?$', v2) and re.match(r'^-?\d+\.?\d*$', v3):
                rows.append(vals)
            else:
                break
        else:
            break
    
    return rows, idx

def convert_table(text, start, end, ncols, rows):
    """将表格转为 markdown 格式"""
    # 找到表头文本
    header_text = text[start:end]
    header_cols = [h.strip() for h in header_text.split('\n') if h.strip()]
    
    result = ''
    result += '| ' + ' | '.join(header_cols) + ' |\n'
    result += '| ' + ' | '.join([':---:'] * ncols) + ' |\n'
    for row in rows:
        result += '| ' + ' | '.join(row) + ' |\n'
    
    return result

def process_file(filepath):
    """处理单个文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    headers = find_table_headers(content)
    if not headers:
        return False
    
    original = content
    # 从后往前替换，避免位置偏移
    for start, end, ncols in reversed(headers):
        rows, consumed = parse_table_rows(content, start, ncols)
        if rows and len(rows) >= 2:
            table_md = convert_table(content, start, end, ncols, rows)
            # 找到数据行结束位置
            lines = content[start:].split('\n')
            total_consumed = 0
            header_count = 0
            data_count = 0
            for i, line in enumerate(lines):
                if line.strip():
                    if header_count < ncols:
                        header_count += 1
                    else:
                        data_count += 1
                    if data_count >= len(rows) * ncols:
                        total_consumed = sum(len(l) + 1 for l in lines[:i+1])
                        break
            
            end_pos = start + total_consumed
            content = content[:start] + table_md + content[end_pos:]
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    files = glob.glob(os.path.join(POSTS_DIR, "*.md"))
    fixed = 0
    for f in files:
        if process_file(f):
            print(f"Fixed: {os.path.basename(f)}")
            fixed += 1
    print(f"\nTotal fixed: {fixed}")

if __name__ == '__main__':
    main()
