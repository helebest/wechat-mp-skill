"""
DraftManager 单元测试
"""

import pytest
from unittest.mock import patch, MagicMock


class TestDraftManagerInit:
    """测试草稿管理器初始化"""

    @pytest.mark.unit
    def test_init_with_client(self, mock_client):
        """测试通过客户端初始化"""
        from scripts import DraftManager
        dm = DraftManager(mock_client)
        assert dm.client == mock_client


class TestArticleValidation:
    """测试文章验证"""

    @pytest.mark.unit
    def test_validate_article_missing_title(self, mock_client):
        """测试缺少标题"""
        from scripts import DraftManager
        dm = DraftManager(mock_client)

        with pytest.raises(ValueError, match="缺少必填字段: title"):
            dm._validate_article({"content": "<p>test</p>"})

    @pytest.mark.unit
    def test_validate_article_missing_content(self, mock_client):
        """测试缺少内容"""
        from scripts import DraftManager
        dm = DraftManager(mock_client)

        with pytest.raises(ValueError, match="缺少必填字段: content"):
            dm._validate_article({"title": "test"})

    @pytest.mark.unit
    def test_validate_article_title_too_long(self, mock_client):
        """测试标题过长"""
        from scripts import DraftManager
        dm = DraftManager(mock_client)

        with pytest.raises(ValueError, match="标题长度不能超过32个字符"):
            dm._validate_article({
                "title": "x" * 33,
                "content": "<p>test</p>"
            })

    @pytest.mark.unit
    def test_validate_article_author_too_long(self, mock_client):
        """测试作者名过长"""
        from scripts import DraftManager
        dm = DraftManager(mock_client)

        with pytest.raises(ValueError, match="作者名长度不能超过16个字符"):
            dm._validate_article({
                "title": "test",
                "content": "<p>test</p>",
                "author": "x" * 17
            })

    @pytest.mark.unit
    def test_validate_article_success(self, mock_client):
        """测试验证通过"""
        from scripts import DraftManager
        dm = DraftManager(mock_client)

        article = {
            "title": "测试标题",
            "content": "<p>测试内容</p>",
            "author": "作者"
        }
        result = dm._validate_article(article)
        assert result == article


class TestDraftCRUD:
    """测试草稿增删改查"""

    @pytest.mark.unit
    def test_create_draft(self, mock_env_vars):
        """测试创建草稿"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            create_response = MagicMock()
            create_response.json.return_value = {
                "errcode": 0,
                "media_id": "draft_media_id"
            }

            mock_requests.get.return_value = token_response
            mock_requests.request.return_value = create_response

            from scripts import WeChatClient, DraftManager
            client = WeChatClient()
            dm = DraftManager(client)

            articles = [{
                "title": "测试文章",
                "content": "<p>内容</p>",
                "thumb_media_id": "cover_id"
            }]

            media_id = dm.create_draft(articles)
            assert media_id == "draft_media_id"

    @pytest.mark.unit
    def test_create_draft_empty_articles(self, mock_client):
        """测试创建空草稿"""
        from scripts import DraftManager
        dm = DraftManager(mock_client)

        with pytest.raises(ValueError, match="文章列表不能为空"):
            dm.create_draft([])

    @pytest.mark.unit
    def test_get_draft(self, mock_env_vars):
        """测试获取草稿"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            get_response = MagicMock()
            get_response.json.return_value = {
                "errcode": 0,
                "news_item": [{
                    "title": "文章标题",
                    "content": "<p>内容</p>"
                }]
            }

            mock_requests.get.return_value = token_response
            mock_requests.request.return_value = get_response

            from scripts import WeChatClient, DraftManager
            client = WeChatClient()
            dm = DraftManager(client)

            result = dm.get_draft("test_media_id")
            assert "news_item" in result
            assert result["news_item"][0]["title"] == "文章标题"

    @pytest.mark.unit
    def test_delete_draft(self, mock_env_vars):
        """测试删除草稿"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            delete_response = MagicMock()
            delete_response.json.return_value = {"errcode": 0}

            mock_requests.get.return_value = token_response
            mock_requests.request.return_value = delete_response

            from scripts import WeChatClient, DraftManager
            client = WeChatClient()
            dm = DraftManager(client)

            result = dm.delete_draft("test_media_id")
            assert result is True

    @pytest.mark.unit
    def test_get_draft_count(self, mock_env_vars):
        """测试获取草稿数量"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            count_response = MagicMock()
            count_response.json.return_value = {
                "errcode": 0,
                "total_count": 15
            }

            mock_requests.get.return_value = token_response
            mock_requests.request.return_value = count_response

            from scripts import WeChatClient, DraftManager
            client = WeChatClient()
            dm = DraftManager(client)

            count = dm.get_draft_count()
            assert count == 15

    @pytest.mark.unit
    def test_list_drafts(self, mock_env_vars):
        """测试获取草稿列表"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            list_response = MagicMock()
            list_response.json.return_value = {
                "errcode": 0,
                "total_count": 30,
                "item_count": 20,
                "item": [{"media_id": "id1"}, {"media_id": "id2"}]
            }

            mock_requests.get.return_value = token_response
            mock_requests.request.return_value = list_response

            from scripts import WeChatClient, DraftManager
            client = WeChatClient()
            dm = DraftManager(client)

            result = dm.list_drafts(offset=0, count=20)
            assert result["total_count"] == 30
            assert len(result["item"]) == 2


class TestPublishing:
    """测试发布功能"""

    @pytest.mark.unit
    def test_publish_draft(self, mock_env_vars):
        """测试发布草稿"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            publish_response = MagicMock()
            publish_response.json.return_value = {
                "errcode": 0,
                "publish_id": "publish_123"
            }

            mock_requests.get.return_value = token_response
            mock_requests.request.return_value = publish_response

            from scripts import WeChatClient, DraftManager
            client = WeChatClient()
            dm = DraftManager(client)

            publish_id = dm.publish_draft("draft_media_id")
            assert publish_id == "publish_123"

    @pytest.mark.unit
    def test_get_publish_status(self, mock_env_vars):
        """测试查询发布状态"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            status_response = MagicMock()
            status_response.json.return_value = {
                "errcode": 0,
                "publish_id": "publish_123",
                "publish_status": 0,
                "article_id": "article_456"
            }

            mock_requests.get.return_value = token_response
            mock_requests.request.return_value = status_response

            from scripts import WeChatClient, DraftManager
            client = WeChatClient()
            dm = DraftManager(client)

            status = dm.get_publish_status("publish_123")
            assert status["publish_status"] == 0
            assert status["article_id"] == "article_456"


class TestHelperFunctions:
    """测试辅助函数"""

    @pytest.mark.unit
    def test_create_simple_article(self):
        """测试创建简单文章"""
        from scripts import create_simple_article

        article = create_simple_article(
            title="测试标题",
            content="<p>测试内容</p>",
            thumb_media_id="cover_123",
            author="作者",
            digest="摘要"
        )

        assert article["title"] == "测试标题"
        assert article["content"] == "<p>测试内容</p>"
        assert article["thumb_media_id"] == "cover_123"
        assert article["author"] == "作者"
        assert article["digest"] == "摘要"

    @pytest.mark.unit
    def test_create_simple_article_minimal(self):
        """测试创建最小文章"""
        from scripts import create_simple_article

        article = create_simple_article(
            title="标题",
            content="<p>内容</p>",
            thumb_media_id="cover_id"
        )

        assert article["title"] == "标题"
        assert "author" not in article
        assert "digest" not in article
