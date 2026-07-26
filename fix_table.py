#!/usr/bin/env python3
"""修复比特币100万到1000万文章的表格排版 - v2"""
import re

path = "content/posts/2026-07-24-比特币-100万-到-1000万-的-梦.md"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 先把表格区域识别出来
# 实际格式：每行之间有空行
# 月份\n\n月度收益率\n\n月末资产 (万元)\n\n11 月\n\n53.48%\n\n153.48\n\n12 月\n\n38.89%\n\n213.17

# 用正则找到所有表格块
# 表格头模式
header_pattern = r'月份\s*\n\s*月度收益率\s*\n\s*月末资产 \(万元\)\s*\n'
# 数据行模式：x 月 \n xx.xx% \n xx.xx（中间可能有空行）

def convert_table(match):
    """转换一个表格块"""
    # 获取表格头之后的内容
    after_header = match.group(1)
    # 把连续空行压缩为单个
    after_header = re.sub(r'\n{3,}', '\n\n', after_header)
    # 分割成非空行
    lines = [l.strip() for l in after_header.split('\n') if l.strip()]
    
    # 三行一组收集数据
    rows = []
    i = 0
    while i + 2 < len(lines):
        v1 = lines[i]
        v2 = lines[i+1]
        v3 = lines[i+2]
        # 检查是否是数据行
        if re.match(r'^\d+\s*月$', v1) and re.match(r'^-?\d+\.\d+%$', v2) and re.match(r'^-?\d+\.\d+$', v3):
            rows.append((v1, v2, v3))
            i += 3
        else:
            break
    
    if not rows:
        return match.group(0)
    
    # 生成 markdown 表格
    result = '| 月份 | 月度收益率 | 月末资产 (万元) |\n| :---: | :---: | :---: |\n'
    for v1, v2, v3 in rows:
        result += f'| {v1} | {v2} | {v3} |\n'
    
    # 剩余内容
    remaining = '\n'.join(lines[i:])
    if remaining:
        result += '\n' + remaining
    
    return result

# 匹配表格头 + 后续内容（直到下一个非表格内容）
# 用 lookahead 找到表格结束：下一个段落开头不是数据行
pattern = r'月份\s*\n\s*月度收益率\s*\n\s*月末资产 \(万元\)\s*\n((?:.*?\n)*?)(?=\n*[^\d\s]*月|[^\n]*\n\n[a-zA-Z\u4e00-\u9fff])'

# 更简单的方法：直接找到所有表格头，然后手动解析
def find_and_convert_tables(text):
    result = []
    pos = 0
    header_re = re.compile(r'月份\s*\n\s*月度收益率\s*\n\s*月末资产 \(万元\)\s*\n')
    
    for m in header_re.finditer(text):
        # 添加表格头之前的内容
        result.append(text[pos:m.start()])
        
        # 从表格头之后开始解析
        after = text[m.end():]
        lines = []
        # 逐字符读取，按行分割
        raw_lines = after.split('\n')
        
        idx = 0
        rows = []
        while idx < len(raw_lines):
            line = raw_lines[idx].strip()
            if not line:
                idx += 1
                continue
            # 尝试读取3个非空行作为一行数据
            vals = []
            while idx < len(raw_lines) and len(vals) < 3:
                l = raw_lines[idx].strip()
                if l:
                    vals.append(l)
                idx += 1
            
            if len(vals) == 3:
                v1, v2, v3 = vals
                if re.match(r'^\d+\s*月$', v1) and re.match(r'^-?\d+\.\d+%$', v2) and re.match(r'^-?\d+\.\d+$', v3):
                    rows.append((v1, v2, v3))
                    continue
                else:
                    # 不是数据行，回退
                    break
            else:
                break
        
        if rows:
            table = '| 月份 | 月度收益率 | 月末资产 (万元) |\n| :---: | :---: | :---: |\n'
            for v1, v2, v3 in rows:
                table += f'| {v1} | {v2} | {v3} |\n'
            result.append(table)
            # 跳过已解析的内容
            # 找到 raw_lines 中已消费的位置
            consumed = 0
            count = 0
            for ci, line in enumerate(raw_lines):
                if count >= len(rows) * 3:
                    consumed = ci
                    break
                if line.strip():
                    count += 1
            else:
                consumed = len(raw_lines)
            
            pos = m.end() + sum(len(l) + 1 for l in raw_lines[:consumed])
        else:
            result.append(text[m.start():m.end()])
            pos = m.end()
    
    result.append(text[pos:])
    return ''.join(result)

content = find_and_convert_tables(content)

# 年份段落加粗
year_bolds = [
    '但是到了2018年：',
    '接下来到了2019年：',
    '然后来到了2020年：',
    '于是，来到了2021年：',
    '于是又来到了2022年：',
    '带着纠结与不甘，带着无奈与释然，走入2023年：',
    '2024年：',
    '2025年：',
    '2026年：',
]
for y in year_bolds:
    content = content.replace(y, f'**{y}**')

# "（本文完）"后加分隔线
content = content.replace('（本文完）\n', '（本文完）\n\n---\n')

# 关键金句做成引用块
golden_lines = [
    '价格，考验的是耐心。',
    '波动，考验的是人性。',
    '时间，筛选的是信念。',
]
for line in golden_lines:
    content = content.replace(f'\n{line}\n', f'\n> **{line}**\n')

# 三组腰斩数据做成引用
content = content.replace(
    '213万跌到59万；\n\n952万跌到257万；\n\n1800万跌到910万。',
    '> 213万跌到59万；\n> 952万跌到257万；\n> 1800万跌到910万。'
)

# 情绪词组做成引用
content = content.replace(
    '兴奋。贪婪。恐惧。怀疑。绝望。希望。狂喜。麻木。平静。',
    '> 兴奋。贪婪。恐惧。怀疑。绝望。希望。狂喜。麻木。平静。'
)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Done! v2 转换完成")
