---
name: wechat-mp-skill
description: 微信公众号管理工具集，支持素材管理（上传/获取/删除图片、视频、语音等永久和临时素材）、草稿管理（创建/编辑/删除/发布草稿）和数据统计（用户/图文/消息数据分析）。适用于公众号创作者通过 Claude Code 进行内容管理和发布流程自动化。触发场景：用户提到微信公众号、公众号素材、公众号草稿、发布文章、上传图片到公众号、公众号数据统计等。
---

# WeChat MP Skill | 微信公众号技能

适用于 Claude Code 的微信公众号管理技能，通过微信公众号 API 管理素材和草稿，实现内容管理自动化。

## 前置准备

用户需提供 AppID 和 AppSecret，支持三种方式（优先级从高到低）：

**方式一：环境变量**
```bash
export WECHAT_APPID="your_appid"
export WECHAT_APPSECRET="your_appsecret"
```

**方式二：.env 文件**（推荐）
在项目根目录创建 `.env` 文件：
```
WECHAT_APPID=your_appid
WECHAT_APPSECRET=your_appsecret
```

**方式三：代码传参**
```python
client = WeChatClient(appid="your_appid", appsecret="your_appsecret")
```

获取方式：微信公众平台 → 设置与开发 → 基本配置

## 核心工作流

### 1. 初始化客户端

```python
from scripts.wechat_client import WeChatClient
client = WeChatClient()  # 自动从环境变量读取配置
```

### 2. 素材管理

```python
from scripts.material_manager import MaterialManager
mm = MaterialManager(client)

# 上传永久素材
media_id = mm.upload_permanent("image", "/path/to/image.jpg")

# 上传图文内图片（返回 URL）
url = mm.upload_article_image("/path/to/image.jpg")

# 获取素材列表
materials = mm.list_materials("image", offset=0, count=20)

# 获取素材统计
stats = mm.get_material_count()

# 删除素材
mm.delete_material(media_id)
```

### 3. 草稿管理

```python
from scripts.draft_manager import DraftManager
dm = DraftManager(client)

# 创建草稿
article = {
    "title": "文章标题",
    "author": "作者名",
    "content": "<p>正文内容（支持 HTML）</p>",
    "thumb_media_id": "封面图素材ID",
    "digest": "摘要（可选）",
    "content_source_url": "原文链接（可选）",
    "need_open_comment": 0,
    "only_fans_can_comment": 0
}
media_id = dm.create_draft([article])

# 获取草稿列表
drafts = dm.list_drafts(offset=0, count=20)

# 获取草稿详情
draft = dm.get_draft(media_id)

# 更新草稿
dm.update_draft(media_id, index=0, article=updated_article)

# 删除草稿
dm.delete_draft(media_id)

# 获取草稿总数
count = dm.get_draft_count()

# 发布草稿
publish_id = dm.publish_draft(media_id)

# 查询发布状态
status = dm.get_publish_status(publish_id)
```

### 4. 数据统计

```python
from scripts.stats_manager import StatsManager
sm = StatsManager(client)

# 获取昨日概览（用户+阅读+分享）
summary = sm.get_yesterday_summary()

# 获取最近7天概览
week_data = sm.get_week_summary()

# 用户数据
user_data = sm.get_user_summary("2026-01-01", "2026-01-07")  # 最大7天
cumulate = sm.get_user_cumulate("2026-01-01", "2026-01-07")

# 图文数据
articles = sm.get_article_summary("2026-01-01")  # 单日
total = sm.get_article_total("2026-01-01")
read_hour = sm.get_user_read_hour("2026-01-01")  # 分时阅读
share_data = sm.get_user_share("2026-01-01", "2026-01-07")

# 消息数据
msg_data = sm.get_upstream_msg("2026-01-01", "2026-01-07")
msg_hour = sm.get_upstream_msg_hour("2026-01-01")

# 接口数据
interface = sm.get_interface_summary("2026-01-01", "2026-01-30")
```

### 5. 完整发布流程示例

```python
# 1. 上传封面图
cover_id = mm.upload_permanent("image", "cover.jpg")

# 2. 上传正文图片
img_url = mm.upload_article_image("content_image.jpg")

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

## 脚本说明

| 脚本 | 用途 |
|------|------|
| `scripts/wechat_client.py` | API 客户端，处理认证和请求 |
| `scripts/material_manager.py` | 素材管理（永久/临时） |
| `scripts/draft_manager.py` | 草稿管理与发布 |
| `scripts/stats_manager.py` | 数据统计（用户/图文/消息） |

## API 限制

- 永久素材上限：图片 100,000 / 语音 1,000 / 视频 1,000
- 图片大小：10MB / 语音：2MB / 视频：10MB
- 草稿图片：最多 20 张
- access_token 有效期：7200 秒（客户端自动管理）

## 权限要求

| 功能 | 未认证公众号 | 已认证公众号 |
|------|-------------|-------------|
| 素材管理（上传/获取/删除） | ✅ | ✅ |
| 草稿管理（创建/编辑/删除/列表） | ✅ | ✅ |
| 发布草稿 | ❌ | ✅ |
| 查询发布状态 | ❌ | ✅ |
| 已发布文章管理 | ❌ | ✅ |
| 数据统计 | ❌ | ✅ |

> **注意**：发布功能（`freepublish/*`）和数据统计功能（`datacube/*`）需要公众号完成微信认证后才能使用。未认证公众号只能管理素材和草稿，无法通过 API 发布文章。认证入口：微信公众平台 → 设置与开发 → 公众号设置 → 微信认证。

## 详细参考

- API 详情：见 `references/api_reference.md`
- 文章格式：见 `references/article_format.md`
- 数据统计：见 `references/stats_reference.md`
- 错误码：见 `references/error_codes.md`

## 扩展模块（后续版本）

预留接口支持：
- 用户管理（标签、粉丝列表）
- 自定义菜单
- 消息管理
- 留言管理
- 客服消息
