"""智能洞察生成 - 从数据中提取可执行的优化建议"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter
from typing import List, Dict, Tuple


class InsightsEngine:
    """从数据中生成智能洞察

    主要功能：
    - 高互动模式识别（聚类分析）
    - 可执行优化建议生成
    - 趋势预测（线性回归）
    - 相关性分析
    """

    def __init__(self, data_root: Path, account_id: str):
        self.data_root = Path(data_root)
        self.account_id = account_id
        self.insights_dir = data_root / "accounts" / account_id / "分析" / "洞察"
        self.insights_dir.mkdir(parents=True, exist_ok=True)

    def identify_high_engagement_patterns(self,
                                         top_copies: List[dict],
                                         min_count: int = 2) -> dict:
        """识别高互动文案的共同特征

        通过聚类分析，识别高赞文案的共同点：
        - 高频钩子类型
        - 高频 CTA 类型
        - 高频选题关键词
        - 最优发布时间

        Args:
            top_copies: 高互动文案列表（应该是 TOP 10-20）
            min_count: 最少出现次数才算高频

        Returns:
            高互动模式分析结果
        """
        if not top_copies:
            return {}

        # 统计各维度的频率
        hook_types = Counter(c.get("hook_type") for c in top_copies if c.get("hook_type"))
        cta_types = Counter(c.get("cta_type") for c in top_copies if c.get("cta_type"))
        categories = Counter(c.get("category") for c in top_copies if c.get("category"))
        pillars = Counter(c.get("pillar") for c in top_copies if c.get("pillar"))

        # 计算平均互动数
        avg_likes = sum(c.get("likes", 0) for c in top_copies) / len(top_copies) if top_copies else 0
        avg_engagement = sum(c.get("engagement_rate", 0) for c in top_copies) / len(top_copies) if top_copies else 0

        return {
            "total_analyzed": len(top_copies),
            "top_hook_types": hook_types.most_common(3),
            "top_cta_types": cta_types.most_common(3),
            "top_categories": categories.most_common(3),
            "top_pillars": pillars.most_common(3),
            "average_engagement": {
                "likes": round(avg_likes, 0),
                "engagement_rate": round(avg_engagement, 4),
            },
        }

    def generate_optimization_suggestions(self,
                                         current_metrics: dict,
                                         target_metrics: dict,
                                         patterns: dict) -> List[str]:
        """生成基于数据的可执行优化建议

        Args:
            current_metrics: 当前指标
            target_metrics: 目标指标
            patterns: 高互动模式

        Returns:
            优化建议列表（按优先级排序）
        """
        suggestions = []

        # 1. 互动率优化
        current_engagement = current_metrics.get("engagement_rate", 0)
        target_engagement = target_metrics.get("engagement_rate", 0.05)

        if current_engagement < target_engagement * 0.9:
            top_hook = patterns.get("top_hook_types", [("", 0)])[0][0]
            if top_hook:
                suggestions.append(
                    f"💡 互动率低于目标，建议增加'{top_hook}'类型钩子，"
                    f"历史数据显示该钩子互动率最高"
                )
            else:
                suggestions.append("💡 互动率低于目标，建议尝试'反问梗式'钩子")

        # 2. 完播率优化
        completion_rate = current_metrics.get("completion_rate", 0)
        if completion_rate < 0.25:
            suggestions.append("📹 完播率低于行业平均（25%），建议缩短视频至60秒以内")

        # 3. 基于高互动选题的建议
        top_categories = patterns.get("top_categories", [])
        if top_categories:
            top_category, count = top_categories[0]
            suggestions.append(
                f"🎯 '{top_category}'类选题表现最优（高频出现），"
                f"建议下周增加该类选题比例至40%"
            )

        # 4. 基于内容支柱的建议
        top_pillars = patterns.get("top_pillars", [])
        if top_pillars:
            top_pillar, count = top_pillars[0]
            suggestions.append(
                f"📊 '{top_pillar}'支柱内容表现稳定，建议保持该支柱在35%以上"
            )

        # 5. CTA 优化
        top_cta = patterns.get("top_cta_types", [("", 0)])[0][0]
        if top_cta:
            suggestions.append(
                f"✍️ TOP 文案采用'{top_cta}' CTA，转化效果最优，建议优先推广"
            )

        # 6. 粉丝增长建议
        follower_change = current_metrics.get("follower_change", 0)
        if follower_change < 100:
            suggestions.append(
                "📉 粉丝增长低于预期，建议分析低效时段并优化发布频率"
            )

        # 7. 评论率建议
        comment_rate = current_metrics.get("comment_rate", 0)
        if comment_rate < 0.01:
            suggestions.append(
                "💬 评论率偏低，建议增加评论引导型CTA，如'评论你的看法'"
            )

        return suggestions[:5]  # 返回 TOP 5 建议

    def forecast_metrics(self, historical_data: List[dict],
                        days_ahead: int = 7) -> dict:
        """简单的趋势预测（基于线性回归）

        使用历史数据拟合线性趋势，预测未来 N 天

        Args:
            historical_data: 历史数据列表
                [{timestamp, followers, engagement_rate, ...}, ...]
            days_ahead: 预测天数

        Returns:
            预测结果
        """
        if len(historical_data) < 3:
            return {"forecast": "数据不足，无法预测", "forecast_points": []}

        # 提取粉丝数据和时间
        followers_data = []
        timestamps = []

        for i, d in enumerate(historical_data):
            followers_data.append(d.get("followers", 0))
            timestamps.append(d.get("timestamp", ""))

        if not followers_data:
            return {"forecast": "无有效数据", "forecast_points": []}

        # 线性回归计算
        x = list(range(len(followers_data)))  # 时间序列
        y = followers_data                      # 粉丝数

        # 计算斜率和截距
        mean_x = sum(x) / len(x)
        mean_y = sum(y) / len(y)

        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x)))
        denominator = sum((x[i] - mean_x) ** 2 for i in range(len(x)))

        if denominator == 0:
            slope = 0
        else:
            slope = numerator / denominator

        intercept = mean_y - slope * mean_x

        # 预测未来 N 天
        last_timestamp = datetime.fromisoformat(timestamps[-1]) if timestamps else datetime.now()
        forecast_points = []

        for i in range(1, days_ahead + 1):
            x_future = len(followers_data) - 1 + i
            y_forecast = intercept + slope * x_future
            forecast_date = last_timestamp + timedelta(days=i)

            forecast_points.append({
                "date": forecast_date.isoformat()[:10],
                "projected_followers": max(0, int(y_forecast)),
            })

        return {
            "forecast_model": "linear_regression",
            "daily_growth_rate": round(slope, 2),
            "confidence": "medium",  # 简单模型，中等信心
            "forecast_points": forecast_points,
        }

    def analyze_pillar_effectiveness(self, content_data: List[dict]) -> dict:
        """分析各内容支柱的有效性

        Args:
            content_data: 内容列表，包含pillar、likes、comments等字段

        Returns:
            各支柱的有效性排名
        """
        pillar_stats = {}

        for content in content_data:
            pillar = content.get("pillar", "unknown")
            if pillar not in pillar_stats:
                pillar_stats[pillar] = {
                    "count": 0,
                    "total_likes": 0,
                    "total_comments": 0,
                    "total_shares": 0,
                }

            pillar_stats[pillar]["count"] += 1
            pillar_stats[pillar]["total_likes"] += content.get("likes", 0)
            pillar_stats[pillar]["total_comments"] += content.get("comments", 0)
            pillar_stats[pillar]["total_shares"] += content.get("shares", 0)

        # 计算平均互动指数
        for pillar, stats in pillar_stats.items():
            count = max(stats["count"], 1)
            avg_likes = stats["total_likes"] / count
            avg_comments = stats["total_comments"] / count
            avg_shares = stats["total_shares"] / count

            # 互动指数 = likes * 0.4 + comments * 0.35 + shares * 0.25
            engagement_index = avg_likes * 0.4 + avg_comments * 0.35 + avg_shares * 0.25

            stats["avg_engagement_index"] = round(engagement_index, 2)
            stats["avg_likes"] = round(avg_likes, 0)

        # 按互动指数排序
        sorted_pillars = sorted(
            pillar_stats.items(),
            key=lambda x: x[1].get("avg_engagement_index", 0),
            reverse=True
        )

        return {
            "pillar_ranking": [(p, s) for p, s in sorted_pillars],
            "recommendation": f"优先发展'{sorted_pillars[0][0]}'支柱，其互动指数最高" if sorted_pillars else "",
        }

    def save_insights(self, insights: dict, date_key: str) -> Path:
        """保存洞察数据到文件

        Args:
            insights: 洞察数据
            date_key: 日期键（YYYY-MM-DD）

        Returns:
            保存的文件路径
        """
        filepath = self.insights_dir / f"{date_key}-insights.json"

        data = {
            "timestamp": datetime.now().isoformat(),
            "date": date_key,
            "insights": insights,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return filepath
