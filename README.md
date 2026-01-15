# WeChat MP Skill | 微信公众号技能

适用于 Claude Code 的微信公众号管理技能。帮助公众号创作者通过 AI 进行内容管理和发布流程自动化。

## 功能特性

- **素材管理** - 上传/获取/删除图片、视频、语音等永久和临时素材
- **草稿管理** - 创建/编辑/删除/发布草稿，支持多图文
- **数据统计** - 用户增减、图文阅读、消息发送等数据分析

## 安装

### 方式一：下载并解压（推荐）

1. 从 [Releases](https://github.com/helebest/wechat-mp-skill/releases) 下载 `wechat-mp-skill.zip`
2. 解压到 `~/.claude/skills/wechat-mp-skill/` 目录

### 方式二：克隆仓库

```bash
git clone https://github.com/helebest/wechat-mp-skill.git ~/.claude/skills/wechat-mp-skill
```

### 本地构建

```bash
uv run python build_skill.py
# 输出: dist/wechat-mp-skill-x.x.x.zip
```

## 配置

支持三种配置方式（优先级从高到低）：

### 1. 代码传参

```python
from scripts import WeChatClient
client = WeChatClient(appid="your_appid", appsecret="your_appsecret")
```

### 2. 环境变量

```bash
export WECHAT_APPID="your_appid"
export WECHAT_APPSECRET="your_appsecret"
```

### 3. .env 文件（推荐）

在项目根目录创建 `.env` 文件：

```
WECHAT_APPID=your_appid
WECHAT_APPSECRET=your_appsecret
```

> 获取方式：微信公众平台 → 设置与开发 → 基本配置

## 快速开始

### 发布文章

```python
from scripts import WeChatClient, MaterialManager, DraftManager

client = WeChatClient()
mm = MaterialManager(client)
dm = DraftManager(client)

# 1. 上传封面图
cover_id = mm.upload_permanent("image", "cover.jpg")

# 2. 上传正文图片
img_url = mm.upload_article_image("content.jpg")

# 3. 创建草稿
article = {
    "title": "我的文章",
    "author": "作者",
    "content": f'<p>正文内容</p><img src="{img_url}"/>',
    "thumb_media_id": cover_id
}
draft_id = dm.create_draft([article])

# 4. 发布
publish_id = dm.publish_draft(draft_id)
```

### 数据统计

```python
from scripts import WeChatClient, StatsManager

client = WeChatClient()
sm = StatsManager(client)

# 获取昨日概览
yesterday = sm.get_yesterday_summary()
print(f"新增粉丝: {sum(u['new_user'] for u in yesterday['user'])}")

# 获取本周数据
week = sm.get_week_summary()
```

### 一键提交 HTML 草稿

```python
from scripts import submit_html_draft

# 自动解析 HTML 中的图片、上传、替换 URL、创建草稿
media_id = submit_html_draft(
    html_path='article.preview.html',
    cover_path='cover.png',
    author='作者名',
    digest='文章摘要'
)
print(f'草稿创建成功: {media_id}')
```

## 模块说明

| 模块 | 文件 | 功能 |
|------|------|------|
| API 客户端 | `scripts/wechat_client.py` | 认证、请求、Token 管理 |
| 素材管理 | `scripts/material_manager.py` | 永久/临时素材操作 |
| 草稿管理 | `scripts/draft_manager.py` | 草稿 CRUD、发布 |
| 数据统计 | `scripts/stats_manager.py` | 各类数据查询 |
| HTML 提交 | `scripts/html_submitter.py` | 高级接口，自动处理图片上传 |

## API 文档

详细 API 参考请查看 `references/` 目录：

- [api_reference.md](references/api_reference.md) - API 完整参考
- [article_format.md](references/article_format.md) - 文章格式指南
- [stats_reference.md](references/stats_reference.md) - 数据统计参考
- [error_codes.md](references/error_codes.md) - 错误码速查

## 注意事项

- 需要在微信公众平台配置服务器 IP 白名单
- access_token 有效期 7200 秒，客户端自动管理
- 永久素材有数量上限（图片 10 万，语音/视频各 1000）
- 图文正文图片必须使用 `upload_article_image()` 上传
- 数据统计只能查询昨天及之前的数据
- **发布和数据统计功能需要公众号完成微信认证**（素材管理、草稿管理无此限制）

## 开发

### 环境设置

```bash
# 安装所有依赖（包括开发依赖）
uv sync --all-extras
```

### 运行测试

```bash
# 单元测试
uv run pytest tests/ -v -m unit

# 端到端测试（需要配置 .env）
uv run pytest tests/test_e2e.py -v -m e2e

# 测试覆盖率
uv run pytest tests/ --cov=scripts --cov-report=html
```

### 构建发布

```bash
# 构建 .skill 包
uv run python build_skill.py

# 指定版本
uv run python build_skill.py --version 1.0.0
```

## 开发计划

- [x] 素材管理
- [x] 草稿管理
- [x] 数据统计
- [ ] 用户管理（标签、粉丝）
- [ ] 自定义菜单
- [ ] 留言管理
- [ ] 客服消息

## 许可证

MIT License
