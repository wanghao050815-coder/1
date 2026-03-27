"""Agent 全局配置"""

import os
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent

# 品牌文档路径
BRAND_DOCS = {
    "brand_voice": ROOT_DIR / "docs" / "brand" / "brand-voice-guide.md",
    "content_pillars": ROOT_DIR / "docs" / "brand" / "content-pillars.md",
    "super_ip": ROOT_DIR / "docs" / "brand" / "super-ip.md",
    "visual_identity": ROOT_DIR / "docs" / "brand" / "visual-identity.md",
    "copywriting_sop": ROOT_DIR / "docs" / "copywriting" / "copywriting-sop.md",
    "douyin_playbook": ROOT_DIR / "docs" / "platforms" / "douyin-playbook.md",
}

# 数据目录
DATA_DIR = ROOT_DIR / "data"
COPYWRITING_DIR = DATA_DIR / "copywriting"
LIBRARY_DIR = COPYWRITING_DIR / "library"
DRAFTS_DIR = COPYWRITING_DIR / "drafts"

# 平台配置
PLATFORMS_CONFIG = ROOT_DIR / "tools" / "config" / "platforms.yaml"

# Anthropic API
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# 平台中文名
PLATFORM_NAMES = {
    "douyin": "抖音",
    "xiaohongshu": "小红书",
    "weibo": "微博",
    "bilibili": "B站",
    "wechat": "微信公众号",
}

ALL_PLATFORMS = list(PLATFORM_NAMES.keys())
