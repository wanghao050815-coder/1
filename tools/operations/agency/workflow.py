"""代运营工作流 - 周报、月报、KPI 总结自动化"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List


class AgencyWorkflow:
    """代运营交付工作流管理

    负责生成定期的代运营交付物：
    - 周报：周度数据汇总、TOP 3 文案分析、优化建议
    - 月报：月度趋势、KPI 对标、策略建议
    - KPI 总结：目标达成情况和预警
    """

    def __init__(self, account_id: str, data_root: Path):
        self.account_id = account_id
        self.data_root = Path(data_root)
        self.account_root = self.data_root / "accounts" / account_id
        self.reports_dir = self.account_root / "代运营" / "周报"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_weekly_report(self,
                             week_start: str,
                             metrics: dict,
                             copy_count: int,
                             top_copies: List[dict],
                             pillar_distribution: dict = None) -> dict:
        """生成代运营周报

        Args:
            week_start: 周一日期 (YYYY-MM-DD)
            metrics: 本周关键指标 {followers, engagement_rate, completion_rate, ...}
            copy_count: 本周发布文案数
            top_copies: TOP 3 文案列表，每个元素包含 {title, likes, comments, shares, hook_type, cta_type, ...}
            pillar_distribution: 各内容支柱的发布数量分布

        Returns:
            周报数据结构
        """
        week_end = (datetime.fromisoformat(week_start) + timedelta(days=6)).strftime("%Y-%m-%d")
        week_number = datetime.fromisoformat(week_start).strftime("W%W")

        report = {
            "type": "weekly_report",
            "account_id": self.account_id,
            "period": {
                "week_start": week_start,
                "week_end": week_end,
                "week_number": week_number,
            },
            "summary": {
                "total_posts": copy_count,
                "engagement_rate": metrics.get("engagement_rate", 0),
                "follower_change": metrics.get("follower_change", 0),
                "estimated_reach": metrics.get("estimated_reach", 0),
                "completion_rate": metrics.get("completion_rate", 0),
            },
            "pillar_distribution": pillar_distribution or {},
            "top_3_copies": top_copies,
            "optimizations": self._generate_optimizations(metrics, top_copies, pillar_distribution),
            "generated_at": datetime.now().isoformat(),
        }

        # 保存周报
        filename = f"{week_start}-周报.json"
        filepath = self.reports_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return report

    def _generate_optimizations(self, metrics: dict, top_copies: List[dict],
                               pillar_distribution: dict = None) -> List[str]:
        """根据数据智能生成优化建议

        基于关键指标和高互动文案，生成可执行的优化建议
        """
        optimizations = []

        # 互动率优化建议
        engagement_rate = metrics.get("engagement_rate", 0)
        if engagement_rate < 0.03:
            optimizations.append("💡 互动率低于目标（目标3%），建议增加评论引导型CTA，尝试'反问梗式'钩子")

        if engagement_rate < 0.02:
            optimizations.append("⚠️ 互动率偏低，建议在视频前3秒强化价值主张，减少冗长开场")

        # 完播率优化建议
        completion_rate = metrics.get("completion_rate", 0)
        if completion_rate < 0.25:
            optimizations.append("💡 完播率低于行业平均（25%），建议缩短视频时长至60秒以内")

        # 基于高互动文案的建议
        if top_copies:
            # 识别最高互动的文案特征
            top_copy = top_copies[0]
            hook_type = top_copy.get("hook_type", "")
            cta_type = top_copy.get("cta_type", "")
            category = top_copy.get("category", "")

            if hook_type:
                optimizations.append(f"🎯 TOP 1文案采用'{hook_type}'钩子，建议下周优先使用该钩子类型")

            if cta_type:
                optimizations.append(f"📊 TOP 1文案采用'{cta_type}' CTA，转化效果最优，建议推广")

            if category:
                optimizations.append(f"📈 '{category}'类选题本周表现最优，建议下周增加该类选题比例至40%")

        # 基于内容支柱的建议
        if pillar_distribution:
            best_pillar = max(pillar_distribution, key=pillar_distribution.get) if pillar_distribution else None
            if best_pillar:
                count = pillar_distribution[best_pillar]
                optimizations.append(f"🔥 '{best_pillar}'支柱本周发布{count}条，表现稳定，建议保持该比例")

        # 粉丝增长建议
        follower_change = metrics.get("follower_change", 0)
        if follower_change < 100:
            optimizations.append("📉 粉丝增长低于预期，建议分析低效时段并调整发布频率")

        return optimizations

    def generate_monthly_report(self,
                               month: str,
                               weekly_reports: List[dict],
                               kpi_data: dict) -> dict:
        """生成代运营月报

        Args:
            month: 月份 (YYYY-MM)
            weekly_reports: 4 周的周报列表
            kpi_data: KPI 目标与实际数据 {target: {...}, actual: {...}}

        Returns:
            月报数据结构
        """
        report = {
            "type": "monthly_report",
            "account_id": self.account_id,
            "period": month,
            "trend_analysis": {
                "follower_growth": self._calc_trend(weekly_reports, "follower_change"),
                "engagement_trend": self._calc_trend(weekly_reports, "engagement_rate"),
                "completion_trend": self._calc_trend(weekly_reports, "completion_rate"),
            },
            "kpi_achievement": self._compare_kpi(kpi_data),
            "top_content_pillar": self._identify_pillar(weekly_reports),
            "weekly_summaries": weekly_reports,
            "strategic_recommendations": self._generate_monthly_recommendations(kpi_data, weekly_reports),
            "generated_at": datetime.now().isoformat(),
        }

        return report

    def _calc_trend(self, reports: List[dict], metric_key: str) -> dict:
        """计算指标趋势

        提取多周报告中的某个指标，计算平均值和趋势方向
        """
        values = []
        for r in reports:
            summary = r.get("summary", {})
            val = summary.get(metric_key, 0)
            values.append(val)

        if not values:
            return {"values": [], "avg": 0, "trend": "stable"}

        avg = sum(values) / len(values)
        trend = "up" if len(values) > 1 and values[-1] > values[0] else ("down" if len(values) > 1 else "stable")

        return {
            "values": values,
            "avg": round(avg, 4),
            "trend": trend,
        }

    def _compare_kpi(self, kpi_data: dict) -> dict:
        """对标 KPI

        比较目标和实际的KPI数据，计算达成率
        """
        target = kpi_data.get("target", {})
        actual = kpi_data.get("actual", {})

        comparisons = {}
        for key in target:
            target_val = target[key]
            actual_val = actual.get(key, 0)
            if isinstance(target_val, (int, float)) and target_val > 0:
                rate = actual_val / target_val
                status = "green" if rate >= 1.0 else ("yellow" if rate >= 0.8 else "red")
            else:
                rate = 0
                status = "unknown"

            comparisons[key] = {
                "target": target_val,
                "actual": actual_val,
                "achievement_rate": round(rate, 2),
                "status": status,
            }

        return comparisons

    def _identify_pillar(self, reports: List[dict]) -> str:
        """识别表现最好的内容支柱

        聚合所有周报的top_copies，统计各支柱出现频次
        """
        pillar_count = {}
        for report in reports:
            for copy in report.get("top_3_copies", []):
                pillar = copy.get("pillar", "unknown")
                pillar_count[pillar] = pillar_count.get(pillar, 0) + 1

        if not pillar_count:
            return "training"  # 默认

        return max(pillar_count, key=pillar_count.get)

    def _generate_monthly_recommendations(self, kpi_data: dict, weekly_reports: List[dict]) -> List[str]:
        """生成月度策略建议"""
        recommendations = []

        # 基于KPI达成情况的建议
        comparisons = self._compare_kpi(kpi_data)
        red_items = [k for k, v in comparisons.items() if v.get("status") == "red"]
        if red_items:
            recommendations.append(f"⚠️ 关键指标未达目标：{', '.join(red_items)}，下月需重点优化")

        # 基于趋势的建议
        engagement_values = self._calc_trend(weekly_reports, "engagement_rate").get("values", [])
        if len(engagement_values) > 1 and engagement_values[-1] < engagement_values[0]:
            recommendations.append("📉 互动率呈下降趋势，建议调整内容策略，增加高互动选题比例")

        followers_values = self._calc_trend(weekly_reports, "follower_change").get("values", [])
        if len(followers_values) > 1 and followers_values[-1] > followers_values[0]:
            recommendations.append("📈 粉丝增长加速，继续保持现有策略和发布频率")

        return recommendations

    def save_monthly_report(self, report: dict, month: str) -> Path:
        """保存月报到文件"""
        monthly_dir = self.account_root / "代运营" / "月报"
        monthly_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{month}-月报.json"
        filepath = monthly_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return filepath
