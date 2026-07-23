# 比特囤币博客

小吴的比特币世界观 — 数据驱动的长期主义博客。

基于 [Hugo](https://gohugo.io/) 构建，部署于 [Cloudflare Pages](https://pages.cloudflare.com/)。

## 本地开发

```bash
# 安装 Hugo (macOS)
brew install hugo

# 克隆仓库
git clone https://github.com/lovexw/bitunbi-blog.git
cd bitunbi-blog

# 启动开发服务器
hugo server --config config/hugo.toml

# 访问 http://localhost:1313
```

## 项目结构

```
├── config/hugo.toml      # Hugo 配置
├── content/posts/        # 文章 Markdown
├── static/images/        # 文章图片
├── static/css/           # 样式文件
├── layouts/              # Hugo 模板
│   ├── _default/         # 基础模板
│   ├── index.html        # 首页
│   └── partials/         # 组件
├── public/               # 构建输出 (gitignore)
└── cloudflare-pages.json # Cloudflare Pages 配置
```

## 部署

推送到 GitHub `main` 分支后，Cloudflare Pages 自动构建部署。

## 声明

本站内容仅为个人投资思考，不构成任何投资建议。比特币投资具有高波动性，请理性评估自身风险承受能力。

愿你穿越牛熊周期，归来仍是囤币少年。
