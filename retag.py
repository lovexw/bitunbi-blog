#!/usr/bin/env python3
"""
为820篇文章重新生成标签 - 基于20个标签分类体系
通过关键词匹配自动分类
"""

import os
import re
import json

POSTS_DIR = "/Users/xw/Downloads/公众号数据/blog-converter/content/posts"

# 20个标签分类体系 + 关键词匹配规则
# 每篇文章匹配1-3个标签
TAG_RULES = [
    ("比特币基础", ["白皮书", "区块链基础", "什么是比特币", "了解比特币", "0基础", "0概念", "入门", "学习", "科普", "基础知识", "新手"]),
    ("投资思考", ["投资", "定投", "仓位", "资产配置", "买入", "卖出", "策略", "止盈", "止损", "加仓", "减仓", "建议", "思考", "实验"]),
    ("市场分析", ["牛熊", "牛市", "熊市", "涨跌", "价格", "走势", "分析", "新高", "暴跌", "崩盘", "回调", "反弹", "横盘", "波动", "十字路口", "关键时刻"]),
    ("ETF与机构", ["ETF", "机构", "灰度", "贝莱德", "基金", "主权基金", "上市公司", "MicroStrategy", "梅萨", "萨尔瓦多", "美国", "法案", "GENIUS"]),
    ("囤币信仰", ["囤币", "信仰", "长期", "持有", "HODL", "穿越牛熊", "信仰者", "坚守", "不动", "时间的"]),
    ("私钥安全", ["私钥", "钱包", "助记词", "签名", "地址", "OneKey", "硬件钱包", "冷钱包", "安全", "防盗", "骗局", "黑客", "破解", "量子"]),
    ("链上数据", ["链上", "地址", "区块", "算力", "难度", "挖矿", "矿工", "矿池", "哈希", "广播", "确认", " GAS"]),
    ("宏观金融", ["美联储", "利率", "通胀", "CPI", "经济", "货币", "美元", "稳定币", "USDT", "USDC", "监管", "政策", "合规"]),
    ("AI与技术", ["AI", "GPT", "人工智能", "编程", "代码", "大模型", "Gemini", "云雀", "扣子", "Claude", "ChatGPT", "Copilot", "自动"]),
    ("数码折腾", ["数码", "苹果", "手机", "电脑", "耳机", "键盘", "鼠标", "输入法", "双拼", "硬件", "设备", "充电", "MacBook", "iPhone", "AirPods", "树莓派", "服务器", "NAS"]),
    ("生活随笔", ["生活", "随笔", "闲聊", "碎碎念", "日常", "感悟", "人生", "心态", "情绪", "性格", "简单", "欲望", "断舍离", "讨好", "人生游戏"]),
    ("旅行游记", ["菲律宾", "旅行", "游记", "攻略", "北京", "乌鲁木齐", "长城", "南方", "出门", "远行", "台湾", "旅游", "游玩", "慕田峪", "小镇"]),
    ("健康养生", ["健康", "睡眠", "牙", "鼻炎", "过敏", "听力", "身体", "医院", "医保", "肠胃", "吃", "喝", "运动", "养生", "失眠"]),
    ("读书思考", ["天道", "读", "书", "白皮书", "技术百科", "幸存者", "悲观", "乐观", "哲学", "认知", "反思", "觉醒", "顿悟"]),
    ("写作运营", ["写作", "公众号", "运营", "粉丝", "精神股东", "汇报", "本周", "近期", "周报", "总结", "回顾", "年度", "写作计划", "千人", "爆款"]),
    ("自由职业", ["不上班", "自由职业", "远程", "数字游民", "独立", "自由", "工作", "辞职", "上班", "打工", "赚钱"]),
    ("折腾日记", ["折腾", "部署", "搭建", "记录", "日记", "PT", "考核", "资费", "改", "修理", "维权", "快递", "ToDesk", "TeamViewer", "WiFi"]),
    ("历史故事", ["历史", "2011", "2017", "2013", "故事", "中本聪", "哈尔·芬尼", "回忆", "曾经", "当年", "过去", "那一年"]),
    ("加密科普", ["加密", "哈希", "密钥", "密码", "安全", "签名", "验证", "原理", "技术", "机制", "共识", "去中心化"]),
    ("人生感悟", ["人生", "选择", "命运", "活着", "生命", "死亡", "送别", "奶奶", "老", "成长", "明白", "道理", "温柔", "深渊", "勇敢", "坚持"]),
]

def classify_tags(title):
    """根据标题匹配标签，返回1-3个标签"""
    matched = []
    for tag, keywords in TAG_RULES:
        for kw in keywords:
            if kw.lower() in title.lower():
                if tag not in matched:
                    matched.append(tag)
                break
    if not matched:
        # 默认标签
        matched = ["生活随笔"]
    # 最多3个标签
    return matched[:3]


def main():
    stats = {}
    total = 0
    changed = 0
    
    for filename in sorted(os.listdir(POSTS_DIR)):
        if not filename.endswith(".md"):
            continue
        
        filepath = os.path.join(POSTS_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取标题
        title_match = re.search(r'^title:\s*"(.+?)"', content, re.MULTILINE)
        if not title_match:
            continue
        title = title_match.group(1)
        
        # 提取分类
        cat_match = re.search(r'categories:\s*\["(.+?)"\]', content)
        category = cat_match.group(1) if cat_match else "生活随笔"
        
        # 生成新标签
        new_tags = classify_tags(title)
        
        # 统计
        for t in new_tags:
            stats[t] = stats.get(t, 0) + 1
        total += 1
        
        # 替换 tags 行
        tags_str = ", ".join(f'"{t}"' for t in new_tags)
        new_content = re.sub(
            r'tags:\s*\[.+?\]',
            f'tags: [{tags_str}]',
            content
        )
        
        if new_content != content:
            changed += 1
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
    
    print(f"处理 {total} 篇文章，更新 {changed} 篇")
    print(f"\n标签分布:")
    for tag, count in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"  {tag}: {count} 篇")


if __name__ == "__main__":
    main()
