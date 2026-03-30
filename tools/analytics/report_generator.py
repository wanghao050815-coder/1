"""报告生成系统 - 周报、月报、专题报告

将原始数据和洞察转化为专业的 Markdown 和 HTML 报告。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict


class ReportGenerator:
    """生成各类分析报告

    支持多种格式：
    - 周报（Markdown）
    - 月报（Markdown）
    - HTML 版本（可选）
    """

    def __init__(self, data_root: Path, account_id: str):
        self.data_root = Path(data_root)
        self.account_id = account_id
        self.reports_dir = data_root / "accounts" / account_id / "分析" / "报告"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_weekly_report(self,
                             week_start: str,
                             metrics: dict,
                             top_copies: List[dict],
                             insights: dict) -> str:
        """生成周报 Markdown

        Args:
            week_start: 周一日期 (YYYY-MM-DD)
            metrics: 本周关键指标
            top_copies: TOP 3 文案列表
            insights: 洞察数据

        Returns:
            Markdown 格式的周报
        """
        from datetime import datetime, timedelta

        # 计算周日期
        start_date = datetime.fromisoformat(week_start)
        end_date = start_date + timedelta(days=6)
        week_num = start_date.strftime("W%W")

        report = f"""# {self.account_id} 周报 — {week_start} ~ {end_date.strftime('%Y-%m-%d')}

> 周期：{week_num} | 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 核心指标

| 指标 | 本周 | 目标 | 达成率 | 评价 |
|------|------|------|--------|------|
| 粉丝增长 | {metrics.get('follower_change', 0):,} | 5,000 | {round(metrics.get('follower_change', 0) / 5000 * 100, 1)}% | {'✅' if metrics.get('follower_change', 0) >= 5000 else '⚠️'} |
| 互动率 | {metrics.get('engagement_rate', 0)*100:.2f}% | 5.0% | {round(metrics.get('engagement_rate', 0) / 0.05 * 100, 1)}% | {'✅' if metrics.get('engagement_rate', 0) >= 0.05 else '⚠️'} |
| 完播率 | {metrics.get('completion_rate', 0)*100:.1f}% | 35.0% | {round(metrics.get('completion_rate', 0) / 0.35 * 100, 1)}% | {'✅' if metrics.get('completion_rate', 0) >= 0.35 else '⚠️'} |
| 评论率 | {metrics.get('comment_rate', 0)*100:.2f}% | 1.5% | {round(metrics.get('comment_rate', 0) / 0.015 * 100, 1)}% | {'✅' if metrics.get('comment_rate', 0) >= 0.015 else '⚠️'} |

## 🎬 发布统计

- **本周发布**：{metrics.get('post_count', 0)} 条
- **平均完播**：{metrics.get('avg_completion', 0)*100:.1f}%
- **平均互动**：{metrics.get('avg_engagement', 0):,.0f} 次

### 内容支柱分布

```
"""
        pillar_dist = metrics.get("pillar_distribution", {})
        for pillar, count in sorted(pillar_dist.items(), key=lambda x: x[1], reverse=True):
            pct = round(count / metrics.get('post_count', 1) * 100)
            bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
            report += f"{pillar:15} {bar} {pct}% ({count}条)\n"

        report += f"""
```

## ⭐ TOP 3 高互动文案

"""
        for i, copy in enumerate(top_copies[:3], 1):
            report += f"""### {i}. {copy.get('title', '无标题')}

- **互动数据**：{copy.get('likes', 0):,} 赞 | {copy.get('comments', 0):,} 评 | {copy.get('shares', 0):,} 转
- **钩子类型**：{copy.get('hook_type', '未标记')}
- **CTA 类型**：{copy.get('cta_type', '未标记')}
- **内容类别**：{copy.get('category', '未分类')}
- **内容支柱**：{copy.get('pillar', '未分类')}

"""

        report += f"""## 💡 关键洞察

"""
        patterns = insights.get("patterns", {})
        if patterns:
            top_hooks = patterns.get("top_hook_types", [])
            top_cta = patterns.get("top_cta_types", [])
            if top_hooks:
                report += f"- **高频钩子**：'{top_hooks[0][0]}'（出现 {top_hooks[0][1]} 次）\n"
            if top_cta:
                report += f"- **高效 CTA**：'{top_cta[0][0]}'（平均互动最高）\n"

        report += f"""
## 🚀 优化建议

"""
        suggestions = insights.get("suggestions", [])
        for j, suggestion in enumerate(suggestions[:5], 1):
            report += f"{j}. {suggestion}\n"

        report += f"""
---

**报告生成时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**账号**：{self.account_id}
"""
        return report

    def generate_monthly_report(self,
                              month: str,
                              weekly_summaries: List[str],
                              kpi_data: dict,
                              trends: dict) -> str:
        """生成月报 Markdown

        Args:
            month: 月份 (YYYY-MM)
            weekly_summaries: 4 周周报摘要
            kpi_data: KPI 达成情况
            trends: 趋势数据

        Returns:
            Markdown 格式的月报
        """
        report = f"""# {self.account_id} 月报 — {month}

> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📈 趋势分析

### 粉丝增长趋势
"""
        trend_followers = trends.get("follower_trend", [])
        if trend_followers:
            for week, value in enumerate(trend_followers, 1):
                bar = "█" * min(value // 2000, 20)
                report += f"**W{week}**：{bar} {value:,}\n"

        report += f"""
### 互动率趋势
"""
        trend_engagement = trends.get("engagement_trend", [])
        if trend_engagement:
            for week, value in enumerate(trend_engagement, 1):
                pct = round(value * 100, 2)
                bar = "█" * int(pct // 0.5)
                report += f"**W{week}**：{bar} {pct}%\n"

        report += f"""
## 🎯 KPI 对标分析

"""
        kpi = kpi_data.get("kpi_achievement", {})
        for metric, data in kpi.items():
            target = data.get("target", 0)
            actual = data.get("actual", 0)
            rate = data.get("achievement_rate", 0)
            status = data.get("status", "unknown")
            emoji = "🟢" if status == "green" else ("🟡" if status == "yellow" else "🔴")

            report += f"- **{metric}**：{emoji} {actual:,} / {target:,} ({rate*100:.1f}%)\n"

        report += f"""
## 📊 内容表现分析

"""
        report += f"""
## 💬 用户反馈和互动热点

- 高互动评论主要围绕：动作细节、效果验证、个人故事
- 优化方向：增加对用户评论的回复，强化社区互动

## 🎬 下月策略建议

1. **内容调整**：基于本月数据，重点突出表现最好的 2 个支柱
2. **发布频率**：优化发布时段，集中在用户活跃高峰期
3. **钩子策略**：优先采用本月表现最好的钩子类型
4. **互动引导**：增加 CTA 的多样性，提升评论和分享

---

**报告生成**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**数据周期**：{month}
**账号**：{self.account_id}
"""
        return report

    def save_report(self, report_content: str, report_type: str, date_key: str) -> Path:
        """保存报告到文件

        Args:
            report_content: 报告内容
            report_type: 报告类型 (weekly/monthly)
            date_key: 日期键 (YYYY-MM-DD 或 YYYY-MM)

        Returns:
            保存的文件路径
        """
        filename = f"{date_key}-{report_type}-report.md"
        filepath = self.reports_dir / filename
        filepath.write_text(report_content, encoding="utf-8")
        return filepath
