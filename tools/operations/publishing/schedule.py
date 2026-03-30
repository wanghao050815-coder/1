"""内容日历管理 — 周/日排期、发布计划生成。"""

import json
from datetime import datetime, timedelta
from pathlib import Path


# 各平台最佳发布时段（基于健身领域数据）
OPTIMAL_TIMES = {
    "douyin": {
        "weekday": ["07:00", "12:00", "18:00", "21:00"],
        "weekend": ["09:00", "12:00", "17:00", "20:00"],
        "best": "18:00-21:00",
        "note": "晚间高峰流量最大，午间次之",
    },
    "xiaohongshu": {
        "weekday": ["07:30", "12:00", "18:30", "21:30"],
        "weekend": ["10:00", "14:00", "20:00"],
        "best": "21:00-22:30",
        "note": "晚间女性用户活跃度最高",
    },
    "weibo": {
        "weekday": ["08:00", "12:00", "22:00"],
        "weekend": ["10:00", "15:00", "22:00"],
        "best": "12:00-13:00",
        "note": "午间碎片时间传播最快",
    },
    "bilibili": {
        "weekday": ["18:00", "20:00"],
        "weekend": ["10:00", "14:00", "20:00"],
        "best": "周末下午",
        "note": "长视频适合周末发布，用户有充足时间观看",
    },
    "wechat": {
        "weekday": ["07:00", "12:00", "21:00"],
        "weekend": ["09:00", "21:00"],
        "best": "07:00-08:00",
        "note": "早间通勤时段打开率最高",
    },
}


def generate_weekly_schedule(week_start: str, posts: list[dict]) -> dict:
    """生成一周的发布排期。

    Args:
        week_start: 周一日期（格式: YYYY-MM-DD）
        posts: 待排期的内容列表，每项含 {topic, platform, pillar, priority}

    Returns:
        周排期计划
    """
    start = datetime.strptime(week_start, "%Y-%m-%d")
    schedule = {
        "week": week_start,
        "created_at": datetime.now().isoformat(),
        "days": {},
    }

    # 按优先级排序
    sorted_posts = sorted(posts, key=lambda x: x.get("priority", 99))

    day_index = 0
    for post in sorted_posts:
        day = start + timedelta(days=day_index % 7)
        day_key = day.strftime("%Y-%m-%d (%A)")
        is_weekend = day.weekday() >= 5

        platform = post.get("platform", "douyin")
        times = OPTIMAL_TIMES.get(platform, OPTIMAL_TIMES["douyin"])
        time_slots = times["weekend"] if is_weekend else times["weekday"]
        suggested_time = time_slots[0] if time_slots else "18:00"

        if day_key not in schedule["days"]:
            schedule["days"][day_key] = []

        schedule["days"][day_key].append({
            "topic": post.get("topic", ""),
            "platform": platform,
            "pillar": post.get("pillar", "training"),
            "suggested_time": suggested_time,
            "status": "scheduled",
            "copy_id": post.get("copy_id", ""),
        })

        day_index += 1

    return schedule


def format_weekly_schedule(schedule: dict) -> str:
    """格式化周排期为 Markdown。"""
    report = f"# 内容发布排期 — {schedule['week']} 周\n\n"

    for day, items in schedule["days"].items():
        report += f"## {day}\n\n"
        for item in items:
            status_icon = "🟢" if item["status"] == "published" else "⏳"
            report += f"- {status_icon} **{item['suggested_time']}** [{item['platform']}] {item['topic']}\n"
            report += f"  - 支柱: {item['pillar']} | 文案编号: {item.get('copy_id', '待分配')}\n"
        report += "\n"

    return report


def get_optimal_time(platform: str, is_weekend: bool = False) -> str:
    """获取指定平台的最佳发布时间。"""
    times = OPTIMAL_TIMES.get(platform, OPTIMAL_TIMES["douyin"])
    return times["best"]


def save_schedule(schedule: dict, data_dir: Path) -> Path:
    """保存排期到文件。"""
    cal_dir = data_dir / "运营" / "排期"
    cal_dir.mkdir(parents=True, exist_ok=True)
    filepath = cal_dir / f"schedule-{schedule['week']}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(schedule, f, ensure_ascii=False, indent=2)
    return filepath
