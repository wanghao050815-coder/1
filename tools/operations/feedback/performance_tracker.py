"""发布文案与互动数据关联 + 金句库自动提取。

数据由用户手动提供（不做自动采集），系统负责关联和分析。
"""

import json
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def record_performance(copy_id: str, metrics: dict,
                       data_dir: Path = None) -> dict:
    """记录文案的发布后互动数据。

    Args:
        copy_id: 文案编号（如 CP-20260401-001）
        metrics: 互动数据，格式:
            {
                "platform": "douyin",
                "likes": 12000,
                "comments": 450,
                "shares": 1200,
                "views": 250000,
                "completion_rate": 0.35,
                "published_at": "2026-04-01T18:00:00"
            }
        data_dir: 数据目录（默认 /数据/文案/）

    Returns:
        关联后的完整记录
    """
    data_dir = data_dir or REPO_ROOT / "数据" / "文案"

    # 查找原始文案元数据
    meta_file = None
    for subdir in ["草稿", "已发布"]:
        candidate = data_dir / subdir / f"{copy_id}.json"
        if candidate.exists():
            meta_file = candidate
            break

    meta = {}
    if meta_file:
        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)

    # 计算互动率
    views = metrics.get("views", 0)
    engagement_rate = 0
    if views > 0:
        engagement_rate = (
            metrics.get("likes", 0) +
            metrics.get("comments", 0) +
            metrics.get("shares", 0)
        ) / views

    # 构建完整记录
    record = {
        "copy_id": copy_id,
        "original_meta": meta,
        "performance": {
            **metrics,
            "engagement_rate": round(engagement_rate, 4),
        },
        "recorded_at": datetime.now().isoformat(),
    }

    # 保存到已发布目录
    published_dir = data_dir / "已发布"
    published_dir.mkdir(parents=True, exist_ok=True)
    perf_file = published_dir / f"{copy_id}-performance.json"
    with open(perf_file, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)

    # 检查是否符合金句库入库条件
    if should_extract_to_golden(metrics):
        extract_to_golden_library(copy_id, record, data_dir)

    return record


def should_extract_to_golden(metrics: dict, likes_threshold: int = 50000) -> bool:
    """判断是否应该提取到金句库。

    条件：点赞数超过阈值，或互动率异常高
    """
    likes = metrics.get("likes", 0)
    views = metrics.get("views", 0)

    if likes >= likes_threshold:
        return True

    if views > 0:
        engagement_rate = (likes + metrics.get("comments", 0) + metrics.get("shares", 0)) / views
        if engagement_rate > 0.1:  # 互动率 > 10%
            return True

    return False


def extract_to_golden_library(copy_id: str, record: dict,
                              data_dir: Path = None) -> Path:
    """将高互动文案提取到金句库。"""
    data_dir = data_dir or REPO_ROOT / "数据" / "文案"
    golden_dir = data_dir / "金句库"
    golden_dir.mkdir(parents=True, exist_ok=True)

    golden_entry = {
        "copy_id": copy_id,
        "title": record.get("original_meta", {}).get("type_name", ""),
        "platform": record["performance"].get("platform", "douyin"),
        "likes": record["performance"].get("likes", 0),
        "comments": record["performance"].get("comments", 0),
        "shares": record["performance"].get("shares", 0),
        "engagement_rate": record["performance"].get("engagement_rate", 0),
        "extracted_at": datetime.now().isoformat(),
        "reason": "高互动自动提取",
    }

    # 查找并附带文案内容
    for subdir in ["草稿", "已发布"]:
        md_file = data_dir / subdir / f"{copy_id}.md"
        if md_file.exists():
            golden_entry["content"] = md_file.read_text(encoding="utf-8")
            break

    filepath = golden_dir / f"{copy_id}-golden.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(golden_entry, f, ensure_ascii=False, indent=2)

    return filepath


def generate_review_report(period: str, data_dir: Path = None) -> str:
    """生成复盘报告。

    Args:
        period: 复盘周期标识（如 "2026-W14" 或 "2026-04"）
        data_dir: 数据目录

    Returns:
        Markdown 格式的复盘报告
    """
    data_dir = data_dir or REPO_ROOT / "数据" / "文案"
    published_dir = data_dir / "已发布"

    if not published_dir.exists():
        return "# 复盘报告\n\n暂无已发布文案的数据记录。"

    # 收集所有 performance 记录
    records = []
    for f in published_dir.glob("*-performance.json"):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                records.append(json.load(fp))
        except (json.JSONDecodeError, KeyError):
            pass

    if not records:
        return f"# 复盘报告 — {period}\n\n暂无发布数据。请先使用 `record_performance()` 录入数据。"

    # 统计
    total = len(records)
    total_likes = sum(r["performance"].get("likes", 0) for r in records)
    total_comments = sum(r["performance"].get("comments", 0) for r in records)
    avg_likes = total_likes // total if total else 0
    avg_engagement = sum(r["performance"].get("engagement_rate", 0) for r in records) / total if total else 0

    # 按赞数排名
    sorted_records = sorted(records, key=lambda r: r["performance"].get("likes", 0), reverse=True)

    report = f"""# 复盘报告 — {period}

## 整体数据
| 指标 | 数值 |
|------|------|
| 发布总数 | {total} 条 |
| 总赞数 | {total_likes:,} |
| 总评论数 | {total_comments:,} |
| 平均赞数 | {avg_likes:,} |
| 平均互动率 | {avg_engagement:.2%} |

## TOP 3 文案
"""
    for i, r in enumerate(sorted_records[:3], 1):
        perf = r["performance"]
        report += f"\n### {i}. {r['copy_id']}\n"
        report += f"- 赞: {perf.get('likes', 0):,} | 评: {perf.get('comments', 0):,} | 转: {perf.get('shares', 0):,}\n"
        report += f"- 互动率: {perf.get('engagement_rate', 0):.2%}\n"

    # 金句库统计
    golden_dir = data_dir / "金句库"
    golden_count = len(list(golden_dir.glob("*.json"))) if golden_dir.exists() else 0

    report += f"\n## 金句库\n本期新入库: {golden_count} 条\n"

    report += f"\n---\n生成时间: {datetime.now().isoformat()}"
    return report
