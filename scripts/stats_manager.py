#!/usr/bin/env python3
"""
微信公众号数据统计模块
支持用户、图文、消息、接口等数据统计
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

try:
    from .wechat_client import WeChatClient, WeChatAPIError
except ImportError:
    from wechat_client import WeChatClient, WeChatAPIError


class StatsManager:
    """数据统计管理器"""
    
    # 最大查询跨度（天）
    MAX_USER_DAYS = 7
    MAX_ARTICLE_DAYS = 1
    MAX_MESSAGE_DAYS = 7
    MAX_INTERFACE_DAYS = 30
    
    def __init__(self, client: WeChatClient):
        """
        初始化数据统计管理器
        
        Args:
            client: 微信客户端实例
        """
        self.client = client
    
    def _format_date(self, date: datetime) -> str:
        """格式化日期为 API 需要的格式"""
        return date.strftime("%Y-%m-%d")
    
    def _validate_date_range(
        self,
        begin_date: str,
        end_date: str,
        max_days: int
    ) -> None:
        """验证日期范围"""
        begin = datetime.strptime(begin_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        if begin > end:
            raise ValueError("开始日期不能晚于结束日期")
        
        if (end - begin).days > max_days:
            raise ValueError(f"日期跨度不能超过 {max_days} 天")
        
        if end >= datetime.now():
            raise ValueError("结束日期不能是今天或未来日期")
    
    # ==================== 用户数据 ====================
    
    def get_user_summary(
        self,
        begin_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        获取用户增减数据
        
        Args:
            begin_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)，最大跨度7天
            
        Returns:
            每日用户数据列表，包含:
            - ref_date: 日期
            - user_source: 用户来源
            - new_user: 新增用户数
            - cancel_user: 取消关注数
        """
        self._validate_date_range(begin_date, end_date, self.MAX_USER_DAYS)
        
        result = self.client.post(
            "/datacube/getusersummary",
            json_data={
                "begin_date": begin_date,
                "end_date": end_date
            }
        )
        return result.get("list", [])
    
    def get_user_cumulate(
        self,
        begin_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        获取累计用户数据
        
        Args:
            begin_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)，最大跨度7天
            
        Returns:
            每日累计用户数据列表，包含:
            - ref_date: 日期
            - cumulate_user: 累计用户数
        """
        self._validate_date_range(begin_date, end_date, self.MAX_USER_DAYS)
        
        result = self.client.post(
            "/datacube/getusercumulate",
            json_data={
                "begin_date": begin_date,
                "end_date": end_date
            }
        )
        return result.get("list", [])
    
    # ==================== 图文数据 ====================
    
    def get_article_summary(self, date: str) -> List[Dict[str, Any]]:
        """
        获取图文群发每日数据
        
        Args:
            date: 日期 (YYYY-MM-DD)，只能查询单日
            
        Returns:
            图文数据列表，包含:
            - ref_date: 日期
            - msgid: 消息ID
            - title: 标题
            - int_page_read_user: 图文页阅读人数
            - int_page_read_count: 图文页阅读次数
            - ori_page_read_user: 原文页阅读人数
            - ori_page_read_count: 原文页阅读次数
            - share_user: 分享人数
            - share_count: 分享次数
            - add_to_fav_user: 收藏人数
            - add_to_fav_count: 收藏次数
        """
        self._validate_date_range(date, date, self.MAX_ARTICLE_DAYS)
        
        result = self.client.post(
            "/datacube/getarticlesummary",
            json_data={
                "begin_date": date,
                "end_date": date
            }
        )
        return result.get("list", [])
    
    def get_article_total(self, date: str) -> List[Dict[str, Any]]:
        """
        获取图文群发总数据
        
        获取某天群发文章从群发日起的总量统计数据
        
        Args:
            date: 日期 (YYYY-MM-DD)
            
        Returns:
            图文总数据列表
        """
        self._validate_date_range(date, date, self.MAX_ARTICLE_DAYS)
        
        result = self.client.post(
            "/datacube/getarticletotal",
            json_data={
                "begin_date": date,
                "end_date": date
            }
        )
        return result.get("list", [])
    
    def get_user_read(
        self,
        begin_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        获取图文阅读概况数据
        
        Args:
            begin_date: 开始日期
            end_date: 结束日期，最大跨度3天
            
        Returns:
            阅读概况数据列表
        """
        self._validate_date_range(begin_date, end_date, 3)
        
        result = self.client.post(
            "/datacube/getuserread",
            json_data={
                "begin_date": begin_date,
                "end_date": end_date
            }
        )
        return result.get("list", [])
    
    def get_user_read_hour(self, date: str) -> List[Dict[str, Any]]:
        """
        获取图文阅读分时数据
        
        Args:
            date: 日期 (YYYY-MM-DD)
            
        Returns:
            每小时阅读数据列表
        """
        self._validate_date_range(date, date, self.MAX_ARTICLE_DAYS)
        
        result = self.client.post(
            "/datacube/getuserreadhour",
            json_data={
                "begin_date": date,
                "end_date": date
            }
        )
        return result.get("list", [])
    
    def get_user_share(
        self,
        begin_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        获取图文转发概况数据
        
        Args:
            begin_date: 开始日期
            end_date: 结束日期，最大跨度7天
            
        Returns:
            转发概况数据列表
        """
        self._validate_date_range(begin_date, end_date, self.MAX_USER_DAYS)
        
        result = self.client.post(
            "/datacube/getusershare",
            json_data={
                "begin_date": begin_date,
                "end_date": end_date
            }
        )
        return result.get("list", [])
    
    def get_user_share_hour(self, date: str) -> List[Dict[str, Any]]:
        """
        获取图文转发分时数据
        
        Args:
            date: 日期 (YYYY-MM-DD)
            
        Returns:
            每小时转发数据列表
        """
        self._validate_date_range(date, date, self.MAX_ARTICLE_DAYS)
        
        result = self.client.post(
            "/datacube/getusersharehour",
            json_data={
                "begin_date": date,
                "end_date": date
            }
        )
        return result.get("list", [])
    
    # ==================== 消息数据 ====================
    
    def get_upstream_msg(
        self,
        begin_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        获取消息发送概况数据
        
        Args:
            begin_date: 开始日期
            end_date: 结束日期，最大跨度7天
            
        Returns:
            消息发送概况数据列表
        """
        self._validate_date_range(begin_date, end_date, self.MAX_MESSAGE_DAYS)
        
        result = self.client.post(
            "/datacube/getupstreammsg",
            json_data={
                "begin_date": begin_date,
                "end_date": end_date
            }
        )
        return result.get("list", [])
    
    def get_upstream_msg_hour(self, date: str) -> List[Dict[str, Any]]:
        """
        获取消息发送分时数据
        
        Args:
            date: 日期 (YYYY-MM-DD)
            
        Returns:
            每小时消息发送数据列表
        """
        self._validate_date_range(date, date, self.MAX_ARTICLE_DAYS)
        
        result = self.client.post(
            "/datacube/getupstreammsghour",
            json_data={
                "begin_date": date,
                "end_date": date
            }
        )
        return result.get("list", [])
    
    def get_upstream_msg_week(
        self,
        begin_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        获取消息发送周数据
        
        Args:
            begin_date: 开始日期
            end_date: 结束日期，最大跨度30天
            
        Returns:
            每周消息发送数据列表
        """
        self._validate_date_range(begin_date, end_date, self.MAX_INTERFACE_DAYS)
        
        result = self.client.post(
            "/datacube/getupstreammsgweek",
            json_data={
                "begin_date": begin_date,
                "end_date": end_date
            }
        )
        return result.get("list", [])
    
    def get_upstream_msg_month(
        self,
        begin_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        获取消息发送月数据
        
        Args:
            begin_date: 开始日期
            end_date: 结束日期，最大跨度30天
            
        Returns:
            每月消息发送数据列表
        """
        self._validate_date_range(begin_date, end_date, self.MAX_INTERFACE_DAYS)
        
        result = self.client.post(
            "/datacube/getupstreammsgmonth",
            json_data={
                "begin_date": begin_date,
                "end_date": end_date
            }
        )
        return result.get("list", [])
    
    def get_upstream_msg_dist(
        self,
        begin_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        获取消息发送分布数据
        
        Args:
            begin_date: 开始日期
            end_date: 结束日期，最大跨度15天
            
        Returns:
            消息发送分布数据列表
        """
        self._validate_date_range(begin_date, end_date, 15)
        
        result = self.client.post(
            "/datacube/getupstreammsgdist",
            json_data={
                "begin_date": begin_date,
                "end_date": end_date
            }
        )
        return result.get("list", [])
    
    # ==================== 接口数据 ====================
    
    def get_interface_summary(
        self,
        begin_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        获取被动回复概要数据
        
        Args:
            begin_date: 开始日期
            end_date: 结束日期，最大跨度30天
            
        Returns:
            接口调用概要数据列表
        """
        self._validate_date_range(begin_date, end_date, self.MAX_INTERFACE_DAYS)
        
        result = self.client.post(
            "/datacube/getinterfacesummary",
            json_data={
                "begin_date": begin_date,
                "end_date": end_date
            }
        )
        return result.get("list", [])
    
    def get_interface_summary_hour(self, date: str) -> List[Dict[str, Any]]:
        """
        获取被动回复分布数据
        
        Args:
            date: 日期 (YYYY-MM-DD)
            
        Returns:
            每小时接口调用数据列表
        """
        self._validate_date_range(date, date, self.MAX_ARTICLE_DAYS)
        
        result = self.client.post(
            "/datacube/getinterfacesummaryhour",
            json_data={
                "begin_date": date,
                "end_date": date
            }
        )
        return result.get("list", [])
    
    # ==================== 便捷方法 ====================
    
    def get_yesterday_summary(self) -> Dict[str, Any]:
        """
        获取昨日概览数据
        
        Returns:
            包含用户、阅读、分享数据的汇总
        """
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        return {
            "date": yesterday,
            "user": self.get_user_summary(yesterday, yesterday),
            "user_cumulate": self.get_user_cumulate(yesterday, yesterday),
            "article": self.get_article_summary(yesterday),
            "share": self.get_user_share(yesterday, yesterday)
        }
    
    def get_week_summary(self) -> Dict[str, Any]:
        """
        获取最近7天概览数据
        
        Returns:
            包含用户增减和累计数据的汇总
        """
        end = datetime.now() - timedelta(days=1)
        begin = end - timedelta(days=6)
        
        begin_str = begin.strftime("%Y-%m-%d")
        end_str = end.strftime("%Y-%m-%d")
        
        return {
            "begin_date": begin_str,
            "end_date": end_str,
            "user": self.get_user_summary(begin_str, end_str),
            "user_cumulate": self.get_user_cumulate(begin_str, end_str),
            "share": self.get_user_share(begin_str, end_str)
        }


# 便捷函数
def create_stats_manager(
    client: Optional[WeChatClient] = None
) -> StatsManager:
    """创建数据统计管理器实例"""
    if client is None:
        client = WeChatClient()
    return StatsManager(client)


if __name__ == "__main__":
    # 测试
    client = WeChatClient()
    sm = StatsManager(client)
    
    # 获取昨日概览
    summary = sm.get_yesterday_summary()
    print(f"昨日数据: {summary}")
