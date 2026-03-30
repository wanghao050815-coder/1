"""多账号数据路径管理 - 物理隔离策略

为不同账号隔离数据存储路径，确保数据安全性和独立性。
"""

from pathlib import Path


class MultiAccountPaths:
    """管理多账号的数据隔离路径

    采用物理隔离策略：
    /数据/accounts/{account_id}/
    ├── 文案/
    │   ├── 草稿/
    │   ├── 已发布/
    │   ├── 归档/
    │   ├── 金句库/
    │   └── 素材库/
    ├── 运营/
    │   ├── KPI/
    │   └── 排期/
    ├── 分析/
    │   ├── 指标/
    │   ├── 报告/
    │   └── 洞察/
    └── 代运营/
        ├── 交付物/
        └── 周报/
    """

    def __init__(self, data_root: Path, account_id: str):
        self.data_root = Path(data_root)
        self.account_id = account_id
        self.account_root = self.data_root / "accounts" / account_id

    # ── 文案数据路径 ──────────────────────────────────

    @property
    def copy_drafts(self) -> Path:
        """文案草稿目录"""
        return self.account_root / "文案" / "草稿"

    @property
    def copy_published(self) -> Path:
        """已发布文案目录"""
        return self.account_root / "文案" / "已发布"

    @property
    def copy_archive(self) -> Path:
        """文案归档目录"""
        return self.account_root / "文案" / "归档"

    @property
    def copy_golden(self) -> Path:
        """金句库目录"""
        return self.account_root / "文案" / "金句库"

    @property
    def copy_library(self) -> Path:
        """素材库目录"""
        return self.account_root / "文案" / "素材库"

    # ── 运营数据路径 ──────────────────────────────────

    @property
    def ops_kpi(self) -> Path:
        """KPI 追踪目录"""
        return self.account_root / "运营" / "KPI"

    @property
    def ops_schedule(self) -> Path:
        """发布排期目录"""
        return self.account_root / "运营" / "排期"

    # ── 分析数据路径 ──────────────────────────────────

    @property
    def analytics_metrics(self) -> Path:
        """指标数据目录"""
        return self.account_root / "分析" / "指标"

    @property
    def analytics_reports(self) -> Path:
        """报告输出目录"""
        return self.account_root / "分析" / "报告"

    @property
    def analytics_insights(self) -> Path:
        """洞察数据目录"""
        return self.account_root / "分析" / "洞察"

    # ── 代运营工作流路径 ────────────────────────────

    @property
    def agency_deliverables(self) -> Path:
        """交付物目录"""
        return self.account_root / "代运营" / "交付物"

    @property
    def agency_weekly_reports(self) -> Path:
        """周报目录"""
        return self.account_root / "代运营" / "周报"

    @property
    def agency_monthly_reports(self) -> Path:
        """月报目录"""
        return self.account_root / "代运营" / "月报"

    # ── 批量操作 ──────────────────────────────────────

    def ensure_all_dirs(self) -> None:
        """创建所有必要的目录"""
        paths = [
            self.copy_drafts, self.copy_published, self.copy_archive, self.copy_golden, self.copy_library,
            self.ops_kpi, self.ops_schedule,
            self.analytics_metrics, self.analytics_reports, self.analytics_insights,
            self.agency_deliverables, self.agency_weekly_reports, self.agency_monthly_reports,
        ]
        for path in paths:
            path.mkdir(parents=True, exist_ok=True)

    def get_all_paths(self) -> dict:
        """获取所有路径的字典表示"""
        return {
            "account_root": str(self.account_root),
            "copy": {
                "drafts": str(self.copy_drafts),
                "published": str(self.copy_published),
                "archive": str(self.copy_archive),
                "golden": str(self.copy_golden),
                "library": str(self.copy_library),
            },
            "ops": {
                "kpi": str(self.ops_kpi),
                "schedule": str(self.ops_schedule),
            },
            "analytics": {
                "metrics": str(self.analytics_metrics),
                "reports": str(self.analytics_reports),
                "insights": str(self.analytics_insights),
            },
            "agency": {
                "deliverables": str(self.agency_deliverables),
                "weekly_reports": str(self.agency_weekly_reports),
                "monthly_reports": str(self.agency_monthly_reports),
            },
        }

    @staticmethod
    def setup_account_directories(data_root: Path, account_id: str) -> "MultiAccountPaths":
        """工厂方法：创建账号目录并返回路径管理对象"""
        paths = MultiAccountPaths(data_root, account_id)
        paths.ensure_all_dirs()
        return paths
