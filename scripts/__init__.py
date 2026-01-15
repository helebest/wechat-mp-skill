"""
微信公众号管理工具集
"""

from .wechat_client import WeChatClient, WeChatAPIError, create_client, load_dotenv
from .material_manager import MaterialManager, create_material_manager
from .draft_manager import DraftManager, create_draft_manager, create_simple_article
from .stats_manager import StatsManager, create_stats_manager
from .html_submitter import submit_html_draft, HtmlSubmitError, ImageUploadError

__all__ = [
    "WeChatClient",
    "WeChatAPIError",
    "create_client",
    "load_dotenv",
    "MaterialManager",
    "create_material_manager",
    "DraftManager",
    "create_draft_manager",
    "create_simple_article",
    "StatsManager",
    "create_stats_manager",
    "submit_html_draft",
    "HtmlSubmitError",
    "ImageUploadError",
]
