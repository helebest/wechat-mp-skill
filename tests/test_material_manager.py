"""
MaterialManager 单元测试
"""

import os
import pytest
from unittest.mock import patch, MagicMock


class TestMaterialManagerInit:
    """测试素材管理器初始化"""

    @pytest.mark.unit
    def test_init_with_client(self, mock_client):
        """测试通过客户端初始化"""
        from scripts import MaterialManager
        mm = MaterialManager(mock_client)
        assert mm.client == mock_client

    @pytest.mark.unit
    def test_create_material_manager(self, mock_env_vars):
        """测试便捷创建函数"""
        with patch("scripts.wechat_client.requests"):
            with patch("scripts.material_manager.WeChatClient"):
                from scripts import create_material_manager
                mm = create_material_manager()
                assert mm is not None


class TestFileValidation:
    """测试文件验证"""

    @pytest.mark.unit
    def test_validate_file_not_exists(self, mock_client):
        """测试文件不存在"""
        from scripts import MaterialManager
        mm = MaterialManager(mock_client)

        with pytest.raises(FileNotFoundError, match="文件不存在"):
            mm._validate_file("/nonexistent/file.jpg", "image")

    @pytest.mark.unit
    def test_validate_file_too_large(self, mock_client, tmp_path):
        """测试文件过大"""
        from scripts import MaterialManager
        mm = MaterialManager(mock_client)

        # 创建超大文件（模拟）
        large_file = tmp_path / "large.jpg"
        large_file.write_bytes(b"x" * (11 * 1024 * 1024))  # 11MB

        with pytest.raises(ValueError, match="超过限制"):
            mm._validate_file(str(large_file), "image")


class TestPermanentMaterial:
    """测试永久素材操作"""

    @pytest.mark.unit
    def test_upload_permanent(self, mock_env_vars, tmp_path):
        """测试上传永久素材"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            # 设置 mock 响应
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            upload_response = MagicMock()
            upload_response.json.return_value = {
                "errcode": 0,
                "media_id": "uploaded_media_id"
            }

            mock_requests.get.return_value = token_response
            mock_requests.request.return_value = upload_response

            # 创建测试文件
            test_file = tmp_path / "test.jpg"
            test_file.write_bytes(b"fake image data")

            from scripts import WeChatClient, MaterialManager
            client = WeChatClient()
            mm = MaterialManager(client)

            media_id = mm.upload_permanent("image", str(test_file))
            assert media_id == "uploaded_media_id"

    @pytest.mark.unit
    def test_get_material_count(self, mock_env_vars):
        """测试获取素材统计"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            count_response = MagicMock()
            count_response.json.return_value = {
                "errcode": 0,
                "voice_count": 10,
                "video_count": 5,
                "image_count": 100,
                "news_count": 20
            }

            mock_requests.get.return_value = token_response
            mock_requests.request.return_value = count_response

            from scripts import WeChatClient, MaterialManager
            client = WeChatClient()
            mm = MaterialManager(client)

            stats = mm.get_material_count()
            assert stats["image_count"] == 100
            assert stats["video_count"] == 5

    @pytest.mark.unit
    def test_list_materials(self, mock_env_vars):
        """测试获取素材列表"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            list_response = MagicMock()
            list_response.json.return_value = {
                "errcode": 0,
                "total_count": 50,
                "item_count": 20,
                "item": [{"media_id": "id1"}, {"media_id": "id2"}]
            }

            mock_requests.get.return_value = token_response
            mock_requests.request.return_value = list_response

            from scripts import WeChatClient, MaterialManager
            client = WeChatClient()
            mm = MaterialManager(client)

            result = mm.list_materials("image", offset=0, count=20)
            assert result["total_count"] == 50
            assert len(result["item"]) == 2

    @pytest.mark.unit
    def test_delete_material(self, mock_env_vars):
        """测试删除素材"""
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

            from scripts import WeChatClient, MaterialManager
            client = WeChatClient()
            mm = MaterialManager(client)

            result = mm.delete_material("test_media_id")
            assert result is True


class TestArticleImage:
    """测试图文内图片"""

    @pytest.mark.unit
    def test_upload_article_image(self, mock_env_vars, tmp_path):
        """测试上传图文内图片"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            upload_response = MagicMock()
            upload_response.json.return_value = {
                "errcode": 0,
                "url": "https://mmbiz.qpic.cn/xxx.jpg"
            }

            mock_requests.get.return_value = token_response
            mock_requests.request.return_value = upload_response

            test_file = tmp_path / "content.jpg"
            test_file.write_bytes(b"fake image data")

            from scripts import WeChatClient, MaterialManager
            client = WeChatClient()
            mm = MaterialManager(client)

            url = mm.upload_article_image(str(test_file))
            assert url.startswith("https://")


class TestTemporaryMaterial:
    """测试临时素材"""

    @pytest.mark.unit
    def test_upload_temporary(self, mock_env_vars, tmp_path):
        """测试上传临时素材"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            upload_response = MagicMock()
            upload_response.json.return_value = {
                "errcode": 0,
                "media_id": "temp_media_id",
                "type": "image",
                "created_at": 1234567890
            }

            mock_requests.get.return_value = token_response
            mock_requests.request.return_value = upload_response

            test_file = tmp_path / "temp.jpg"
            test_file.write_bytes(b"fake image data")

            from scripts import WeChatClient, MaterialManager
            client = WeChatClient()
            mm = MaterialManager(client)

            result = mm.upload_temporary("image", str(test_file))
            assert result["media_id"] == "temp_media_id"
            assert result["type"] == "image"
