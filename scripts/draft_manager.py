#!/usr/bin/env python3
"""
微信公众号草稿管理模块
支持草稿的增删改查和发布
"""

from typing import Optional, Dict, Any, List, Literal

try:
    from .wechat_client import WeChatClient, WeChatAPIError
except ImportError:
    from wechat_client import WeChatClient, WeChatAPIError


ArticleType = Literal["news", "newspic"]


class DraftManager:
    """草稿管理器"""
    
    def __init__(self, client: WeChatClient):
        """
        初始化草稿管理器
        
        Args:
            client: 微信客户端实例
        """
        self.client = client
    
    def _validate_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """验证并规范化文章数据"""
        required_fields = ["title", "content"]
        
        for field in required_fields:
            if field not in article:
                raise ValueError(f"文章缺少必填字段: {field}")
        
        # 标题长度检查
        if len(article["title"]) > 32:
            raise ValueError("标题长度不能超过32个字符")
        
        # 作者长度检查
        if article.get("author") and len(article["author"]) > 16:
            raise ValueError("作者名长度不能超过16个字符")
        
        # 摘要长度检查
        if article.get("digest") and len(article["digest"]) > 128:
            raise ValueError("摘要长度不能超过128个字符")
        
        return article
    
    def create_draft(
        self,
        articles: List[Dict[str, Any]]
    ) -> str:
        """
        新增草稿
        
        Args:
            articles: 文章列表，每篇文章包含:
                - title: 标题（必填，<=32字符）
                - content: 正文 HTML（必填，<2万字符）
                - thumb_media_id: 封面图素材ID（图文消息必填）
                - author: 作者（可选，<=16字符）
                - digest: 摘要（可选，<=128字符）
                - content_source_url: 原文链接（可选）
                - need_open_comment: 是否打开评论 0/1（可选，默认0）
                - only_fans_can_comment: 是否仅粉丝可评论 0/1（可选，默认0）
                - article_type: 文章类型 news/newspic（可选，默认news）
                - pic_crop_235_1: 封面裁剪坐标2.35:1（可选）
                - pic_crop_1_1: 封面裁剪坐标1:1（可选）
                
        Returns:
            media_id: 草稿 ID
        """
        if not articles:
            raise ValueError("文章列表不能为空")
        
        # 验证每篇文章
        validated_articles = [
            self._validate_article(article) for article in articles
        ]
        
        result = self.client.post(
            "/cgi-bin/draft/add",
            json_data={"articles": validated_articles}
        )
        
        return result["media_id"]
    
    def get_draft(self, media_id: str) -> Dict[str, Any]:
        """
        获取草稿详情
        
        Args:
            media_id: 草稿 ID
            
        Returns:
            草稿详情，包含 news_item 文章列表
        """
        return self.client.post(
            "/cgi-bin/draft/get",
            json_data={"media_id": media_id}
        )
    
    def update_draft(
        self,
        media_id: str,
        index: int,
        article: Dict[str, Any]
    ) -> bool:
        """
        更新草稿中的指定文章
        
        Args:
            media_id: 草稿 ID
            index: 要更新的文章索引（从0开始）
            article: 新的文章内容（字段同 create_draft）
            
        Returns:
            是否更新成功
        """
        validated_article = self._validate_article(article)
        
        self.client.post(
            "/cgi-bin/draft/update",
            json_data={
                "media_id": media_id,
                "index": index,
                "articles": validated_article
            }
        )
        
        return True
    
    def delete_draft(self, media_id: str) -> bool:
        """
        删除草稿
        
        Args:
            media_id: 草稿 ID
            
        Returns:
            是否删除成功
        """
        self.client.post(
            "/cgi-bin/draft/delete",
            json_data={"media_id": media_id}
        )
        return True
    
    def list_drafts(
        self,
        offset: int = 0,
        count: int = 20,
        no_content: bool = False
    ) -> Dict[str, Any]:
        """
        获取草稿列表
        
        Args:
            offset: 偏移量
            count: 返回数量（1-20）
            no_content: 是否不返回正文内容
            
        Returns:
            草稿列表，包含:
            - total_count: 总数
            - item_count: 本次返回数量
            - item: 草稿列表
        """
        if count < 1 or count > 20:
            count = 20
        
        return self.client.post(
            "/cgi-bin/draft/batchget",
            json_data={
                "offset": offset,
                "count": count,
                "no_content": 1 if no_content else 0
            }
        )
    
    def get_draft_count(self) -> int:
        """
        获取草稿总数
        
        Returns:
            草稿总数
        """
        result = self.client.get("/cgi-bin/draft/count")
        return result["total_count"]
    
    def set_draft_switch(self, is_open: bool) -> bool:
        """
        设置草稿箱开关
        
        Args:
            is_open: 是否开启草稿箱功能
            
        Returns:
            是否设置成功
        """
        self.client.post(
            "/cgi-bin/draft/switch",
            json_data={"checkonly": 0}
        )
        return True
    
    def get_draft_switch(self) -> bool:
        """
        查询草稿箱开关状态
        
        Returns:
            是否已开启草稿箱功能
        """
        result = self.client.post(
            "/cgi-bin/draft/switch",
            json_data={"checkonly": 1}
        )
        return result.get("is_open", False)
    
    # ==================== 发布相关 ====================
    
    def publish_draft(self, media_id: str) -> str:
        """
        发布草稿
        
        Args:
            media_id: 草稿 ID
            
        Returns:
            publish_id: 发布任务 ID
        """
        result = self.client.post(
            "/cgi-bin/freepublish/submit",
            json_data={"media_id": media_id}
        )
        return result["publish_id"]
    
    def get_publish_status(self, publish_id: str) -> Dict[str, Any]:
        """
        查询发布状态
        
        Args:
            publish_id: 发布任务 ID
            
        Returns:
            发布状态，包含:
            - publish_id: 发布任务 ID
            - publish_status: 0=成功, 1=发布中, 2=原创失败, 3=常规失败,
                              4=平台审核不通过, 5=成功后用户删除
            - article_id: 发布成功时的文章 ID
            - fail_idx: 失败的文章索引列表
        """
        return self.client.post(
            "/cgi-bin/freepublish/get",
            json_data={"publish_id": publish_id}
        )
    
    def get_published_article(self, article_id: str) -> Dict[str, Any]:
        """
        获取已发布文章详情
        
        Args:
            article_id: 文章 ID
            
        Returns:
            文章详情
        """
        return self.client.post(
            "/cgi-bin/freepublish/getarticle",
            json_data={"article_id": article_id}
        )
    
    def list_published(
        self,
        offset: int = 0,
        count: int = 20,
        no_content: bool = False
    ) -> Dict[str, Any]:
        """
        获取已发布文章列表
        
        Args:
            offset: 偏移量
            count: 返回数量（1-20）
            no_content: 是否不返回正文内容
            
        Returns:
            已发布文章列表
        """
        if count < 1 or count > 20:
            count = 20
        
        return self.client.post(
            "/cgi-bin/freepublish/batchget",
            json_data={
                "offset": offset,
                "count": count,
                "no_content": 1 if no_content else 0
            }
        )
    
    def delete_published(self, article_id: str, index: int = 0) -> bool:
        """
        删除已发布文章
        
        Args:
            article_id: 文章 ID
            index: 要删除的文章索引（多图文时使用）
            
        Returns:
            是否删除成功
        """
        self.client.post(
            "/cgi-bin/freepublish/delete",
            json_data={
                "article_id": article_id,
                "index": index
            }
        )
        return True


# 便捷函数
def create_draft_manager(
    client: Optional[WeChatClient] = None
) -> DraftManager:
    """创建草稿管理器实例"""
    if client is None:
        client = WeChatClient()
    return DraftManager(client)


def create_simple_article(
    title: str,
    content: str,
    thumb_media_id: str,
    author: Optional[str] = None,
    digest: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建简单的文章字典
    
    Args:
        title: 标题
        content: 正文 HTML
        thumb_media_id: 封面图素材 ID
        author: 作者（可选）
        digest: 摘要（可选）
        
    Returns:
        文章字典
    """
    article = {
        "title": title,
        "content": content,
        "thumb_media_id": thumb_media_id
    }
    
    if author:
        article["author"] = author
    if digest:
        article["digest"] = digest
    
    return article


if __name__ == "__main__":
    # 测试
    client = WeChatClient()
    dm = DraftManager(client)
    
    # 获取草稿数量
    count = dm.get_draft_count()
    print(f"草稿总数: {count}")
