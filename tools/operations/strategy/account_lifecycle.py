"""账号阶段管理 — 冷启动 / 增长期 / 稳定期 / 衰退期。

根据当前粉丝数、互动率、增长趋势自动判断账号所处阶段，
并给出对应的运营策略建议。
"""

import json
from datetime import datetime
from pathlib import Path

# 账号生命周期阶段定义
LIFECYCLE_STAGES = {
    "cold_start": {
        "name": "冷启动期",
        "description": "0-1万粉，找到内容方向，测试爆款模型",
        "follower_range": (0, 10000),
        "strategy": {
            "发布频率": "每日1-2条，测试不同选题方向",
            "内容支柱配比": {"training": 50, "sect_ip": 20, "lifestyle": 15, "nutrition": 10, "trending": 5},
            "核心目标": "找到稳定出爆款的选题模型",
            "关键指标": "完播率 > 30%，单条爆款率 > 5%",
            "运营重点": [
                "高频发布，快速试错",
                "每条分析数据，找出爆款特征",
                "建立宗门人设，沉淀核心粉丝",
                "积极回复评论，建立互动习惯",
            ],
        },
    },
    "growth": {
        "name": "增长期",
        "description": "1万-50万粉，放大爆款模型，建立稳定增长",
        "follower_range": (10000, 500000),
        "strategy": {
            "发布频率": "每日1条精品 + 每周2条测试",
            "内容支柱配比": {"training": 40, "sect_ip": 15, "lifestyle": 15, "nutrition": 15, "trending": 10, "brand": 5},
            "核心目标": "稳定月增粉速度，建立内容矩阵",
            "关键指标": "月增粉 > 10%，互动率 > 5%",
            "运营重点": [
                "复制爆款模型，批量化生产",
                "建立内容日历，保持稳定更新",
                "开始商业化探索（低频合作）",
                "发展子账号/矩阵号",
            ],
        },
    },
    "stable": {
        "name": "稳定期",
        "description": "50万粉以上，稳定变现，维持影响力",
        "follower_range": (500000, float("inf")),
        "strategy": {
            "发布频率": "每日1条，质量优先",
            "内容支柱配比": {"training": 35, "sect_ip": 15, "nutrition": 15, "lifestyle": 15, "brand": 10, "trending": 10},
            "核心目标": "稳定商业变现，维持粉丝活跃度",
            "关键指标": "月掉粉率 < 2%，商业合作ROI > 3",
            "运营重点": [
                "精品内容为主，减少低质量产出",
                "商业合作常态化，建立报价体系",
                "社群运营深化，提高粉丝粘性",
                "布局长期IP资产（课程/社群/品牌）",
            ],
        },
    },
    "decline": {
        "name": "衰退期",
        "description": "连续3个月掉粉或互动率持续下降",
        "follower_range": None,
        "strategy": {
            "发布频率": "减少发布，专注内容创新",
            "内容支柱配比": {"training": 30, "trending": 25, "sect_ip": 20, "lifestyle": 15, "nutrition": 10},
            "核心目标": "找到新的增长点，重新激活账号",
            "关键指标": "止跌回升，恢复正增长",
            "运营重点": [
                "分析下降原因（算法/内容疲劳/竞品）",
                "测试新内容方向和形式",
                "加大热点追踪力度",
                "考虑账号转型或矩阵分流",
            ],
        },
    },
}


def detect_stage(followers: int, monthly_growth_rate: float = 0,
                 engagement_rate: float = 0) -> dict:
    """检测账号当前所处阶段。

    Args:
        followers: 当前粉丝数
        monthly_growth_rate: 月增长率（如 0.1 表示 10%），负值表示掉粉
        engagement_rate: 互动率（点赞+评论+转发/播放量）

    Returns:
        当前阶段信息和策略建议
    """
    # 衰退期优先判断（连续负增长）
    if monthly_growth_rate < -0.02:
        stage = LIFECYCLE_STAGES["decline"]
        stage_key = "decline"
    elif followers < 10000:
        stage = LIFECYCLE_STAGES["cold_start"]
        stage_key = "cold_start"
    elif followers < 500000:
        stage = LIFECYCLE_STAGES["growth"]
        stage_key = "growth"
    else:
        stage = LIFECYCLE_STAGES["stable"]
        stage_key = "stable"

    return {
        "stage_key": stage_key,
        "stage_name": stage["name"],
        "description": stage["description"],
        "strategy": stage["strategy"],
        "detected_at": datetime.now().isoformat(),
        "metrics": {
            "followers": followers,
            "monthly_growth_rate": monthly_growth_rate,
            "engagement_rate": engagement_rate,
        },
    }


def get_stage_strategy(stage_key: str) -> dict:
    """获取指定阶段的运营策略。"""
    stage = LIFECYCLE_STAGES.get(stage_key)
    if not stage:
        return {"error": f"未知阶段: {stage_key}"}
    return stage["strategy"]


def format_stage_report(stage_info: dict) -> str:
    """格式化阶段报告为 Markdown。"""
    s = stage_info["strategy"]
    metrics = stage_info["metrics"]

    report = f"""# 账号阶段诊断报告

## 当前阶段：{stage_info['stage_name']}
{stage_info['description']}

## 账号指标
| 指标 | 数值 |
|------|------|
| 粉丝数 | {metrics['followers']:,} |
| 月增长率 | {metrics['monthly_growth_rate']:.1%} |
| 互动率 | {metrics['engagement_rate']:.1%} |

## 运营策略

### 发布频率
{s['发布频率']}

### 内容支柱配比
"""
    for pillar, pct in s["内容支柱配比"].items():
        report += f"- {pillar}: {pct}%\n"

    report += f"""
### 核心目标
{s['核心目标']}

### 关键指标
{s['关键指标']}

### 运营重点
"""
    for item in s["运营重点"]:
        report += f"- {item}\n"

    report += f"\n---\n诊断时间: {stage_info['detected_at']}"
    return report
