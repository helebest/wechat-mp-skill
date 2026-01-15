"""
HtmlSubmitter 单元测试
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestParseFileUri:
    """测试 file:// URI 解析"""

    @pytest.mark.unit
    def test_parse_windows_file_uri(self):
        """测试 Windows file:// URI"""
        from scripts.html_submitter import _parse_file_uri

        # 标准 Windows 路径
        uri = "file:///C:/Users/test/image.png"
        assert _parse_file_uri(uri) == "C:/Users/test/image.png"

    @pytest.mark.unit
    def test_parse_windows_file_uri_with_spaces(self):
        """测试带空格的 Windows file:// URI"""
        from scripts.html_submitter import _parse_file_uri

        # URL 编码的空格
        uri = "file:///C:/Users/HE%20LE/Project/image.png"
        assert _parse_file_uri(uri) == "C:/Users/HE LE/Project/image.png"

    @pytest.mark.unit
    def test_parse_unix_file_uri(self):
        """测试 Unix file:// URI"""
        from scripts.html_submitter import _parse_file_uri

        uri = "file:///home/user/image.png"
        assert _parse_file_uri(uri) == "/home/user/image.png"

    @pytest.mark.unit
    def test_parse_file_uri_chinese_chars(self):
        """测试中文字符的 URL 编码"""
        from scripts.html_submitter import _parse_file_uri

        # 中文路径 URL 编码
        uri = "file:///C:/Users/test/%E5%9B%BE%E7%89%87.png"
        assert _parse_file_uri(uri) == "C:/Users/test/图片.png"


class TestExtractLocalImages:
    """测试本地图片路径提取"""

    @pytest.mark.unit
    def test_extract_file_uri_images(self, tmp_path):
        """测试提取 file:// 协议的图片"""
        from scripts.html_submitter import _extract_local_images

        html = '''
        <img src="file:///C:/Users/test/image1.png" />
        <img src="file:///C:/Users/test/image2.jpg" />
        '''

        images = _extract_local_images(html, tmp_path)
        assert len(images) == 2
        assert images[0][0] == "file:///C:/Users/test/image1.png"
        assert images[0][1] == "C:/Users/test/image1.png"

    @pytest.mark.unit
    def test_extract_relative_path_images(self, tmp_path):
        """测试提取相对路径的图片"""
        from scripts.html_submitter import _extract_local_images

        html = '<img src="images/photo.jpg" />'

        images = _extract_local_images(html, tmp_path)
        assert len(images) == 1
        assert images[0][0] == "images/photo.jpg"
        assert images[0][1] == str(tmp_path / "images/photo.jpg")

    @pytest.mark.unit
    def test_skip_http_images(self, tmp_path):
        """测试跳过 http/https 图片"""
        from scripts.html_submitter import _extract_local_images

        html = '''
        <img src="https://example.com/image.png" />
        <img src="http://example.com/image.jpg" />
        <img src="file:///C:/local.png" />
        '''

        images = _extract_local_images(html, tmp_path)
        assert len(images) == 1
        assert "file:///" in images[0][0]

    @pytest.mark.unit
    def test_extract_images_with_single_quotes(self, tmp_path):
        """测试单引号的 src 属性"""
        from scripts.html_submitter import _extract_local_images

        html = "<img src='images/photo.jpg' />"

        images = _extract_local_images(html, tmp_path)
        assert len(images) == 1


class TestExtractTitle:
    """测试标题提取"""

    @pytest.mark.unit
    def test_extract_title(self):
        """测试从 HTML 提取标题"""
        from scripts.html_submitter import _extract_title

        html = "<html><head><title>测试标题</title></head></html>"
        assert _extract_title(html) == "测试标题"

    @pytest.mark.unit
    def test_extract_title_with_whitespace(self):
        """测试带空白的标题"""
        from scripts.html_submitter import _extract_title

        html = "<title>  标题带空格  </title>"
        assert _extract_title(html) == "标题带空格"

    @pytest.mark.unit
    def test_extract_title_missing(self):
        """测试缺少标题"""
        from scripts.html_submitter import _extract_title

        html = "<html><body>内容</body></html>"
        assert _extract_title(html) is None


class TestExtractBody:
    """测试 body 内容提取"""

    @pytest.mark.unit
    def test_extract_body(self):
        """测试提取 body 内容"""
        from scripts.html_submitter import _extract_body

        html = "<html><body><p>段落内容</p></body></html>"
        assert "<p>段落内容</p>" in _extract_body(html)

    @pytest.mark.unit
    def test_extract_body_with_attributes(self):
        """测试带属性的 body"""
        from scripts.html_submitter import _extract_body

        html = '<body class="article"><div>内容</div></body>'
        body = _extract_body(html)
        assert "<div>内容</div>" in body
        assert "class=" not in body  # body 标签属性不应包含

    @pytest.mark.unit
    def test_extract_body_missing(self):
        """测试缺少 body 标签"""
        from scripts.html_submitter import _extract_body

        html = "<div>直接内容</div>"
        assert _extract_body(html) == html


class TestSubmitHtmlDraft:
    """测试 HTML 草稿提交"""

    @pytest.mark.unit
    def test_submit_html_file_not_found(self, mock_client):
        """测试 HTML 文件不存在"""
        from scripts.html_submitter import submit_html_draft

        with pytest.raises(FileNotFoundError, match="HTML 文件不存在"):
            submit_html_draft(
                html_path="/nonexistent/file.html",
                cover_path="/nonexistent/cover.png",
                client=mock_client
            )

    @pytest.mark.unit
    def test_submit_cover_not_found(self, mock_client, tmp_path):
        """测试封面图不存在"""
        from scripts.html_submitter import submit_html_draft

        # 创建 HTML 文件
        html_file = tmp_path / "test.html"
        html_file.write_text("<html><title>Test</title><body>Content</body></html>")

        with pytest.raises(FileNotFoundError, match="封面图不存在"):
            submit_html_draft(
                html_path=str(html_file),
                cover_path="/nonexistent/cover.png",
                client=mock_client
            )

    @pytest.mark.unit
    def test_submit_missing_title(self, mock_client, tmp_path):
        """测试缺少标题"""
        from scripts.html_submitter import submit_html_draft, HtmlSubmitError

        # 创建无标题的 HTML
        html_file = tmp_path / "test.html"
        html_file.write_text("<html><body>Content</body></html>")

        cover_file = tmp_path / "cover.png"
        cover_file.write_bytes(b"fake image")

        with pytest.raises(HtmlSubmitError, match="未提供标题"):
            submit_html_draft(
                html_path=str(html_file),
                cover_path=str(cover_file),
                client=mock_client
            )

    @pytest.mark.unit
    def test_submit_with_explicit_title(self, mock_env_vars, tmp_path):
        """测试使用显式指定的标题"""
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
                "media_id": "cover_media_id"
            }

            draft_response = MagicMock()
            draft_response.json.return_value = {
                "errcode": 0,
                "media_id": "draft_media_id"
            }

            mock_requests.get.return_value = token_response
            mock_requests.request.side_effect = [upload_response, draft_response]

            # 创建测试文件（无 title 标签）
            html_file = tmp_path / "test.html"
            html_file.write_text("<html><body><p>Content</p></body></html>")

            cover_file = tmp_path / "cover.png"
            cover_file.write_bytes(b"fake image")

            from scripts.html_submitter import submit_html_draft

            media_id = submit_html_draft(
                html_path=str(html_file),
                cover_path=str(cover_file),
                title="显式标题"
            )

            assert media_id == "draft_media_id"

    @pytest.mark.unit
    def test_submit_full_workflow(self, mock_env_vars, tmp_path):
        """测试完整提交流程"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            # 设置 mock 响应
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            cover_upload_response = MagicMock()
            cover_upload_response.json.return_value = {
                "errcode": 0,
                "media_id": "cover_media_id"
            }

            image_upload_response = MagicMock()
            image_upload_response.json.return_value = {
                "errcode": 0,
                "url": "https://mmbiz.qpic.cn/uploaded.jpg"
            }

            draft_response = MagicMock()
            draft_response.json.return_value = {
                "errcode": 0,
                "media_id": "draft_media_id"
            }

            mock_requests.get.return_value = token_response
            mock_requests.request.side_effect = [
                cover_upload_response,
                image_upload_response,
                draft_response
            ]

            # 创建测试文件
            html_file = tmp_path / "test.html"
            image_file = tmp_path / "image.png"
            image_file.write_bytes(b"fake image data")

            html_content = f'''
            <html>
            <head><title>测试文章</title></head>
            <body>
                <p>正文内容</p>
                <img src="{image_file}" />
            </body>
            </html>
            '''
            html_file.write_text(html_content, encoding="utf-8")

            cover_file = tmp_path / "cover.png"
            cover_file.write_bytes(b"fake cover image")

            from scripts.html_submitter import submit_html_draft

            media_id = submit_html_draft(
                html_path=str(html_file),
                cover_path=str(cover_file),
                author="测试作者",
                digest="测试摘要"
            )

            assert media_id == "draft_media_id"

    @pytest.mark.unit
    def test_image_upload_error_file_not_found(self, mock_env_vars, tmp_path):
        """测试正文图片不存在时的错误"""
        with patch("scripts.wechat_client.requests") as mock_requests:
            token_response = MagicMock()
            token_response.json.return_value = {
                "access_token": "test_token",
                "expires_in": 7200
            }

            cover_upload_response = MagicMock()
            cover_upload_response.json.return_value = {
                "errcode": 0,
                "media_id": "cover_media_id"
            }

            mock_requests.get.return_value = token_response
            mock_requests.request.return_value = cover_upload_response

            # 创建 HTML 引用不存在的图片
            html_file = tmp_path / "test.html"
            html_content = '''
            <html>
            <head><title>测试</title></head>
            <body>
                <img src="nonexistent.png" />
            </body>
            </html>
            '''
            html_file.write_text(html_content, encoding="utf-8")

            cover_file = tmp_path / "cover.png"
            cover_file.write_bytes(b"fake cover")

            from scripts.html_submitter import submit_html_draft, ImageUploadError

            with pytest.raises(ImageUploadError, match="文件不存在"):
                submit_html_draft(
                    html_path=str(html_file),
                    cover_path=str(cover_file)
                )


class TestExceptionClasses:
    """测试异常类"""

    @pytest.mark.unit
    def test_html_submit_error(self):
        """测试 HtmlSubmitError"""
        from scripts.html_submitter import HtmlSubmitError

        error = HtmlSubmitError("测试错误")
        assert str(error) == "测试错误"

    @pytest.mark.unit
    def test_image_upload_error(self):
        """测试 ImageUploadError"""
        from scripts.html_submitter import ImageUploadError

        error = ImageUploadError("/path/to/image.png", "文件不存在")
        assert "/path/to/image.png" in str(error)
        assert "文件不存在" in str(error)
        assert error.path == "/path/to/image.png"
        assert error.reason == "文件不存在"
