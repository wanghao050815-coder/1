"""B2 分析部门功能测试

测试指标计算、洞察生成、报告生成等核心功能
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta

TEST_DATA_ROOT = Path(__file__).parent.parent / "数据"


class TestMetricsCalculator:
    """指标计算器测试"""

    def test_health_score_calculation(self):
        """测试健康度评分计算"""
        from tools.analytics.metrics_engine import MetricsCalculator, MetricsSnapshot

        calculator = MetricsCalculator(TEST_DATA_ROOT, "B1")
        snapshot = MetricsSnapshot(
            timestamp=datetime.now().isoformat(),
            followers=185000,
            follower_change=1200,
            engagement_rate=0.052,
            completion_rate=0.35,
            comment_rate=0.012,
            share_rate=0.008,
            save_rate=0.015,
        )

        health = calculator.calculate_health_score(snapshot)

        # 验证评分结构
        assert "health_score" in health
        assert 0 <= health["health_score"] <= 100
        assert "components" in health
        assert health["status"] in ["excellent", "good", "fair", "poor"]

    def test_anomaly_detection(self):
        """测试异常检测"""
        from tools.analytics.metrics_engine import MetricsCalculator, MetricsSnapshot

        calculator = MetricsCalculator(TEST_DATA_ROOT, "B1")

        # 创建历史数据
        historical = []
        for i in range(10):
            snapshot = MetricsSnapshot(
                timestamp=(datetime.now() - timedelta(days=i)).isoformat(),
                followers=180000 + i * 500,
                follower_change=500,
                engagement_rate=0.05,
                completion_rate=0.35,
                comment_rate=0.01,
                share_rate=0.008,
                save_rate=0.012,
            )
            historical.append(snapshot)

        # 创建异常数据（2倍增长）
        current = MetricsSnapshot(
            timestamp=datetime.now().isoformat(),
            followers=185000,
            follower_change=1000,  # 异常：2倍正常值
            engagement_rate=0.05,
            completion_rate=0.35,
            comment_rate=0.01,
            share_rate=0.008,
            save_rate=0.012,
        )

        anomalies = calculator.detect_anomalies(current, historical)
        # 应该检测到粉丝变化异常
        assert any(a["metric"] == "粉丝变化" for a in anomalies)

    def test_content_effectiveness(self):
        """测试内容有效性评分"""
        from tools.analytics.metrics_engine import MetricsCalculator

        calculator = MetricsCalculator(TEST_DATA_ROOT, "B1")

        effectiveness = calculator.calculate_content_effectiveness({
            "views": 250000,
            "likes": 12500,
            "comments": 450,
            "shares": 1200,
            "hook_type": "反问梗式",
            "cta_type": "效果承诺型",
        })

        assert 0 <= effectiveness["effectiveness_score"] <= 100
        assert "engagement_index" in effectiveness


class TestInsightsEngine:
    """洞察生成引擎测试"""

    def test_pattern_identification(self):
        """测试高互动模式识别"""
        from tools.analytics.insights_engine import InsightsEngine

        insights = InsightsEngine(TEST_DATA_ROOT, "B1")

        top_copies = [
            {"hook_type": "反问梗式", "cta_type": "效果承诺型", "category": "腹肌/核心", "likes": 12500},
            {"hook_type": "反问梗式", "cta_type": "效果承诺型", "category": "腹肌/核心", "likes": 11200},
            {"hook_type": "感叹堆积式", "cta_type": "行动鼓励型", "category": "背部训练", "likes": 8900},
        ]

        patterns = insights.identify_high_engagement_patterns(top_copies)

        assert "top_hook_types" in patterns
        assert "top_cta_types" in patterns
        assert "top_categories" in patterns
        assert patterns["top_hook_types"][0][0] == "反问梗式"

    def test_suggestions_generation(self):
        """测试优化建议生成"""
        from tools.analytics.insights_engine import InsightsEngine

        insights = InsightsEngine(TEST_DATA_ROOT, "B1")

        current = {"engagement_rate": 0.03, "completion_rate": 0.25}
        target = {"engagement_rate": 0.05, "completion_rate": 0.35}
        patterns = {
            "top_hook_types": [("反问梗式", 5)],
            "top_cta_types": [("效果承诺型", 4)],
            "top_categories": [("腹肌/核心", 6)],
        }

        suggestions = insights.generate_optimization_suggestions(current, target, patterns)

        # 应该生成多条建议
        assert len(suggestions) > 0
        assert all(isinstance(s, str) for s in suggestions)

    def test_forecasting(self):
        """测试趋势预测"""
        from tools.analytics.insights_engine import InsightsEngine

        insights = InsightsEngine(TEST_DATA_ROOT, "B1")

        historical = [
            {"timestamp": (datetime.now() - timedelta(days=i)).isoformat(), "followers": 180000 + i * 500}
            for i in range(10)
        ]

        forecast = insights.forecast_metrics(historical, days_ahead=7)

        assert "forecast_model" in forecast
        assert "forecast_points" in forecast
        assert len(forecast["forecast_points"]) == 7


class TestReportGenerator:
    """报告生成器测试"""

    def test_weekly_report_generation(self):
        """测试周报生成"""
        from tools.analytics.report_generator import ReportGenerator

        report_gen = ReportGenerator(TEST_DATA_ROOT, "B1")

        metrics = {
            "follower_change": 8400,
            "engagement_rate": 0.052,
            "completion_rate": 0.35,
            "post_count": 7,
            "pillar_distribution": {"training": 4, "sect_ip": 2, "trending": 1},
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

        insights = {
            "patterns": {"top_hook_types": [("反问梗式", 5)]},
            "suggestions": ["建议增加反问梗式钩子"],
        }

        report = report_gen.generate_weekly_report(
            week_start="2026-03-31",
            metrics=metrics,
            top_copies=top_copies,
            insights=insights,
        )

        # 验证报告内容
        assert "周报" in report
        assert "核心指标" in report
        assert "TOP 3" in report or "top_copies" in report


class TestAnalyticsAgent:
    """Analytics Agent 测试"""

    def test_agent_initialization(self):
        """测试 Agent 初始化"""
        from tools.agents.analytics import AnalyticsAgent

        agent_b1 = AnalyticsAgent(account_id="B1")
        assert agent_b1.account_id == "B1"
        assert hasattr(agent_b1, "metrics_calc")
        assert hasattr(agent_b1, "insights_gen")
        assert hasattr(agent_b1, "report_gen")

    def test_agent_methods(self):
        """测试 Agent 新增方法"""
        from tools.agents.analytics import AnalyticsAgent

        agent = AnalyticsAgent(account_id="B1")

        # 验证新方法存在
        assert hasattr(agent, "comprehensive_analysis")
        assert hasattr(agent, "health_diagnosis")
        assert hasattr(agent, "forecasting_analysis")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
