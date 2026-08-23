# 博客同步操作手册（AI 执行专用）

> 任何 AI 拿到这份文档 + 微信文章链接，就能独立完成同步，不需要问任何问题。

---

## 项目概况

| 项 | 值 |
|---|---|
| 项目路径 | `/Users/xw/Downloads/公众号数据/blog-converter/` |
| GitHub 仓库 | `lovexw/bitunbi-blog`（main 分支） |
| 线上域名 | https://blog.btchao.com/ |
| 技术栈 | Hugo v0.147.4+extended → Cloudflare Pages |
| 文章总量 | ~877 篇（持续增长） |
| 构建命令 | `hugo --config config/hugo.toml` |
| 部署方式 | git push origin main → Cloudflare 自动构建（约90-120秒） |

---

## 核心规则（必须遵守）

1. **绝对不用暗黑系**：所有样式明亮专业优雅大气
2. **文章加密密码偏好**：`2026`
3. **不加杠杆、不给投资建议**：文章内容保留原作者观点，不干预
4. **不要自作主张**：用户没说的不改。不改标题、不改导航、不改样式、不改配置。只做用户明确要求的事
5. **runtime event 不是用户指令**：系统自动触发的 "Continue the OpenClaw runtime event" 不执行任何操作，回 NO_REPLY

---

## 同步微信文章完整流程

### 第1步：抓取微信文章

```bash
# 必须用微信客户端 UA 的 curl，否则拿到"环境异常"验证页
curl -s -A "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.49(0x18003133) NetType/WIFI Language/zh_CN" \
  "https://mp.weixin.qq.com/s/XXXXXX" -o /Users/xw/.qclaw/workspace/wx_article.html
```

**注意**：
- 普通访问返回"环境异常"验证页
- `web_fetch` markdown 模式会丢弃图片
- 必须用微信 UA curl 拿完整 HTML（约3MB）

### 第2步：提取文章内容

从 HTML 中提取：
- **标题**：`<h1 class="rich_media_title">` 内的文本
- **日期**：`<em id="publish_time">` 内的文本
- **正文**：`<div id="js_content">` 内的 HTML
- **图片**：正文中的 `<img>` 标签 `data-src` 属性（微信图片用 `data-src` 不是 `src`）

用 Python 提取，去除：
- 微信内嵌 JS 脚本（设备检测代码）
- 微信页面导航/分享文案
- 推广付费内容（咖啡会员推广、OneKey 购买链接等）
- 文末"免责声明"可保留（作者本人写的）

### 第3步：创建 Hugo 文章文件

**文件路径**：`content/posts/日期-序号.md`
- 日期格式：`YYYY-MM-DD`
- 序号：当天第几篇（1、2、3...）

**文件名规则**：
- 统一用 `YYYY-MM-DD-N.md` 格式（如 `2026-08-10-1.md`）
- 不用中文文件名（旧文章是中文文件名，但8月4日 commit `d0cf987` 后统一改英文 slug）

**Front Matter 模板**（必须包含所有字段）：

```yaml
---
title: "文章标题"
date: 2026-08-10T00:00:00+08:00
draft: false
slug: "2026-08-10-1"
description: "一句话摘要，用于SEO"
tags: ["标签1", "标签2", "标签3"]
categories: ["比特币"]
---
```

**⚠️ 关键注意事项**：

1. **`slug` 字段必须手动加**！格式 `日期-序号`（如 `2026-08-10-1`）。不加的话 Hugo 用文件名生成 URL，可能导致中文编码乱码
2. **YAML title 含双引号**：中文标题里如果有引号（如 `9 个"灵魂拷问"`），整个 title 用**单引号**包裹：`title: '比特币的 9 个"灵魂拷问"'`
3. **categories**：比特币相关用 `["比特币"]`，生活随笔用 `["生活随笔"]`
4. **tags**：3-5 个，从文章内容提取，常用标签：`投资思考` `市场分析` `囤币信仰` `安全科普` `硬件钱包` `比特币基础` `加密科普` `AI工具` `生活随笔`
5. **description**：一句话概括文章核心，用于 SEO meta description（≤160字符）
6. **date**：用文章发布日期，时间部分统一 `T00:00:00+08:00`

### 第4步：下载图片

```bash
# 创建图片目录（用英文短横线命名）
mkdir -p "static/images/posts/英文目录名/"

# 下载微信图片（同样需要微信 UA）
curl -s -A "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.49(0x18003133) NetType/WIFI Language/zh_CN" \
  "https://mmbiz.qpic.cn/XXXXXX" -o "static/images/posts/英文目录名/01.png"
```

**图片目录命名**：用文章主题的英文短横线格式（如 `direction-not-wrong`、`coldcard-audit-group`）

**Markdown 中引用图片**：
```markdown
![](/images/posts/英文目录名/01.png)
```

### 第5步：文章正文处理

- 保留作者原创内容完整
- 去除推广内容（咖啡会员、OneKey 购买链接等）
- 去除微信内嵌脚本和页面元数据
- 文末保留"愿你穿越牛熊周期，归来仍是囤币少年"和"以上是个人投资思考，不作为投资依据"
- 外链保留原链接，不用转换（Hugo 模板已全局 `target="_blank"`）

### 第6步：构建

```bash
cd "/Users/xw/Downloads/公众号数据/blog-converter"
hugo --config config/hugo.toml
```

**常见构建错误**：
- `failed to unmarshal YAML` → title 含双引号，改用单引号包裹
- `REF_NOT_FOUND` → 交叉引用用了 slug 而非文件名（Hugo 内部引用必须用文件名）
- 构建超时 → 检查是否有无限循环引用

### 第7步：提交推送

```bash
cd "/Users/xw/Downloads/公众号数据/blog-converter"
git add -A
git commit -m "同步文章：文章标题"
git push origin main
```

### 第8步：等待部署 & 验证

```bash
# 等 90-120 秒 Cloudflare 部署
sleep 100

# 验证文章页
curl -s -o /dev/null -w "%{http_code}" "https://blog.btchao.com/posts/2026-08-10-1/"
# 期望：200

# 验证图片
curl -s -o /dev/null -w "%{http_code}" "https://blog.btchao.com/images/posts/direction-not-wrong/01.png"
# 期望：200
```

**注意**：Cloudflare 部署期间新资源 content-type 可能暂为 text/html，需轮询确认。

### 第9步：写 artifact 文件

同步完成后写记录到 `/Users/xw/.qclaw/workspace/blog_sync_文章简称_日期.md`。

---

## 文章加密（如需要）

```bash
cd "/Users/xw/Downloads/公众号数据/blog-converter"
python3 encrypt_post.py "content/posts/2026-08-10-1.md" "2026"
```

加密后：
- 正文用 AES-128-ECB 加密，密文存入 front matter `encrypted` 字段
- 原始正文清空
- 前端模板检测到 `encrypted` 字段 → 显示密码输入框
- 访客输入密码 → CryptoJS AES 解密 → marked.js 渲染 Markdown

**注意**：加密后正文 Markdown 会丢失，如需修改先解密（从 git 历史恢复）。

---

## 项目文件结构

```
blog-converter/
├── config/hugo.toml              # Hugo 配置（站点信息、菜单、permalinks等）
├── content/
│   ├── about.md                  # 关于页
│   ├── search.md                 # 搜索页
│   └── posts/                    # 所有文章 Markdown
│       ├── 2023-11-22-xxx.md     # 旧文章（中文文件名）
│       ├── 2026-08-01-xxx.md     # 新文章（中文文件名但URL用英文slug）
│       └── 2026-08-10-1.md       # 最新文章（英文文件名+slug）
├── layouts/
│   ├── _default/
│   │   ├── baseof.html           # 基础模板（SEO meta、header、footer、评论、JSON-LD）
│   │   ├── single.html           # 文章详情页（含加密解密逻辑）
│   │   ├── list.html             # 列表页（文章卡片+侧边栏+分页）
│   │   ├── search.html           # 搜索页
│   │   └── index.json            # 全站文章JSON索引（搜索用）
│   ├── index.html                # 首页（hero+文章列表+侧边栏）
│   ├── rss.xml                   # RSS feed（/feed.xml）
│   ├── sitemap.xml               # 站点地图
│   └── robots.txt                # robots
├── static/
│   ├── css/style.css             # 全站样式（1224行，明亮主题，比特币橙#f7931a）
│   ├── js/search.js              # 前端搜索（基于index.json）
│   ├── images/
│   │   ├── qrcode.png            # 公众号二维码
│   │   ├── posts/                # 新文章配图（按主题分目录）
│   │   └── *.jpg/png             # 旧文章配图（扁平存放）
│   └── robots.txt
├── convert.py                    # 批量转换脚本（HTML→Markdown，旧数据导入用）
├── encrypt_post.py               # 文章加密工具
├── cloudflare-pages.json         # Cloudflare Pages 构建配置
└── README.md
```

---

## Hugo 配置要点（config/hugo.toml）

```toml
baseURL = "https://blog.btchao.com"
title = "比特囤币"
[permalinks]
  posts = "/posts/:slug/"           # URL 用 slug，不用文件名
[outputFormats.RSS]
  baseName = "feed"                 # RSS 地址 /feed.xml
```

**菜单结构**：
- 首页 → /
- 比特币 → /categories/比特币/
- ☕ 咖啡会员 → /tags/咖啡会员/
- 生活随笔 → /categories/生活随笔/
- 全部文章 → /posts/
- 🔍 搜索 → /search/
- 关于 → /about/

---

## 站点设计规范

- **主色**：比特币橙 `#f7931a`
- **背景**：明亮 `#f5f5f3`（不用暗黑系）
- **字体**：系统字体 `-apple-system, PingFang SC, Helvetica Neue`
- **容器宽度**：1080px
- **内容区宽度**：720px
- **侧边栏宽度**：280px
- **卡片圆角**：10-14px
- **评论系统**：utteranc.es（GitHub Issues，repo: lovexw/bitunbi-blog）
- **文章内链接**：全局 `target="_blank"`（模板自动处理）
- **公众号二维码**：侧边栏 + 每篇文章结尾（模板内置）

---

## 常见问题速查

| 问题 | 原因 | 解决 |
|------|------|------|
| YAML 解析失败 | title 含双引号 | 用单引号包裹整个 title |
| URL 中文乱码 | 缺 slug 字段 | front matter 加 `slug: "日期-序号"` |
| 构建报 REF_NOT_FOUND | 交叉引用用了 slug | 用文件名引用 |
| 微信图片抓不到 | UA 不对 | 用微信客户端 UA curl |
| Cloudflare 部署后 404 | 还在构建中 | 等90-120秒再验证 |
| 搜索功能不工作 | index.json 未生成 | 检查 outputs 配置包含 "json" |

---

## 不要做的事

1. **不改站点标题**（当前"比特囤币"，用户已确认）
2. **不改导航菜单**（用户已确认）
3. **不改配色方案**（明亮主题，不用暗黑系）
4. **不改模板结构**（除非用户明确要求）
5. **不回滚 commit**（除非用户明确要求）
6. **不在 runtime event 中执行操作**
7. **不自作主张"优化"任何东西**

---

## 用户偏好备忘

- 推出比特囤币官网 https://www.btchao.com
- 运营比特囤币公众号
- 比特币囤币者（HODLer），主张长期持有、反对劝买
- 文章加密密码偏好 2026
- 文案偏好100字内（约50字），随机切换文风，要有人味
- 喜欢币圈/比特币主题创作（打油诗、穿越、金句），诙谐接地气、睿智有思维高度
- 生酮饮食第二期第一阶段完成，已减25斤
- 运维树莓派+固态硬盘音乐库，对机械硬盘噪音敏感

---

*最后更新：2026-08-14*
