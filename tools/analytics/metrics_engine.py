"""指标计算引擎 - 账号和内容的多维度指标计算

支持健康度评分、异常检测、内容有效性评估等核心分析功能。
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
import json


@dataclass
class MetricsSnapshot:
    """指标快照 - 单日或单周的完整指标数据"""
    timestamp: str                  # ISO 8601 时间戳
    followers: int                  # 粉丝数
    follower_change: int            # 日增长数（可为负）
    engagement_rate: float          # 互动率 (likes+comments+shares)/views
    completion_rate: float          # 完播率 (完播数/总播放数)
    comment_rate: float             # 评论率 (评论数/总播放数)
    share_rate: float               # 转发率 (转发数/总播放数)
    save_rate: float                # 收藏率 (收藏数/总播放数)


class MetricsCalculator:
    """指标计算和追踪

    负责计算各类指标，包括：
    - 健康度评分（0-100）
    - 异常检测（3-sigma 规则）
    - 内容有效性评分
    - 趋势预测
    """

    def __init__(self, data_root: Path, account_id: str):
        self.data_root = Path(data_root)
        self.account_id = account_id
        self.metrics_dir = data_root / "accounts" / account_id / "分析" / "指标"
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

    def calculate_health_score(self, snapshot: MetricsSnapshot) -> dict:
        """计算账号健康度评分 (0-100)

        权重：
        - 粉丝增长趋势 (30%)：日增长数
        - 互动率 (25%)：likes+comments+shares 占比
        - 完播率 (20%)：视频完播率
        - 评论/转发率 (15%)：互动评论和转发
        - 收藏率 (10%)：内容收藏

        Args:
            snapshot: 指标快照

        Returns:
            {
                "health_score": 0-100,
                "components": {
                    "growth": 0-100,
                    "engagement": 0-100,
                    ...
                },
                "status": "excellent|good|fair|poor"
            }
        """
        # 规范化各个指标到 0-100
        # 粉丝增长：假设日增 5000+ 为满分 100
        growth_score = min(100, max(0, snapshot.follower_change) / 50)

        # 互动率：规范化为 0-100
        # 目标互动率 5% 为满分 100
        engagement_score = min(100, snapshot.engagement_rate * 2000)

        # 完播率：直接转换为百分比
        completion_score = snapshot.completion_rate * 100

        # 互动细分：评论 + 转发
        interaction_score = min(100, (snapshot.comment_rate + snapshot.share_rate) * 5000)

        # 收藏率
        save_score = min(100, snapshot.save_rate * 667)

        # 加权计算
        health_score = (
            growth_score * 0.30 +
            engagement_score * 0.25 +
            completion_score * 0.20 +
            interaction_score * 0.15 +
            save_score * 0.10
        )

        status = self._classify_health(health_score)

        return {
            "health_score": round(min(100, health_score), 2),
            "components": {
                "growth": round(growth_score, 2),
                "engagement": round(engagement_score, 2),
                "completion": round(completion_score, 2),
                "interaction": round(interaction_score, 2),
                "save": round(save_score, 2),
            },
            "status": status,
        }

    def _classify_health(self, score: float) -> str:
        """健康度分类"""
        if score >= 85:
            return "excellent"  # 优秀
        elif score >= 70:
            return "good"       # 良好
        elif score >= 50:
            return "fair"       # 一般
        else:
            return "poor"       # 较差

    def detect_anomalies(self, current: MetricsSnapshot,
                        historical: List[MetricsSnapshot]) -> List[dict]:
        """检测关键指标异常

        使用 3-sigma 规则：
        - 如果数据离平均值超过 3 倍标准差，则判定为异常
        - 4-5 倍为高风险异常

        Args:
            current: 当前数据
            historical: 历史数据（至少 3 个点）

        Returns:
            异常列表 [{metric, expected, actual, severity}, ...]
        """
        if len(historical) < 3:
            return []  # 数据不足

        anomalies = []
        metrics_to_check = [
            ("follower_change", "粉丝变化"),
            ("engagement_rate", "互动率"),
            ("completion_rate", "完播率"),
        ]

        for metric_key, metric_name in metrics_to_check:
            values = [getattr(h, metric_key) for h in historical]
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            sigma = variance ** 0.5

            current_val = getattr(current, metric_key)
            deviation = abs(current_val - mean)

            # 3-sigma 检测
            if deviation > 3 * sigma:
                # 判定严重程度
                if deviation > 4 * sigma:
                    severity = "critical"
                elif deviation > 3.5 * sigma:
                    severity = "high"
                else:
                    severity = "medium"

                anomalies.append({
                    "metric": metric_name,
                    "expected": round(mean, 4),
                    "actual": round(current_val, 4),
                    "deviation": round(deviation, 4),
                    "sigma": round(deviation / sigma, 2),
                    "severity": severity,
                })

        return anomalies

    def calculate_content_effectiveness(self, content_performance: dict) -> dict:
        """计算内容有效性评分

        综合评分 = likes * 0.4 + comments * 0.35 + shares * 0.25 / views

        Args:
            content_performance: {
                "views": 250000,
                "likes": 12500,
                "comments": 450,
                "shares": 1200,
                "hook_type": "反问梗式",
                "cta_type": "效果承诺型",
                ...
            }

        Returns:
            有效性评分 (0-100)
        """
        views = max(content_performance.get("views", 1), 1)
        likes = content_performance.get("likes", 0)
        comments = content_performance.get("comments", 0)
        shares = content_performance.get("shares", 0)

        # 加权互动指数
        engagement_index = (likes * 0.4 + comments * 0.35 + shares * 0.25) / views

        # 转换为 0-100 分
        # 目标：互动指数 0.08 为 100 分
        effectiveness_score = min(100, engagement_index * 1250)

        return {
            "effectiveness_score": round(effectiveness_score, 2),
            "engagement_index": round(engagement_index, 4),
            "hook_type": content_performance.get("hook_type", "unknown"),
            "cta_type": content_performance.get("cta_type", "unknown"),
            "category": content_performance.get("category", "unknown"),
        }

    def calculate_trend(self, snapshots: List[MetricsSnapshot],
                       metric_key: str, window: int = 7) -> dict:
        """计算指标趋势

        使用移动平均线计算趋势

        Args:
            snapshots: 有序的指标快照列表
            metric_key: 指标字段名 (follower_change, engagement_rate, etc.)
            window: 移动平均窗口大小（天数）

        Returns:
            {
                "current": 当前值,
                "ma7": 7日移动平均,
                "trend": "up|down|stable",
                "velocity": 趋势速度
            }
        """
        if not snapshots:
            return {}

        values = [getattr(s, metric_key) for s in snapshots]
        current = values[-1]

        # 计算移动平均
        if len(values) >= window:
            ma = sum(values[-window:]) / window
        else:
            ma = sum(values) / len(values)

        # 计算趋势（简单线性）
        if len(values) > 1:
            velocity = values[-1] - values[0]  # 总变化
            trend = "up" if velocity > 0 else ("down" if velocity < 0 else "stable")
        else:
            velocity = 0
            trend = "stable"

        return {
            "current": round(current, 4),
            "ma7": round(ma, 4),
            "trend": trend,
            "velocity": round(velocity, 4),
        }

    def save_metrics(self, snapshot: MetricsSnapshot) -> Path:
        """保存指标快照到文件

        Args:
            snapshot: 指标快照

        Returns:
            保存的文件路径
        """
        date_key = datetime.fromisoformat(snapshot.timestamp).strftime("%Y-%m-%d")
        filepath = self.metrics_dir / f"{date_key}-metrics.json"

        data = {
            "timestamp": snapshot.timestamp,
            "data": {
                "followers": snapshot.followers,
                "follower_change": snapshot.follower_change,
                "engagement_rate": snapshot.engagement_rate,
                "completion_rate": snapshot.completion_rate,
                "comment_rate": snapshot.comment_rate,
                "share_rate": snapshot.share_rate,
                "save_rate": snapshot.save_rate,
            }
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return filepath

    def load_historical_metrics(self, days: int = 30) -> List[MetricsSnapshot]:
        """加载历史指标数据

        Args:
            days: 加载过去 N 天的数据

        Returns:
            指标快照列表（按时间排序）
        """
        snapshots = []

        if not self.metrics_dir.exists():
            return snapshots

        # 列出所有指标文件
        metric_files = sorted(self.metrics_dir.glob("*-metrics.json"))

        # 筛选最近 N 天
        cutoff_date = (datetime.now() - timedelta(days=days)).date()

        for filepath in metric_files:
            try:
                with open(filepath, encoding="utf-8") as f:
                    data = json.load(f)

                timestamp = data.get("timestamp", "")
                metric_date = datetime.fromisoformat(timestamp).date()

                if metric_date >= cutoff_date:
                    metric_data = data.get("data", {})
                    snapshot = MetricsSnapshot(
                        timestamp=timestamp,
                        followers=metric_data.get("followers", 0),
                        follower_change=metric_data.get("follower_change", 0),
                        engagement_rate=metric_data.get("engagement_rate", 0),
                        completion_rate=metric_data.get("completion_rate", 0),
                        comment_rate=metric_data.get("comment_rate", 0),
                        share_rate=metric_data.get("share_rate", 0),
                        save_rate=metric_data.get("save_rate", 0),
                    )
                    snapshots.append(snapshot)
            except (json.JSONDecodeError, ValueError):
                continue

        return snapshots
