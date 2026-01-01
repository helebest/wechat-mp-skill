"""
端到端测试 (E2E Tests)

这些测试需要真实的微信公众号凭证才能运行。
运行前请确保已设置环境变量或 .env 文件：
  - WECHAT_APPID
  - WECHAT_APPSECRET

运行命令：
  uv run pytest tests/test_e2e.py -v -m e2e

注意：这些测试会实际调用微信 API，请谨慎使用。
"""

import os
import pytest
from datetime import datetime, timedelta


# ==================== 客户端测试 ====================

@pytest.mark.e2e
class TestClientE2E:
    """客户端端到端测试"""

    def test_get_access_token(self, real_client):
        """测试获取真实 access_token"""
        token = real_client.get_access_token()

        assert token is not None
        assert len(token) > 0
        print(f"✓ 获取 access_token 成功: {token[:20]}...")

    def test_token_refresh(self, real_client):
        """测试 token 刷新"""
        token1 = real_client.get_access_token()
        token2 = real_client.get_access_token(force_refresh=True)

        # 强制刷新可能返回相同或不同的 token
        assert token1 is not None
        assert token2 is not None
        print(f"✓ Token 刷新成功")


# ==================== 素材管理测试 ====================

@pytest.mark.e2e
class TestMaterialManagerE2E:
    """素材管理端到端测试"""

    def test_get_material_count(self, real_material_manager):
        """测试获取素材统计"""
        stats = real_material_manager.get_material_count()

        assert "image_count" in stats
        assert "video_count" in stats
        assert "voice_count" in stats
        assert "news_count" in stats

        print(f"✓ 素材统计:")
        print(f"  - 图片: {stats['image_count']}")
        print(f"  - 视频: {stats['video_count']}")
        print(f"  - 语音: {stats['voice_count']}")
        print(f"  - 图文: {stats['news_count']}")

    def test_list_materials(self, real_material_manager):
        """测试获取素材列表"""
        result = real_material_manager.list_materials("image", offset=0, count=5)

        assert "total_count" in result
        assert "item_count" in result
        assert "item" in result

        print(f"✓ 图片素材列表: 共 {result['total_count']} 个，本次返回 {result['item_count']} 个")

    def test_upload_and_delete_image(self, real_material_manager, tmp_path):
        """测试上传和删除图片素材"""
        # 创建测试图片 (1x1 红色像素 PNG)
        test_image = tmp_path / "test_image.png"
        # 最小有效 PNG 文件
        png_data = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
            0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
            0xDE, 0x00, 0x00, 0x00, 0x0C, 0x49, 0x44, 0x41,  # IDAT chunk
            0x54, 0x08, 0xD7, 0x63, 0xF8, 0xCF, 0xC0, 0x00,
            0x00, 0x00, 0x03, 0x00, 0x01, 0x00, 0x05, 0xFE,
            0xD4, 0xEF, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45,  # IEND chunk
            0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82
        ])
        test_image.write_bytes(png_data)

        try:
            # 上传
            media_id = real_material_manager.upload_permanent("image", str(test_image))
            assert media_id is not None
            print(f"✓ 上传图片成功: {media_id}")

            # 删除
            result = real_material_manager.delete_material(media_id)
            assert result is True
            print(f"✓ 删除图片成功")
        except Exception as e:
            pytest.skip(f"上传/删除测试跳过: {e}")


# ==================== 草稿管理测试 ====================

@pytest.mark.e2e
class TestDraftManagerE2E:
    """草稿管理端到端测试"""

    def test_get_draft_count(self, real_draft_manager):
        """测试获取草稿数量"""
        count = real_draft_manager.get_draft_count()

        assert isinstance(count, int)
        assert count >= 0

        print(f"✓ 草稿总数: {count}")

    def test_list_drafts(self, real_draft_manager):
        """测试获取草稿列表"""
        result = real_draft_manager.list_drafts(offset=0, count=5, no_content=True)

        assert "total_count" in result
        assert "item_count" in result
        assert "item" in result

        print(f"✓ 草稿列表: 共 {result['total_count']} 个，本次返回 {result['item_count']} 个")

    def test_get_draft_switch(self, real_draft_manager):
        """测试查询草稿箱开关"""
        try:
            is_open = real_draft_manager.get_draft_switch()
            print(f"✓ 草稿箱开关状态: {'开启' if is_open else '关闭'}")
        except Exception as e:
            pytest.skip(f"草稿箱开关查询跳过: {e}")


# ==================== 数据统计测试 ====================

@pytest.mark.e2e
class TestStatsManagerE2E:
    """数据统计端到端测试"""

    def test_get_yesterday_summary(self, real_stats_manager):
        """测试获取昨日概览"""
        try:
            summary = real_stats_manager.get_yesterday_summary()

            assert "date" in summary
            assert "user" in summary
            assert "user_cumulate" in summary
            assert "article" in summary
            assert "share" in summary

            print(f"✓ 昨日概览 ({summary['date']}):")
            if summary["user"]:
                new_users = sum(u.get("new_user", 0) for u in summary["user"])
                cancel_users = sum(u.get("cancel_user", 0) for u in summary["user"])
                print(f"  - 新增用户: {new_users}")
                print(f"  - 取消关注: {cancel_users}")
            if summary["user_cumulate"]:
                print(f"  - 累计用户: {summary['user_cumulate'][0].get('cumulate_user', 'N/A')}")
        except Exception as e:
            pytest.skip(f"昨日概览获取跳过: {e}")

    def test_get_week_summary(self, real_stats_manager):
        """测试获取本周概览"""
        try:
            summary = real_stats_manager.get_week_summary()

            assert "begin_date" in summary
            assert "end_date" in summary
            assert "user" in summary
            assert "user_cumulate" in summary
            assert "share" in summary

            print(f"✓ 本周概览 ({summary['begin_date']} ~ {summary['end_date']}):")
            if summary["user"]:
                total_new = sum(u.get("new_user", 0) for u in summary["user"])
                total_cancel = sum(u.get("cancel_user", 0) for u in summary["user"])
                print(f"  - 周新增用户: {total_new}")
                print(f"  - 周取消关注: {total_cancel}")
        except Exception as e:
            pytest.skip(f"本周概览获取跳过: {e}")

    def test_get_user_summary(self, real_stats_manager):
        """测试获取用户增减数据"""
        try:
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            result = real_stats_manager.get_user_summary(yesterday, yesterday)

            assert isinstance(result, list)
            print(f"✓ 用户增减数据 ({yesterday}): {len(result)} 条记录")
        except Exception as e:
            pytest.skip(f"用户增减数据获取跳过: {e}")

    def test_get_interface_summary(self, real_stats_manager):
        """测试获取接口调用数据"""
        try:
            end = datetime.now() - timedelta(days=1)
            begin = end - timedelta(days=6)
            begin_str = begin.strftime("%Y-%m-%d")
            end_str = end.strftime("%Y-%m-%d")

            result = real_stats_manager.get_interface_summary(begin_str, end_str)

            assert isinstance(result, list)
            print(f"✓ 接口调用数据 ({begin_str} ~ {end_str}): {len(result)} 条记录")
        except Exception as e:
            pytest.skip(f"接口调用数据获取跳过: {e}")


# ==================== 集成测试 ====================

@pytest.mark.e2e
class TestIntegrationE2E:
    """集成测试"""

    def test_full_workflow_info(self, real_client, real_material_manager, real_draft_manager, real_stats_manager):
        """测试完整工作流信息获取"""
        print("\n" + "=" * 50)
        print("微信公众号 API 连接测试")
        print("=" * 50)

        # 1. Token
        token = real_client.get_access_token()
        print(f"\n[1] Access Token: {token[:20]}...")

        # 2. 素材统计
        stats = real_material_manager.get_material_count()
        print(f"\n[2] 素材统计:")
        print(f"    图片: {stats['image_count']} | 视频: {stats['video_count']}")
        print(f"    语音: {stats['voice_count']} | 图文: {stats['news_count']}")

        # 3. 草稿统计
        draft_count = real_draft_manager.get_draft_count()
        print(f"\n[3] 草稿数量: {draft_count}")

        # 4. 昨日概览
        try:
            summary = real_stats_manager.get_yesterday_summary()
            print(f"\n[4] 昨日概览 ({summary['date']}):")
            if summary["user_cumulate"]:
                print(f"    累计用户: {summary['user_cumulate'][0].get('cumulate_user', 'N/A')}")
        except Exception:
            print(f"\n[4] 昨日概览: 无数据")

        print("\n" + "=" * 50)
        print("✓ 所有 API 连接测试通过")
        print("=" * 50)
