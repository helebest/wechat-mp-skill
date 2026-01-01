#!/usr/bin/env python3
"""
微信公众号素材管理模块
支持永久素材和临时素材的增删改查
"""

import os
import mimetypes
from typing import Optional, Dict, Any, List, Literal
from pathlib import Path

try:
    from .wechat_client import WeChatClient, WeChatAPIError
except ImportError:
    from wechat_client import WeChatClient, WeChatAPIError


MaterialType = Literal["image", "voice", "video", "thumb"]


class MaterialManager:
    """素材管理器"""
    
    # 素材类型对应的 MIME 类型
    MEDIA_TYPES = {
        "image": ["image/jpeg", "image/png", "image/gif", "image/bmp"],
        "voice": ["audio/mp3", "audio/amr", "audio/mpeg"],
        "video": ["video/mp4"],
        "thumb": ["image/jpeg"]
    }
    
    # 素材大小限制（字节）
    SIZE_LIMITS = {
        "image": 10 * 1024 * 1024,  # 10MB
        "voice": 2 * 1024 * 1024,   # 2MB
        "video": 10 * 1024 * 1024,  # 10MB
        "thumb": 64 * 1024          # 64KB
    }
    
    def __init__(self, client: WeChatClient):
        """
        初始化素材管理器
        
        Args:
            client: 微信客户端实例
        """
        self.client = client
    
    def _validate_file(
        self,
        file_path: str,
        media_type: MaterialType
    ) -> None:
        """验证文件是否符合要求"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 检查文件大小
        size = path.stat().st_size
        limit = self.SIZE_LIMITS.get(media_type, 10 * 1024 * 1024)
        if size > limit:
            raise ValueError(
                f"文件大小 {size / 1024 / 1024:.2f}MB 超过限制 "
                f"{limit / 1024 / 1024:.2f}MB"
            )
    
    # ==================== 永久素材 ====================
    
    def upload_permanent(
        self,
        media_type: MaterialType,
        file_path: str,
        title: Optional[str] = None,
        introduction: Optional[str] = None
    ) -> str:
        """
        上传永久素材
        
        Args:
            media_type: 素材类型 (image/voice/video/thumb)
            file_path: 文件路径
            title: 视频标题（仅视频类型需要）
            introduction: 视频描述（仅视频类型需要）
            
        Returns:
            media_id: 素材 ID
        """
        self._validate_file(file_path, media_type)
        
        endpoint = "/cgi-bin/material/add_material"
        
        extra_data = {"type": media_type}
        
        # 视频需要额外参数
        if media_type == "video":
            if not title:
                title = Path(file_path).stem
            description = {
                "title": title,
                "introduction": introduction or ""
            }
            import json
            extra_data["description"] = json.dumps(description)
        
        result = self.client.upload_file(
            endpoint,
            file_path,
            file_field="media",
            extra_data=extra_data
        )
        
        return result["media_id"]
    
    def upload_article_image(self, file_path: str) -> str:
        """
        上传图文消息内的图片
        
        用于在图文消息正文中使用的图片，返回 URL 而非 media_id
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            图片 URL（可在图文正文中使用）
        """
        self._validate_file(file_path, "image")
        
        result = self.client.upload_file(
            "/cgi-bin/media/uploadimg",
            file_path,
            file_field="media"
        )
        
        return result["url"]
    
    def get_material(self, media_id: str) -> Dict[str, Any]:
        """
        获取永久素材详情
        
        Args:
            media_id: 素材 ID
            
        Returns:
            素材信息（图文返回详情，其他返回二进制内容）
        """
        result = self.client.post(
            "/cgi-bin/material/get_material",
            json_data={"media_id": media_id}
        )
        return result
    
    def download_material(
        self,
        media_id: str,
        save_path: Optional[str] = None
    ) -> bytes:
        """
        下载永久素材文件
        
        Args:
            media_id: 素材 ID
            save_path: 保存路径（可选）
            
        Returns:
            文件二进制内容
        """
        content = self.client.download_file(
            "/cgi-bin/material/get_material",
            json_data={"media_id": media_id}
        )
        
        if save_path:
            with open(save_path, "wb") as f:
                f.write(content)
        
        return content
    
    def delete_material(self, media_id: str) -> bool:
        """
        删除永久素材
        
        Args:
            media_id: 素材 ID
            
        Returns:
            是否删除成功
        """
        self.client.post(
            "/cgi-bin/material/del_material",
            json_data={"media_id": media_id}
        )
        return True
    
    def get_material_count(self) -> Dict[str, int]:
        """
        获取永久素材总数
        
        Returns:
            各类型素材数量，包含:
            - voice_count: 语音数量
            - video_count: 视频数量
            - image_count: 图片数量
            - news_count: 图文数量
        """
        return self.client.get("/cgi-bin/material/get_materialcount")
    
    def list_materials(
        self,
        media_type: MaterialType,
        offset: int = 0,
        count: int = 20
    ) -> Dict[str, Any]:
        """
        获取永久素材列表
        
        Args:
            media_type: 素材类型 (image/voice/video/news)
            offset: 偏移量
            count: 返回数量（1-20）
            
        Returns:
            素材列表，包含:
            - total_count: 总数
            - item_count: 本次返回数量
            - item: 素材列表
        """
        if count < 1 or count > 20:
            count = 20
        
        return self.client.post(
            "/cgi-bin/material/batchget_material",
            json_data={
                "type": media_type,
                "offset": offset,
                "count": count
            }
        )
    
    # ==================== 临时素材 ====================
    
    def upload_temporary(
        self,
        media_type: MaterialType,
        file_path: str
    ) -> Dict[str, Any]:
        """
        上传临时素材（有效期 3 天）
        
        Args:
            media_type: 素材类型 (image/voice/video/thumb)
            file_path: 文件路径
            
        Returns:
            包含 media_id 和 created_at 的字典
        """
        self._validate_file(file_path, media_type)
        
        result = self.client.upload_file(
            "/cgi-bin/media/upload",
            file_path,
            file_field="media",
            extra_data={"type": media_type}
        )
        
        return {
            "media_id": result["media_id"],
            "type": result.get("type", media_type),
            "created_at": result.get("created_at")
        }
    
    def get_temporary(
        self,
        media_id: str,
        save_path: Optional[str] = None
    ) -> bytes:
        """
        获取临时素材
        
        Args:
            media_id: 素材 ID
            save_path: 保存路径（可选）
            
        Returns:
            文件二进制内容
        """
        content = self.client.download_file(
            "/cgi-bin/media/get",
            params={"media_id": media_id}
        )
        
        if save_path:
            with open(save_path, "wb") as f:
                f.write(content)
        
        return content
    
    def get_hd_voice(
        self,
        media_id: str,
        save_path: Optional[str] = None
    ) -> bytes:
        """
        获取高清语音素材
        
        用于 JSSDK 上传的语音素材
        
        Args:
            media_id: 素材 ID
            save_path: 保存路径（可选）
            
        Returns:
            语音文件二进制内容
        """
        content = self.client.download_file(
            "/cgi-bin/media/get/jssdk",
            params={"media_id": media_id}
        )
        
        if save_path:
            with open(save_path, "wb") as f:
                f.write(content)
        
        return content


# 便捷函数
def create_material_manager(
    client: Optional[WeChatClient] = None
) -> MaterialManager:
    """创建素材管理器实例"""
    if client is None:
        client = WeChatClient()
    return MaterialManager(client)


if __name__ == "__main__":
    # 测试
    client = WeChatClient()
    mm = MaterialManager(client)
    
    # 获取素材统计
    stats = mm.get_material_count()
    print(f"素材统计: {stats}")
