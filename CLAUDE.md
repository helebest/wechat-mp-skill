# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**WeChat MP Skill | 微信公众号技能** - A Claude Code skill for managing WeChat Official Accounts. Provides Python modules for interacting with the WeChat MP API to manage materials (素材), drafts (草稿), and statistics (数据统计).

## Configuration

Credentials are required: `WECHAT_APPID` and `WECHAT_APPSECRET`. Set via:
1. Constructor parameters (highest priority)
2. Environment variables
3. `.env` file in project root (recommended)

The client auto-manages access_token caching (`.wechat_token_cache.json`) with 5-minute expiry buffer.

## Architecture

```
scripts/
├── wechat_client.py     # Core API client - handles auth, requests, token management
├── material_manager.py  # Permanent/temporary media: images, voice, video
├── draft_manager.py     # Draft CRUD, publishing workflow
├── stats_manager.py     # Analytics: user growth, article reads, messages
├── html_submitter.py    # High-level HTML submission: auto image upload & draft creation
└── __init__.py          # Exports all managers and convenience functions
```

**Module Pattern**: Each manager takes a `WeChatClient` instance. Convenience functions (`create_*_manager()`) auto-create clients.

```python
from scripts import WeChatClient, MaterialManager, DraftManager, StatsManager

client = WeChatClient()
mm = MaterialManager(client)
dm = DraftManager(client)
sm = StatsManager(client)
```

## Key API Constraints

- **Materials**: Images 10MB/100k limit, voice 2MB/1k, video 10MB/1k, thumb 64KB
- **Articles**: Title ≤64 chars, author ≤8 chars, digest ≤128 chars, content <1MB/<20k chars
- **Stats**: Only historical data (yesterday or earlier). User/share max 7 days, article max 1 day, interface max 30 days
- **Publishing Permission**: All `freepublish/*` APIs require WeChat-verified account (认证公众号). Unverified accounts will get error 48001.
- **Stats Permission**: All `datacube/*` APIs require verification. Unverified accounts cannot access statistics.
- **Article images in content**: Must use `upload_article_image()` which returns URL, not `upload_permanent()` which returns media_id

## Publishing Workflow

1. Upload cover image → get `media_id`
2. Upload content images → get URLs
3. Create draft with article(s) → get `draft_media_id`
4. Publish draft → get `publish_id`
5. Check publish status via `publish_id`

## Development Commands

Package management uses **uv**. All Python scripts should be executed via `uv run`.

```bash
# Install dependencies
uv sync                    # Runtime only
uv sync --all-extras       # Include dev dependencies

# Run tests
uv run pytest tests/ -v -m unit           # Unit tests (mocked)
uv run pytest tests/test_e2e.py -v -m e2e # E2E tests (requires credentials)
uv run pytest tests/ --cov=scripts        # With coverage

# Run a script directly
uv run python scripts/wechat_client.py
```

## Reference Documentation

- `references/api_reference.md` - WeChat API endpoints and parameters
- `references/article_format.md` - Article HTML formatting guidelines
- `references/stats_reference.md` - Statistics API details and date range limits
- `references/error_codes.md` - WeChat API error codes

## Development Guidelines

When adding new features that call WeChat server APIs:

1. **Test API permission requirements** - Verify if the API requires a verified account (认证公众号)
2. **Document in SKILL.md** - Update the "权限要求" table with the new API's permission status
3. **Handle 48001 errors** - APIs requiring verification return error code 48001 for unverified accounts

Current permission status:
- ✅ No verification needed: `material/*`, `media/*`, `draft/*`
- ❌ Verification required: `freepublish/*`, `datacube/*`

## Release Guidelines

- **GitHub Release title format**: `wechat-mp-skill vx.y.z` (e.g., `wechat-mp-skill v0.1.0`)
- **Tag format**: `vx.y.z` (e.g., `v0.1.0`)
