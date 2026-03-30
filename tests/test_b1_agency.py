"""B1 代运营功能测试

测试多账号隔离、权限控制、周报生成等核心功能
"""

import pytest
from pathlib import Path
import json
from datetime import datetime

# 测试路径
TEST_DATA_ROOT = Path(__file__).parent.parent / "数据"


class TestAccountManagement:
    """账号管理测试"""

    def test_account_loading(self):
        """测试账号配置加载"""
        from tools.agents.shared.account import AccountManager

        mgr = AccountManager(TEST_DATA_ROOT)
        accounts = mgr.load_accounts()

        assert "B1" in accounts
        assert "B2" in accounts
        assert "B3" in accounts

    def test_account_types(self):
        """测试账号类型"""
        from tools.agents.shared.account import AccountManager, AccountType

        mgr = AccountManager(TEST_DATA_ROOT)

        b1 = mgr.get_account("B1")
        assert b1.type == AccountType.MASTER

        b2 = mgr.get_account("B2")
        assert b2.type == AccountType.SUB
        assert b2.master_account == "B1"

    def test_permission_control(self):
        """测试权限控制"""
        from tools.agents.shared.account import AccountManager

        mgr = AccountManager(TEST_DATA_ROOT)

        # B1 拥有全部权限
        assert mgr.has_permission("B1", "copywrite") is True
        assert mgr.has_permission("B1", "publish") is True
        assert mgr.has_permission("B1", "analytics") is True

        # B2 仅有发布权限
        assert mgr.has_permission("B2", "copywrite") is False
        assert mgr.has_permission("B2", "publish") is True
        assert mgr.has_permission("B2", "analytics") is False

    def test_account_hierarchy(self):
        """测试账号层级关系"""
        from tools.agents.shared.account import AccountManager

        mgr = AccountManager(TEST_DATA_ROOT)
        hierarchy = mgr.get_account_hierarchy("B1")

        assert hierarchy["self"].account_id == "B1"
        assert "B2" in [s.account_id for s in hierarchy["subs"]]
        assert "B3" in [s.account_id for s in hierarchy["subs"]]


class TestDataIsolation:
    """数据隔离测试"""

    def test_account_paths_isolation(self):
        """测试账号路径隔离"""
        from tools.agents.shared.multi_paths import MultiAccountPaths

        paths_b1 = MultiAccountPaths(TEST_DATA_ROOT, "B1")
        paths_b2 = MultiAccountPaths(TEST_DATA_ROOT, "B2")

        # 确认路径不同
        assert paths_b1.copy_drafts != paths_b2.copy_drafts
        assert "B1" in str(paths_b1.copy_drafts)
        assert "B2" in str(paths_b2.copy_drafts)

    def test_directory_creation(self):
        """测试目录自动创建"""
        from tools.agents.shared.multi_paths import MultiAccountPaths

        paths = MultiAccountPaths(TEST_DATA_ROOT, "B_test")
        paths.ensure_all_dirs()

        # 验证所有目录都被创建了
        assert paths.copy_drafts.exists()
        assert paths.ops_kpi.exists()
        assert paths.analytics_metrics.exists()
        assert paths.agency_weekly_reports.exists()

        # 清理测试目录
        import shutil
        if paths.account_root.exists():
            shutil.rmtree(paths.account_root)


class TestAgencyWorkflow:
    """代运营工作流测试"""

    def test_weekly_report_generation(self):
        """测试周报生成"""
        from tools.operations.agency.workflow import AgencyWorkflow

        workflow = AgencyWorkflow("B1", TEST_DATA_ROOT)

        # 准备测试数据
        metrics = {
            "followers": 185000,
            "follower_change": 8400,
            "engagement_rate": 0.052,
            "completion_rate": 0.35,
            "estimated_reach": 1750000,
        }

        top_copies = [
            {
                "title": "腹肌秘诀",
                "likes": 12500,
                "comments": 450,
                "shares": 1200,
                "hook_type": "反问梗式",
                "cta_type": "效果承诺型",
                "category": "腹肌/核心",
            }
        ]

        pillar_distribution = {"training": 4, "sect_ip": 2, "trending": 1}

        # 生成周报
        report = workflow.generate_weekly_report(
            week_start="2026-03-31",
            metrics=metrics,
            copy_count=7,
            top_copies=top_copies,
            pillar_distribution=pillar_distribution,
        )

        # 验证周报结构
        assert report["type"] == "weekly_report"
        assert report["account_id"] == "B1"
        assert report["summary"]["total_posts"] == 7
        assert report["summary"]["engagement_rate"] == 0.052
        assert len(report["optimizations"]) > 0

    def test_monthly_report_generation(self):
        """测试月报生成"""
        from tools.operations.agency.workflow import AgencyWorkflow

        workflow = AgencyWorkflow("B1", TEST_DATA_ROOT)

        # 准备测试数据（4 周周报）
        weekly_reports = []
        for i in range(4):
            weekly_reports.append({
                "summary": {
                    "follower_change": 8000 + i * 200,
                    "engagement_rate": 0.05 - i * 0.002,
                    "completion_rate": 0.35,
                }
            })

        kpi_data = {
            "target": {"followers_growth": 30000, "engagement_rate": 0.05},
            "actual": {"followers_growth": 35000, "engagement_rate": 0.048},
        }

        # 生成月报
        report = workflow.generate_monthly_report(
            month="2026-04",
            weekly_reports=weekly_reports,
            kpi_data=kpi_data,
        )

        # 验证月报结构
        assert report["type"] == "monthly_report"
        assert report["period"] == "2026-04"
        assert "trend_analysis" in report
        assert "kpi_achievement" in report
        assert "strategic_recommendations" in report


class TestAgencyAgent:
    """Agency Agent 测试"""

    def test_agent_initialization(self):
        """测试 Agent 初始化"""
        from tools.agents.agency import AgencyAgent

        # B1 Agent
        agent_b1 = AgencyAgent(account_id="B1")
        assert agent_b1.account_id == "B1"

        # B2 Agent
        agent_b2 = AgencyAgent(account_id="B2")
        assert agent_b2.account_id == "B2"

    def test_agent_system_prompt(self):
        """测试 Agent 系统提示词"""
        from tools.agents.agency import AgencyAgent

        agent = AgencyAgent(account_id="B1")
        prompt = agent._build_system_prompt()

        # 验证提示词包含关键信息
        assert "邪修宗" in prompt
        assert "代运营" in prompt
        assert "周报" in prompt
        assert "月报" in prompt


class TestBackwardCompatibility:
    """向下兼容性测试"""

    def test_single_account_mode(self):
        """测试单账号模式兼容"""
        from tools.agents.agency import AgencyAgent

        # 不指定 account_id，应该默认使用 B1
        agent = AgencyAgent()
        assert agent.account_id == "B1"

    def test_default_account_paths(self):
        """测试默认账号路径"""
        from tools.agents.base import BaseAgent

        agent = BaseAgent()
        # 默认应该是 B1
        assert "B1" in str(agent.account_copy_drafts)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
