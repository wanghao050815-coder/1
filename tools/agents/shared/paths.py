"""统一的路径管理 — 所有 Agent 共享的路径常量。"""

from pathlib import Path

# 项目根目录
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# 数据目录
DATA_ROOT = REPO_ROOT / "数据"
COPY_DATA_DIR = DATA_ROOT / "文案"
COPY_DRAFTS_DIR = COPY_DATA_DIR / "草稿"
COPY_PUBLISHED_DIR = COPY_DATA_DIR / "已发布"
COPY_ARCHIVE_DIR = COPY_DATA_DIR / "归档"
COPY_GOLDEN_DIR = COPY_DATA_DIR / "金句库"
COPY_LIBRARY_DIR = COPY_DATA_DIR / "素材库"
COPY_RAW_DIR = COPY_DATA_DIR / "原始投喂"
STYLE_DNA_PATH = COPY_DATA_DIR / "风格DNA.md"

# 运营数据
OPS_DATA_DIR = DATA_ROOT / "运营"
OPS_KPI_DIR = OPS_DATA_DIR / "KPI"
OPS_SCHEDULE_DIR = OPS_DATA_DIR / "排期"

# 内容日历
CALENDAR_DIR = DATA_ROOT / "内容日历"

# 文档目录
DOCS_ROOT = REPO_ROOT / "文档"
BRAND_DOCS_DIR = DOCS_ROOT / "品牌"
COPY_DOCS_DIR = DOCS_ROOT / "文案"
PLATFORM_DOCS_DIR = DOCS_ROOT / "平台"

# 配置目录
CONFIG_DIR = REPO_ROOT / "tools" / "配置"

# 工具目录
TOOLS_ROOT = REPO_ROOT / "tools"


def ensure_dirs():
    """确保所有必要目录存在。"""
    for d in [
        COPY_DRAFTS_DIR, COPY_PUBLISHED_DIR, COPY_ARCHIVE_DIR,
        COPY_GOLDEN_DIR, COPY_LIBRARY_DIR,
        OPS_KPI_DIR, OPS_SCHEDULE_DIR,
        CALENDAR_DIR,
    ]:
        d.mkdir(parents=True, exist_ok=True)
