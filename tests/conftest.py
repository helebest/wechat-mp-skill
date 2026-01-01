"""
pytest 配置和共享 fixtures
"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ==================== Mock Fixtures ====================

@pytest.fixture
def mock_access_token():
    """模拟的 access_token"""
    return "mock_access_token_1234567890"


@pytest.fixture
def mock_env_vars():
    """模拟环境变量"""
    with patch.dict(os.environ, {
        "WECHAT_APPID": "test_appid",
        "WECHAT_APPSECRET": "test_appsecret"
    }):
        yield


@pytest.fixture
def mock_token_response(mock_access_token):
    """模拟获取 token 的响应"""
    return {
        "access_token": mock_access_token,
        "expires_in": 7200
    }


@pytest.fixture
def mock_client(mock_env_vars, mock_access_token):
    """创建模拟的 WeChatClient"""
    with patch("scripts.wechat_client.requests") as mock_requests:
        # 模拟 token 请求
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "access_token": mock_access_token,
            "expires_in": 7200
        }
        mock_requests.get.return_value = mock_response
        mock_requests.request.return_value = mock_response

        from scripts import WeChatClient
        client = WeChatClient()
        client._mock_requests = mock_requests
        yield client


# ==================== E2E Fixtures ====================

def pytest_configure(config):
    """配置 pytest markers"""
    config.addinivalue_line(
        "markers", "e2e: end-to-end tests requiring real API credentials"
    )
    config.addinivalue_line(
        "markers", "unit: unit tests with mocked responses"
    )


@pytest.fixture
def real_client():
    """
    创建真实的 WeChatClient（用于 E2E 测试）
    需要设置 WECHAT_APPID 和 WECHAT_APPSECRET 环境变量
    """
    from dotenv import load_dotenv
    load_dotenv()

    appid = os.environ.get("WECHAT_APPID")
    appsecret = os.environ.get("WECHAT_APPSECRET")

    if not appid or not appsecret:
        pytest.skip("需要设置 WECHAT_APPID 和 WECHAT_APPSECRET 环境变量")

    from scripts import WeChatClient
    return WeChatClient()


@pytest.fixture
def real_material_manager(real_client):
    """创建真实的 MaterialManager"""
    from scripts import MaterialManager
    return MaterialManager(real_client)


@pytest.fixture
def real_draft_manager(real_client):
    """创建真实的 DraftManager"""
    from scripts import DraftManager
    return DraftManager(real_client)


@pytest.fixture
def real_stats_manager(real_client):
    """创建真实的 StatsManager"""
    from scripts import StatsManager
    return StatsManager(real_client)
