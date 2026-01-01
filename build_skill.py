#!/usr/bin/env python3
"""
wechat-mp-skill 打包脚本

将 skill 打包为 .skill 文件（zip 格式），用于分发和安装。

用法：
    uv run python build_skill.py
    uv run python build_skill.py --output dist/
    uv run python build_skill.py --version 0.2.0
"""

import argparse
import zipfile
import json
import re
from pathlib import Path
from datetime import datetime


# 需要包含在 .skill 包中的文件和目录
INCLUDE_PATTERNS = [
    "SKILL.md",
    "scripts/*.py",
    "references/*.md",
]

# 排除的文件模式
EXCLUDE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    ".env",
    ".wechat_token_cache.json",
]


def get_version_from_pyproject() -> str:
    """从 pyproject.toml 读取版本号"""
    pyproject_path = Path(__file__).parent / "pyproject.toml"
    if pyproject_path.exists():
        content = pyproject_path.read_text(encoding="utf-8")
        match = re.search(r'version\s*=\s*"([^"]+)"', content)
        if match:
            return match.group(1)
    return "0.1.0"


def get_skill_metadata() -> dict:
    """从 SKILL.md 读取元数据"""
    skill_path = Path(__file__).parent / "SKILL.md"
    metadata = {"name": "wechat-mp-skill", "description": ""}

    if skill_path.exists():
        content = skill_path.read_text(encoding="utf-8")
        # 解析 YAML frontmatter
        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                frontmatter = content[3:end].strip()
                for line in frontmatter.split("\n"):
                    if ":" in line:
                        key, _, value = line.partition(":")
                        key = key.strip()
                        value = value.strip()
                        if key in ("name", "description"):
                            metadata[key] = value

    return metadata


def should_exclude(path: Path) -> bool:
    """检查文件是否应该被排除"""
    path_str = str(path)
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return True
    return False


def collect_files(root: Path) -> list[tuple[Path, str]]:
    """收集需要打包的文件"""
    files = []

    for pattern in INCLUDE_PATTERNS:
        if "*" in pattern:
            # glob 模式
            for file_path in root.glob(pattern):
                if file_path.is_file() and not should_exclude(file_path):
                    arcname = str(file_path.relative_to(root))
                    files.append((file_path, arcname))
        else:
            # 精确路径
            file_path = root / pattern
            if file_path.exists() and file_path.is_file():
                files.append((file_path, pattern))

    return files


def build_skill(output_dir: Path, version: str = None) -> Path:
    """
    构建 .skill 包

    Args:
        output_dir: 输出目录
        version: 版本号（可选，默认从 pyproject.toml 读取）

    Returns:
        生成的 .skill 文件路径
    """
    root = Path(__file__).parent

    # 获取版本和元数据
    if version is None:
        version = get_version_from_pyproject()
    metadata = get_skill_metadata()

    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)

    # 生成输出文件名
    skill_name = metadata["name"]
    output_file = output_dir / f"{skill_name}-{version}.skill"

    # 收集文件
    files = collect_files(root)

    print(f"构建 {skill_name} v{version}")
    print(f"输出: {output_file}")
    print(f"包含 {len(files)} 个文件:")

    # 创建 zip 包
    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path, arcname in files:
            print(f"  + {arcname}")
            zf.write(file_path, arcname)

        # 添加 manifest.json（包元数据）
        manifest = {
            "name": skill_name,
            "version": version,
            "description": metadata["description"],
            "build_time": datetime.now().isoformat(),
            "files": [arcname for _, arcname in files],
        }
        zf.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))
        print(f"  + manifest.json")

    # 计算文件大小
    size_kb = output_file.stat().st_size / 1024
    print(f"\n构建完成! 文件大小: {size_kb:.1f} KB")

    # 同时创建不带版本号的文件（便于下载）
    latest_file = output_dir / f"{skill_name}.skill"
    if latest_file.exists():
        latest_file.unlink()
    import shutil
    shutil.copy(output_file, latest_file)
    print(f"复制到: {latest_file}")

    return output_file


def main():
    parser = argparse.ArgumentParser(
        description="构建 wechat-mp-skill .skill 包"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("dist"),
        help="输出目录 (默认: dist/)"
    )
    parser.add_argument(
        "--version", "-v",
        type=str,
        default=None,
        help="版本号 (默认从 pyproject.toml 读取)"
    )

    args = parser.parse_args()

    build_skill(args.output, args.version)


if __name__ == "__main__":
    main()
