# 数据统计 API 参考

## 查询限制

| 数据类型 | 最大跨度 | 说明 |
|----------|----------|------|
| 用户增减/累计 | 7天 | begin_date 到 end_date |
| 图文每日数据 | 1天 | 只能查询单日 |
| 图文阅读概况 | 3天 | |
| 图文转发概况 | 7天 | |
| 消息发送概况 | 7天 | |
| 消息分布数据 | 15天 | |
| 消息周/月数据 | 30天 | |
| 接口调用数据 | 30天 | |

**注意**: 结束日期不能是今天，最早只能查询昨天的数据。

## 用户数据

### 获取用户增减数据

```
POST /datacube/getusersummary

{
  "begin_date": "2024-01-01",
  "end_date": "2024-01-07"
}
```

返回字段：
- `ref_date`: 日期
- `user_source`: 用户来源（0其他/1搜索/17名片/...）
- `new_user`: 新增用户数
- `cancel_user`: 取消关注数

### 获取累计用户数据

```
POST /datacube/getusercumulate

{
  "begin_date": "2024-01-01",
  "end_date": "2024-01-07"
}
```

返回字段：
- `ref_date`: 日期
- `cumulate_user`: 累计用户数

## 图文数据

### 获取图文群发每日数据

```
POST /datacube/getarticlesummary

{
  "begin_date": "2024-01-01",
  "end_date": "2024-01-01"
}
```

返回字段：
- `ref_date`: 日期
- `msgid`: 消息ID
- `title`: 标题
- `int_page_read_user`: 图文页阅读人数
- `int_page_read_count`: 图文页阅读次数
- `ori_page_read_user`: 原文页阅读人数
- `ori_page_read_count`: 原文页阅读次数
- `share_user`: 分享人数
- `share_count`: 分享次数
- `add_to_fav_user`: 收藏人数
- `add_to_fav_count`: 收藏次数

### 获取图文群发总数据

```
POST /datacube/getarticletotal

{
  "begin_date": "2024-01-01",
  "end_date": "2024-01-01"
}
```

返回从群发日起的总量统计。

### 获取图文阅读概况

```
POST /datacube/getuserread

{
  "begin_date": "2024-01-01",
  "end_date": "2024-01-03"
}
```

### 获取图文阅读分时数据

```
POST /datacube/getuserreadhour

{
  "begin_date": "2024-01-01",
  "end_date": "2024-01-01"
}
```

返回每小时数据，`ref_hour` 为小时 (0-23)。

### 获取图文转发概况

```
POST /datacube/getusershare

{
  "begin_date": "2024-01-01",
  "end_date": "2024-01-07"
}
```

### 获取图文转发分时数据

```
POST /datacube/getusersharehour

{
  "begin_date": "2024-01-01",
  "end_date": "2024-01-01"
}
```

## 消息数据

### 获取消息发送概况

```
POST /datacube/getupstreammsg

{
  "begin_date": "2024-01-01",
  "end_date": "2024-01-07"
}
```

返回字段：
- `ref_date`: 日期
- `msg_type`: 消息类型
- `msg_user`: 发送人数
- `msg_count`: 发送次数

### 获取消息发送分时数据

```
POST /datacube/getupstreammsghour
```

### 获取消息发送周数据

```
POST /datacube/getupstreammsgweek
```

### 获取消息发送月数据

```
POST /datacube/getupstreammsgmonth
```

### 获取消息发送分布数据

```
POST /datacube/getupstreammsgdist
```

返回按消息数量区间统计的用户数。

## 接口数据

### 获取被动回复概要

```
POST /datacube/getinterfacesummary

{
  "begin_date": "2024-01-01",
  "end_date": "2024-01-30"
}
```

返回字段：
- `ref_date`: 日期
- `callback_count`: 回复次数
- `fail_count`: 失败次数
- `total_time_cost`: 总耗时
- `max_time_cost`: 最大耗时

### 获取被动回复分布

```
POST /datacube/getinterfacesummaryhour
```

返回每小时的接口调用数据。

## 用户来源说明

| 值 | 来源 |
|----|------|
| 0 | 其他合计 |
| 1 | 公众号搜索 |
| 17 | 名片分享 |
| 30 | 扫描二维码 |
| 43 | 图文页右上角菜单 |
| 51 | 支付后关注 |
| 57 | 文章内公众号名称 |
| 75 | 公众号文章广告 |
| 78 | 朋友圈广告 |

## 便捷方法示例

```python
from scripts.stats_manager import StatsManager
from scripts.wechat_client import WeChatClient

client = WeChatClient()
sm = StatsManager(client)

# 快速获取昨日概览
yesterday = sm.get_yesterday_summary()
print(f"昨日新增: {sum(u['new_user'] for u in yesterday['user'])}")
print(f"昨日取关: {sum(u['cancel_user'] for u in yesterday['user'])}")

# 快速获取本周概览
week = sm.get_week_summary()
cumulate = week['user_cumulate']
if cumulate:
    print(f"当前总粉丝: {cumulate[-1]['cumulate_user']}")
```
