"""
StatsManager 单元测试
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock


class TestStatsManagerInit:
    """测试数据统计管理器初始化"""

    @pytest.mark.unit
    def test_init_with_client(self, mock_client):
        """测试通过客户端初始化"""
        from scripts import StatsManager
        sm = StatsManager(mock_client)
        assert sm.client == mock_client


class TestDateValidation:
    """测试日期验证"""

    @pytest.mark.unit
    def test_validate_date_range_begin_after_end(self, mock_client):
        """测试开始日期晚于结束日期"""
        from scripts import StatsManager
        sm = StatsManager(mock_client)

        with pytest.raises(ValueError, match="开始日期不能晚于结束日期"):
            sm._validate_date_range("2024-01-10", "2024-01-01", 7)

    @pytest.mark.unit
    def test_validate_date_range_exceed_max_days(self, mock_client):
        """测试超过最大天数"""
        from scripts import StatsManager
        sm = StatsManager(mock_client)

        with pytest.raises(ValueError, match="日期跨度不能超过 7 天"):
            sm._validate_date_range("2024-01-01", "2024-01-10", 7)

    @pytest.mark.unit
    def test_validate_date_range_future_date(self, mock_client):
        """测试未来日期"""
        from scripts import StatsManager
        sm = StatsManager(mock_client)

        future = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        with pytest.raises(ValueError, match="结束日期不能是今天或未来日期"):
            sm._validate_date_range(future, future, 7)


class TestUserStats:
    """测试用户数据统计"""

    @pytest.mark.unit
    def test_get_user_summary(self, mock_env_vars):
        """测试获取用户增减数据"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            stats_response = MagicMock()
            stats_response.json.return_value = {
                "errcode": 0,
                "list": [
                    {"ref_date": "2024-01-01", "new_user": 10, "cancel_user": 2}
                ]
            }

            mock_requests.get.return_value = token_response
            mock_requests.request.return_value = stats_response

            from scripts import WeChatClient, StatsManager
            client = WeChatClient()
            sm = StatsManager(client)

            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            result = sm.get_user_summary(yesterday, yesterday)

            assert len(result) == 1
            assert result[0]["new_user"] == 10

    @pytest.mark.unit
    def test_get_user_cumulate(self, mock_env_vars):
        """测试获取累计用户数据"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            stats_response = MagicMock()
            stats_response.json.return_value = {
                "errcode": 0,
                "list": [
                    {"ref_date": "2024-01-01", "cumulate_user": 1000}
                ]
            }

            mock_requests.get.return_value = token_response
            mock_requests.request.return_value = stats_response

            from scripts import WeChatClient, StatsManager
            client = WeChatClient()
            sm = StatsManager(client)

            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            result = sm.get_user_cumulate(yesterday, yesterday)

            assert len(result) == 1
            assert result[0]["cumulate_user"] == 1000


class TestArticleStats:
    """测试图文数据统计"""

    @pytest.mark.unit
    def test_get_article_summary(self, mock_env_vars):
        """测试获取图文每日数据"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            stats_response = MagicMock()
            stats_response.json.return_value = {
                "errcode": 0,
                "list": [
                    {
                        "ref_date": "2024-01-01",
                        "title": "测试文章",
                        "int_page_read_count": 100,
                        "share_count": 10
                    }
                ]
            }

            mock_requests.get.return_value = token_response
            mock_requests.request.return_value = stats_response

            from scripts import WeChatClient, StatsManager
            client = WeChatClient()
            sm = StatsManager(client)

            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            result = sm.get_article_summary(yesterday)

            assert len(result) == 1
            assert result[0]["int_page_read_count"] == 100

    @pytest.mark.unit
    def test_get_user_read_hour(self, mock_env_vars):
        """测试获取分时阅读数据"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            stats_response = MagicMock()
            stats_response.json.return_value = {
                "errcode": 0,
                "list": [
                    {"ref_date": "2024-01-01", "ref_hour": 10, "int_page_read_count": 50}
                ]
            }

            mock_requests.get.return_value = token_response
            mock_requests.request.return_value = stats_response

            from scripts import WeChatClient, StatsManager
            client = WeChatClient()
            sm = StatsManager(client)

            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            result = sm.get_user_read_hour(yesterday)

            assert len(result) == 1
            assert result[0]["ref_hour"] == 10


class TestMessageStats:
    """测试消息数据统计"""

    @pytest.mark.unit
    def test_get_upstream_msg(self, mock_env_vars):
        """测试获取消息发送数据"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            stats_response = MagicMock()
            stats_response.json.return_value = {
                "errcode": 0,
                "list": [
                    {"ref_date": "2024-01-01", "msg_count": 500}
                ]
            }

            mock_requests.get.return_value = token_response
            mock_requests.request.return_value = stats_response

            from scripts import WeChatClient, StatsManager
            client = WeChatClient()
            sm = StatsManager(client)

            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            result = sm.get_upstream_msg(yesterday, yesterday)

            assert len(result) == 1
            assert result[0]["msg_count"] == 500


class TestConvenienceMethods:
    """测试便捷方法"""

    @pytest.mark.unit
    def test_get_yesterday_summary(self, mock_env_vars):
        """测试获取昨日概览"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            stats_response = MagicMock()
            stats_response.json.return_value = {
                "errcode": 0,
                "list": []
            }

            mock_requests.get.return_value = token_response
            mock_requests.request.return_value = stats_response

            from scripts import WeChatClient, StatsManager
            client = WeChatClient()
            sm = StatsManager(client)

            result = sm.get_yesterday_summary()

            assert "date" in result
            assert "user" in result
            assert "user_cumulate" in result
            assert "article" in result
            assert "share" in result

    @pytest.mark.unit
    def test_get_week_summary(self, mock_env_vars):
        """测试获取本周概览"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            stats_response = MagicMock()
            stats_response.json.return_value = {
                "errcode": 0,
                "list": []
            }

            mock_requests.get.return_value = token_response
            mock_requests.request.return_value = stats_response

            from scripts import WeChatClient, StatsManager
            client = WeChatClient()
            sm = StatsManager(client)

            result = sm.get_week_summary()

            assert "begin_date" in result
            assert "end_date" in result
            assert "user" in result
            assert "user_cumulate" in result
            assert "share" in result
