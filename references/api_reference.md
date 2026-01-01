# 微信公众号 API 参考

官方文档：https://developers.weixin.qq.com/doc/subscription/api/

## 基础接口

### 获取 Access Token

```
GET https://api.weixin.qq.com/cgi-bin/token
  ?grant_type=client_credential
  &appid=APPID
  &secret=APPSECRET
```

响应：
```json
{
  "access_token": "ACCESS_TOKEN",
  "expires_in": 7200
}
```

## 素材管理

### 上传永久素材

```
POST https://api.weixin.qq.com/cgi-bin/material/add_material
  ?access_token=ACCESS_TOKEN
  &type=TYPE

Content-Type: multipart/form-data
media: (binary)
```

类型：image / voice / video / thumb

### 上传图文内图片

```
POST https://api.weixin.qq.com/cgi-bin/media/uploadimg
  ?access_token=ACCESS_TOKEN

Content-Type: multipart/form-data
media: (binary)
```

返回 URL 供图文正文使用。

### 获取永久素材

```
POST https://api.weixin.qq.com/cgi-bin/material/get_material
  ?access_token=ACCESS_TOKEN

{"media_id": "MEDIA_ID"}
```

### 删除永久素材

```
POST https://api.weixin.qq.com/cgi-bin/material/del_material
  ?access_token=ACCESS_TOKEN

{"media_id": "MEDIA_ID"}
```

### 获取素材列表

```
POST https://api.weixin.qq.com/cgi-bin/material/batchget_material
  ?access_token=ACCESS_TOKEN

{
  "type": "image",
  "offset": 0,
  "count": 20
}
```

### 获取素材总数

```
GET https://api.weixin.qq.com/cgi-bin/material/get_materialcount
  ?access_token=ACCESS_TOKEN
```

## 草稿管理

### 新增草稿

```
POST https://api.weixin.qq.com/cgi-bin/draft/add
  ?access_token=ACCESS_TOKEN

{
  "articles": [{
    "title": "标题",
    "author": "作者",
    "digest": "摘要",
    "content": "<p>正文HTML</p>",
    "content_source_url": "原文链接",
    "thumb_media_id": "封面素材ID",
    "need_open_comment": 0,
    "only_fans_can_comment": 0
  }]
}
```

### 获取草稿

```
POST https://api.weixin.qq.com/cgi-bin/draft/get
  ?access_token=ACCESS_TOKEN

{"media_id": "MEDIA_ID"}
```

### 更新草稿

```
POST https://api.weixin.qq.com/cgi-bin/draft/update
  ?access_token=ACCESS_TOKEN

{
  "media_id": "MEDIA_ID",
  "index": 0,
  "articles": { ... }
}
```

### 删除草稿

```
POST https://api.weixin.qq.com/cgi-bin/draft/delete
  ?access_token=ACCESS_TOKEN

{"media_id": "MEDIA_ID"}
```

### 获取草稿列表

```
POST https://api.weixin.qq.com/cgi-bin/draft/batchget
  ?access_token=ACCESS_TOKEN

{
  "offset": 0,
  "count": 20,
  "no_content": 0
}
```

### 获取草稿总数

```
GET https://api.weixin.qq.com/cgi-bin/draft/count
  ?access_token=ACCESS_TOKEN
```

## 发布能力

### 发布草稿

```
POST https://api.weixin.qq.com/cgi-bin/freepublish/submit
  ?access_token=ACCESS_TOKEN

{"media_id": "MEDIA_ID"}
```

返回 publish_id。

### 查询发布状态

```
POST https://api.weixin.qq.com/cgi-bin/freepublish/get
  ?access_token=ACCESS_TOKEN

{"publish_id": "PUBLISH_ID"}
```

状态码：0=成功, 1=发布中, 2=原创失败, 3=常规失败, 4=审核不通过, 5=用户删除

### 获取已发布文章

```
POST https://api.weixin.qq.com/cgi-bin/freepublish/getarticle
  ?access_token=ACCESS_TOKEN

{"article_id": "ARTICLE_ID"}
```

### 删除已发布文章

```
POST https://api.weixin.qq.com/cgi-bin/freepublish/delete
  ?access_token=ACCESS_TOKEN

{"article_id": "ARTICLE_ID", "index": 0}
```

## 数据统计

### 用户增减数据

```
POST https://api.weixin.qq.com/datacube/getusersummary
  ?access_token=ACCESS_TOKEN

{"begin_date": "2024-01-01", "end_date": "2024-01-07"}
```

### 累计用户数据

```
POST https://api.weixin.qq.com/datacube/getusercumulate
  ?access_token=ACCESS_TOKEN

{"begin_date": "2024-01-01", "end_date": "2024-01-07"}
```

### 图文群发每日数据

```
POST https://api.weixin.qq.com/datacube/getarticlesummary
  ?access_token=ACCESS_TOKEN

{"begin_date": "2024-01-01", "end_date": "2024-01-01"}
```

### 图文阅读分时数据

```
POST https://api.weixin.qq.com/datacube/getuserreadhour
  ?access_token=ACCESS_TOKEN

{"begin_date": "2024-01-01", "end_date": "2024-01-01"}
```

详细数据统计 API 见 `references/stats_reference.md`

## 限制

| 类型 | 大小限制 | 数量限制 |
|------|----------|----------|
| 图片 | 10MB | 100,000 |
| 语音 | 2MB | 1,000 |
| 视频 | 10MB | 1,000 |
| 缩略图 | 64KB | - |
| 草稿图片 | - | 20张/篇 |
| 正文 | <1MB | <2万字符 |
| 标题 | - | <=32字符 |
| 作者 | - | <=16字符 |
| 摘要 | - | <=128字符 |
