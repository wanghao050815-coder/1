"""内容支柱配比规划 — 根据账号阶段和目标调整内容配比。"""

from datetime import datetime

# 默认内容支柱配比（百分比）
DEFAULT_MIX = {
    "training": 40,
    "nutrition": 15,
    "lifestyle": 15,
    "sect_ip": 15,
    "trending": 10,
    "brand": 5,
}

PILLAR_NAMES = {
    "training": "训练方法",
    "nutrition": "营养饮食",
    "lifestyle": "健康生活方式",
    "sect_ip": "宗门IP",
    "trending": "热点追踪",
    "brand": "品牌合作",
}


def calculate_weekly_mix(total_posts: int = 7, mix: dict = None) -> dict:
    """根据配比计算每周各支柱应发布的数量。

    Args:
        total_posts: 每周总发布条数
        mix: 配比字典（百分比），默认使用 DEFAULT_MIX

    Returns:
        每个支柱的周发布数量
    """
    mix = mix or DEFAULT_MIX
    allocation = {}
    remaining = total_posts

    # 按百分比从高到低分配
    sorted_pillars = sorted(mix.items(), key=lambda x: x[1], reverse=True)
    for pillar, pct in sorted_pillars[:-1]:
        count = max(1, round(total_posts * pct / 100))
        allocation[pillar] = count
        remaining -= count

    # 最后一个支柱取剩余
    last_pillar = sorted_pillars[-1][0]
    allocation[last_pillar] = max(0, remaining)

    return allocation


def suggest_mix_adjustment(current_mix: dict, performance: dict) -> dict:
    """根据各支柱表现数据建议配比调整。

    Args:
        current_mix: 当前配比
        performance: 各支柱表现（格式: {pillar: {"avg_likes": N, "avg_completion": N}}）

    Returns:
        建议的新配比和调整理由
    """
    adjustments = {}
    reasons = []

    for pillar, data in performance.items():
        current_pct = current_mix.get(pillar, 0)
        avg_likes = data.get("avg_likes", 0)
        avg_completion = data.get("avg_completion", 0)

        if avg_likes > 50000 and current_pct < 30:
            adjustments[pillar] = min(current_pct + 10, 50)
            reasons.append(f"{PILLAR_NAMES.get(pillar, pillar)}: 表现优异（均赞{avg_likes:,}），建议增加至{adjustments[pillar]}%")
        elif avg_likes < 5000 and current_pct > 10:
            adjustments[pillar] = max(current_pct - 5, 5)
            reasons.append(f"{PILLAR_NAMES.get(pillar, pillar)}: 表现低迷（均赞{avg_likes:,}），建议降至{adjustments[pillar]}%")
        else:
            adjustments[pillar] = current_pct

    # 归一化确保总和为100
    total = sum(adjustments.values())
    if total != 100 and total > 0:
        factor = 100 / total
        adjustments = {k: round(v * factor) for k, v in adjustments.items()}

    return {
        "suggested_mix": adjustments,
        "reasons": reasons,
        "generated_at": datetime.now().isoformat(),
    }


def format_mix_report(mix: dict, weekly_posts: int = 7) -> str:
    """格式化内容配比报告为 Markdown。"""
    allocation = calculate_weekly_mix(weekly_posts, mix)

    report = "# 内容支柱配比规划\n\n"
    report += f"| 支柱 | 配比 | 周发布数（共{weekly_posts}条） |\n"
    report += "|------|------|--------|\n"
    for pillar, pct in sorted(mix.items(), key=lambda x: x[1], reverse=True):
        name = PILLAR_NAMES.get(pillar, pillar)
        count = allocation.get(pillar, 0)
        report += f"| {name} | {pct}% | {count}条 |\n"

    return report
