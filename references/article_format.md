# 公众号文章格式指南

## 文章结构

```python
article = {
    # 必填字段
    "title": "文章标题",           # <=32字符
    "content": "<p>正文HTML</p>",  # <2万字符, <1MB
    "thumb_media_id": "封面ID",    # 图文消息必填
    
    # 可选字段
    "author": "作者名",            # <=16字符
    "digest": "摘要",              # <=128字符，单图文有效
    "content_source_url": "https://原文链接",
    "need_open_comment": 0,        # 0=关闭评论, 1=开启
    "only_fans_can_comment": 0,    # 0=所有人, 1=仅粉丝
    
    # 封面裁剪（可选）
    "pic_crop_235_1": "X1_Y1_X2_Y2",  # 2.35:1 比例
    "pic_crop_1_1": "X1_Y1_X2_Y2",    # 1:1 比例
    
    # 文章类型（可选）
    "article_type": "news"  # news=图文, newspic=图片消息
}
```

## 正文 HTML 规范

### 支持的标签

```html
<!-- 段落 -->
<p>段落文本</p>
<section>区块内容</section>

<!-- 文本格式 -->
<strong>加粗</strong>
<em>斜体</em>
<span style="color: #ff0000;">红色文字</span>

<!-- 图片（URL 必须来自 uploadimg 接口） -->
<img src="https://mmbiz.qpic.cn/xxx" />

<!-- 链接 -->
<a href="https://example.com">链接文字</a>

<!-- 列表 -->
<ul><li>无序列表项</li></ul>
<ol><li>有序列表项</li></ol>

<!-- 引用 -->
<blockquote>引用内容</blockquote>

<!-- 分割线 -->
<hr />
```

### 不支持的内容

- JavaScript 代码（会被移除）
- 外部图片链接（会被过滤）
- iframe 嵌入
- 表单元素

## 图片处理流程

```python
from scripts.material_manager import MaterialManager
from scripts.wechat_client import WeChatClient

client = WeChatClient()
mm = MaterialManager(client)

# 1. 上传封面图（永久素材）
cover_id = mm.upload_permanent("image", "cover.jpg")

# 2. 上传正文图片（返回URL）
img_url = mm.upload_article_image("content.jpg")

# 3. 在正文中使用
content = f'''
<p>这是一段文字</p>
<img src="{img_url}" />
<p>图片后的文字</p>
'''
```

## 封面裁剪坐标

坐标系：左上角(0,0)，右下角(1,1)

```python
# 2.35:1 比例裁剪示例
# 取图片中间区域
pic_crop_235_1 = "0.1945_0_1_0.5236"

# 1:1 比例裁剪示例
# 取图片中央正方形
pic_crop_1_1 = "0.166_0_0.833_1"
```

## 图片消息（newspic）

```python
article = {
    "article_type": "newspic",
    "title": "图片消息标题",
    "content": "<p>简短描述</p>",  # 仅支持纯文本
    "image_info": {
        "image_list": [
            {"image_media_id": "永久素材ID1"},
            {"image_media_id": "永久素材ID2"}
        ]
    },
    "cover_info": {
        "crop_percent_list": [{
            "ratio": "1_1",
            "x1": "0.166",
            "y1": "0",
            "x2": "0.833",
            "y2": "1"
        }]
    }
}
```

## 多图文

一个草稿可包含多篇文章：

```python
articles = [
    {"title": "头条", "content": "...", "thumb_media_id": "..."},
    {"title": "次条", "content": "...", "thumb_media_id": "..."},
    {"title": "第三条", "content": "...", "thumb_media_id": "..."}
]

dm.create_draft(articles)
```

注意：
- 只有单图文才显示摘要
- 多图文中每篇文章独立
