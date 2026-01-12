"""
WeChatClient 单元测试
"""

import os
import pytest
from unittest.mock import patch, MagicMock


class TestWeChatClientInit:
    """测试客户端初始化"""

    @pytest.mark.unit
    def test_init_with_params(self, mock_env_vars):
        """测试通过参数初始化"""
        with patch("scripts.wechat_client.requests"):
            from scripts import WeChatClient
            client = WeChatClient(appid="param_appid", appsecret="param_secret")
            assert client.appid == "param_appid"
            assert client.appsecret == "param_secret"

    @pytest.mark.unit
    def test_init_with_env_vars(self, mock_env_vars):
        """测试通过环境变量初始化"""
        with patch("scripts.wechat_client.requests"):
            from scripts import WeChatClient
            client = WeChatClient()
            assert client.appid == "test_appid"
            assert client.appsecret == "test_appsecret"

    @pytest.mark.unit
    def test_init_missing_credentials(self):
        """测试缺少凭证时抛出异常"""
        with patch.dict(os.environ, {"HOME": "/tmp", "USERPROFILE": "C:\\Users\\test"}, clear=True):
            with patch("scripts.wechat_client.find_dotenv", return_value=""):
                from scripts import WeChatClient
                with pytest.raises(ValueError, match="请设置 WECHAT_APPID"):
                    WeChatClient()


class TestAccessToken:
    """测试 access_token 管理"""

    @pytest.mark.unit
    def test_get_access_token(self, mock_env_vars, tmp_path):
        """测试获取 access_token"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "access_token": "test_token_12345",
                "expires_in": 7200
            }
            mock_requests.get.return_value = mock_response

            from scripts.wechat_client import WeChatClient
            # 使用临时目录避免加载缓存
            client = WeChatClient(token_cache_dir=str(tmp_path))
            token = client.get_access_token()

            assert token == "test_token_12345"

    @pytest.mark.unit
    def test_token_caching(self, mock_client):
        """测试 token 缓存"""
        # 第一次获取
        token1 = mock_client.get_access_token()
        # 第二次应该使用缓存
        token2 = mock_client.get_access_token()
        assert token1 == token2

    @pytest.mark.unit
    def test_force_refresh_token(self, mock_env_vars):
        """测试强制刷新 token"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "access_token": "new_token",
                "expires_in": 7200
            }
            mock_requests.get.return_value = mock_response

            from scripts import WeChatClient
            client = WeChatClient()

            # 强制刷新
            token = client.get_access_token(force_refresh=True)
            assert token == "new_token"


class TestApiRequest:
    """测试 API 请求"""

    @pytest.mark.unit
    def test_get_request(self, mock_env_vars):
        """测试 GET 请求"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            # Token 响应
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            # API 响应
            api_response = MagicMock()
            api_response.json.return_value = {"errcode": 0, "data": "test"}

            mock_requests.get.return_value = token_response
            mock_requests.request.return_value = api_response

            from scripts import WeChatClient
            client = WeChatClient()
            result = client.get("/test/endpoint")

            assert result["data"] == "test"

    @pytest.mark.unit
    def test_post_request(self, mock_env_vars):
        """测试 POST 请求"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            api_response = MagicMock()
            api_response.json.return_value = {"errcode": 0, "media_id": "123"}

            mock_requests.get.return_value = token_response
            mock_requests.request.return_value = api_response

            from scripts import WeChatClient
            client = WeChatClient()
            result = client.post("/test/endpoint", json_data={"key": "value"})

            assert result["media_id"] == "123"

    @pytest.mark.unit
    def test_api_error_handling(self, mock_env_vars):
        """测试 API 错误处理"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            error_response = MagicMock()
            error_response.json.return_value = {
                "errcode": 40001,
                "errmsg": "invalid credential"
            }

            mock_requests.get.return_value = token_response
            mock_requests.request.return_value = error_response

            from scripts import WeChatClient, WeChatAPIError
            client = WeChatClient()

            with pytest.raises(WeChatAPIError) as exc_info:
                client.get("/test/endpoint")

            assert exc_info.value.errcode == 40001


class TestLoadDotenv:
    """测试 .env 文件加载（python-dotenv 集成）"""

    @pytest.mark.unit
    def test_load_dotenv_integration(self, tmp_path):
        """测试 python-dotenv 集成加载 .env 文件"""
        # 创建临时 .env 文件
        env_file = tmp_path / ".env"
        env_file.write_text('TEST_VAR="test_value"\n')

        from scripts.wechat_client import load_dotenv

        with patch.dict(os.environ, {}, clear=True):
            load_dotenv(str(env_file))
            assert os.environ.get("TEST_VAR") == "test_value"
