# 微信公众号 API 错误码

## 通用错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| -1 | 系统繁忙 | 稍后重试 |
| 0 | 请求成功 | - |
| 40001 | access_token 无效 | 重新获取 token |
| 40002 | grant_type 无效 | 检查参数 |
| 40003 | openid 无效 | 检查 openid |
| 40014 | access_token 无效 | 重新获取 token |
| 40033 | 请求 URL 无效 | 检查 URL |
| 41001 | 缺少 access_token | 添加 token 参数 |
| 42001 | access_token 过期 | 重新获取 token |
| 45009 | API 调用频率超限 | 降低调用频率 |
| 45015 | 回复时间超限 | 用户发消息48小时内 |
| 48001 | API 未授权 | 检查公众号权限 |
| 50001 | 用户未授权 | 请求用户授权 |

## 素材相关错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 40004 | 媒体文件无效 | 检查文件格式和大小 |
| 40005 | 文件类型无效 | 使用支持的文件类型 |
| 40006 | 文件大小超限 | 压缩文件 |
| 40007 | 媒体文件ID无效 | 检查 media_id |
| 45001 | 多媒体文件大小超限 | 压缩文件 |
| 45002 | 消息内容超长 | 减少内容 |
| 45003 | 标题过长 | <=64字符 |
| 45004 | 描述过长 | <=128字符 |
| 45005 | 链接过长 | 缩短链接 |
| 45006 | 图片链接过长 | 缩短链接 |
| 45007 | 语音时长超限 | <=60秒 |
| 45008 | 图文消息超限 | <=8篇 |
| 45010 | 语音文件数量超限 | 减少数量 |
| 45011 | 图片数量超限 | 减少数量 |
| 45012 | 素材数量超限 | 删除旧素材 |

## 草稿相关错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 53404 | 账号已被限制带货能力 | 删除商品后重试 |
| 53405 | 插入商品信息有误 | 检查商品参数 |
| 53406 | 请先开通带货能力 | 在公众平台开通 |

## 发布相关错误码

发布状态码：
- 0 = 发布成功
- 1 = 发布中
- 2 = 原创失败（可重试）
- 3 = 常规失败（需检查内容）
- 4 = 平台审核不通过
- 5 = 成功后用户删除

## 错误处理示例

```python
from scripts.wechat_client import WeChatClient, WeChatAPIError

client = WeChatClient()

try:
    result = client.post("/cgi-bin/draft/add", json_data={...})
except WeChatAPIError as e:
    if e.errcode == 40001:
        # token 无效，自动重试
        pass
    elif e.errcode == 45003:
        print("标题过长，请控制在64字符以内")
    else:
        print(f"API错误: [{e.errcode}] {e.errmsg}")
```

## 调试工具

官方 API 调试工具：
https://developers.weixin.qq.com/console/devtools/debug

查询 rid 详情：
```python
result = client.post(
    "/cgi-bin/openapi/rid/get",
    json_data={"rid": "错误返回的rid"}
)
```
