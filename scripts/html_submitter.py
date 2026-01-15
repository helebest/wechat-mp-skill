#!/usr/bin/env python3
"""
HTML 文章提交模块
接收 HTML 文件，自动处理图片上传并创建草稿
"""

import re
from pathlib import Path
from typing import Optional, List, Tuple
from urllib.parse import unquote

try:
    from .wechat_client import WeChatClient
    from .material_manager import MaterialManager
    from .draft_manager import DraftManager, create_simple_article
except ImportError:
    from wechat_client import WeChatClient
    from material_manager import MaterialManager
    from draft_manager import DraftManager, create_simple_article


class HtmlSubmitError(Exception):
    """HTML 提交错误"""
    pass


class ImageUploadError(HtmlSubmitError):
    """图片上传错误"""

    def __init__(self, path: str, reason: str):
        self.path = path
        self.reason = reason
        super().__init__(f"图片上传失败: {path}\n原因: {reason}")


def _parse_file_uri(uri: str) -> str:
    """
    解析 file:// URI 为本地路径

    支持格式:
    - file:///C:/Users/... (Windows)
    - file:///home/user/... (Unix)

    Args:
        uri: file:// 协议的 URI

    Returns:
        解码后的本地路径
    """
    if not uri.startswith("file://"):
        return unquote(uri)

    # 去掉 file:// 前缀（7 个字符），保留后面的路径
    path = uri[7:]

    # Windows 路径: file:///C:/path -> /C:/path -> C:/path
    # Unix 路径: file:///home/path -> /home/path (保持不变)
    if len(path) >= 3 and path[0] == "/" and path[2] == ":":
        # Windows: /C:/path -> C:/path
        path = path[1:]

    # URL 解码（处理 %20 等）
    return unquote(path)


def _extract_local_images(html: str, html_dir: Path) -> List[Tuple[str, str]]:
    """
    从 HTML 中提取本地图片路径

    Args:
        html: HTML 内容
        html_dir: HTML 文件所在目录（用于解析相对路径）

    Returns:
        列表，每项为 (原始 src 值, 本地文件路径)
    """
    img_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
    local_images = []

    for match in re.finditer(img_pattern, html, re.IGNORECASE):
        src = match.group(1)

        # 跳过已经是 http/https 的 URL
        if src.startswith(("http://", "https://")):
            continue

        # 处理 file:// 协议
        if src.startswith("file://"):
            local_path = _parse_file_uri(src)
        else:
            # 相对路径，相对于 HTML 文件目录
            local_path = str(html_dir / src)

        local_images.append((src, local_path))

    return local_images


def _extract_title(html: str) -> Optional[str]:
    """从 HTML 中提取标题"""
    match = re.search(r'<title>(.+?)</title>', html, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def _extract_body(html: str) -> str:
    """从 HTML 中提取 body 内容"""
    match = re.search(r'<body[^>]*>(.*?)</body>', html, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return html


def submit_html_draft(
    html_path: str,
    cover_path: str,
    title: Optional[str] = None,
    author: Optional[str] = None,
    digest: Optional[str] = None,
    client: Optional[WeChatClient] = None
) -> str:
    """
    提交 HTML 文章到微信公众号草稿

    自动完成：
    1. 解析 HTML 中的本地图片引用
    2. 上传封面图和正文图片
    3. 替换图片路径为微信 URL
    4. 创建草稿

    Args:
        html_path: HTML 文件路径
        cover_path: 封面图路径
        title: 文章标题（不提供则从 <title> 提取）
        author: 作者（可选）
        digest: 摘要（可选）
        client: 微信客户端（可选，不提供则自动创建）

    Returns:
        草稿 media_id

    Raises:
        FileNotFoundError: HTML 文件或封面图不存在
        HtmlSubmitError: 标题缺失
        ImageUploadError: 图片上传失败
    """
    html_file = Path(html_path)
    cover_file = Path(cover_path)

    # 验证文件存在
    if not html_file.exists():
        raise FileNotFoundError(f"HTML 文件不存在: {html_path}")
    if not cover_file.exists():
        raise FileNotFoundError(f"封面图不存在: {cover_path}")

    # 初始化客户端
    if client is None:
        client = WeChatClient()

    mm = MaterialManager(client)
    dm = DraftManager(client)

    # 1. 读取 HTML
    html_content = html_file.read_text(encoding="utf-8")

    # 2. 提取标题
    if not title:
        title = _extract_title(html_content)
        if not title:
            raise HtmlSubmitError("未提供标题且无法从 HTML 中提取")

    # 3. 提取 body 内容
    body_html = _extract_body(html_content)

    # 4. 解析本地图片
    local_images = _extract_local_images(body_html, html_file.parent)

    # 5. 上传封面图
    try:
        cover_media_id = mm.upload_permanent("image", str(cover_file))
    except Exception as e:
        raise ImageUploadError(str(cover_path), str(e))

    # 6. 上传正文图片并替换 URL
    for original_src, local_path in local_images:
        if not Path(local_path).exists():
            raise ImageUploadError(local_path, "文件不存在")

        try:
            url = mm.upload_article_image(local_path)
        except Exception as e:
            raise ImageUploadError(local_path, str(e))

        # 替换 src（保持引号类型）
        body_html = body_html.replace(f'src="{original_src}"', f'src="{url}"')
        body_html = body_html.replace(f"src='{original_src}'", f"src='{url}'")

    # 7. 创建草稿
    article = create_simple_article(
        title=title,
        content=body_html,
        thumb_media_id=cover_media_id,
        author=author,
        digest=digest
    )

    media_id = dm.create_draft([article])
    return media_id


if __name__ == "__main__":
    # 使用示例
    print("HTML 提交模块")
    print("使用方法:")
    print("  from scripts.html_submitter import submit_html_draft")
    print("  media_id = submit_html_draft('article.html', 'cover.png')")
