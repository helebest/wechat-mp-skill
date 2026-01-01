# Changelog

本文档记录 wechat-mp-skill (微信公众号技能) 的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.1.0] - 2026-01-01

### 新增

#### 核心功能
- **WeChatClient** - 微信公众号 API 客户端
  - access_token 自动获取和缓存管理
  - 支持环境变量、.env 文件、参数传入三种配置方式
  - 自动处理 token 过期和刷新
  - GET/POST 请求封装
  - 文件上传/下载支持

- **MaterialManager** - 素材管理模块
  - 永久素材：上传、获取、删除、列表、统计
  - 临时素材：上传、获取（3天有效期）
  - 图文内图片上传（返回 URL）
  - 高清语音素材获取

- **DraftManager** - 草稿管理模块
  - 草稿 CRUD 操作
  - 草稿列表和数量查询
  - 草稿发布和状态查询
  - 已发布文章管理

- **StatsManager** - 数据统计模块
  - 用户增减和累计数据
  - 图文阅读、分享数据
  - 消息发送数据
  - 接口调用数据
  - 便捷方法：昨日概览、本周概览

#### 开发工具
- **uv 包管理** - 使用 uv 进行依赖管理和脚本执行
- **pytest 测试框架** - 单元测试和端到端测试支持
- **测试覆盖率** - pytest-cov 集成
- **打包脚本** - `build_skill.py` 生成 `.skill` 分发包
- **GitHub Actions CI** - 自动测试和发布工作流

### 文件结构

```
wechat-mp-skill/
├── scripts/                    # 核心模块
│   ├── __init__.py
│   ├── wechat_client.py       # API 客户端
│   ├── material_manager.py    # 素材管理
│   ├── draft_manager.py       # 草稿管理
│   └── stats_manager.py       # 数据统计
├── tests/                      # 测试文件
│   ├── __init__.py
│   ├── conftest.py            # pytest 配置和 fixtures
│   ├── test_wechat_client.py  # 客户端单元测试
│   ├── test_material_manager.py
│   ├── test_draft_manager.py
│   ├── test_stats_manager.py
│   └── test_e2e.py            # 端到端测试
├── references/                 # API 参考文档
│   ├── api_reference.md
│   ├── article_format.md
│   ├── stats_reference.md
│   └── error_codes.md
├── .github/workflows/          # CI/CD 配置
│   ├── ci.yml                 # 持续集成（测试）
│   └── release.yml            # 发布工作流
├── pyproject.toml             # 项目配置和依赖
├── build_skill.py             # 打包脚本
├── CLAUDE.md                  # Claude Code 指南
├── SKILL.md                   # Skill 定义文件
├── README.md                  # 项目说明
└── CHANGELOG.md               # 变更日志
```

### 依赖

**运行时依赖：**
- requests >= 2.28.0
- python-dotenv >= 1.0.0

**开发依赖：**
- pytest >= 8.0.0
- pytest-mock >= 3.12.0
- pytest-cov >= 4.1.0
- responses >= 0.25.0

---

## 使用说明

### 安装依赖

```bash
# 安装运行时依赖
uv sync

# 安装开发依赖
uv sync --all-extras
```

### 运行测试

```bash
# 运行所有单元测试
uv run pytest tests/ -v -m unit

# 运行端到端测试（需要配置凭证）
uv run pytest tests/test_e2e.py -v -m e2e

# 运行测试并生成覆盖率报告
uv run pytest tests/ --cov=scripts --cov-report=html
```

### 配置凭证

创建 `.env` 文件：

```
WECHAT_APPID=your_appid
WECHAT_APPSECRET=your_appsecret
```
