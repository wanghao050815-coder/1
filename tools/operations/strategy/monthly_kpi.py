"""月度/季度 KPI 目标设定与跟踪。"""

import json
from datetime import datetime
from pathlib import Path


# KPI 维度定义
KPI_DIMENSIONS = {
    "followers_growth": {
        "name": "粉丝增长",
        "unit": "人",
        "description": "当月净增粉丝数",
    },
    "avg_likes": {
        "name": "平均点赞",
        "unit": "次/条",
        "description": "当月发布内容的平均点赞数",
    },
    "avg_completion_rate": {
        "name": "平均完播率",
        "unit": "%",
        "description": "当月视频的平均完播率",
    },
    "engagement_rate": {
        "name": "互动率",
        "unit": "%",
        "description": "（点赞+评论+转发）/播放量",
    },
    "post_count": {
        "name": "发布量",
        "unit": "条",
        "description": "当月总发布条数",
    },
    "viral_count": {
        "name": "爆款数",
        "unit": "条",
        "description": "赞数超过均值3倍的视频数量",
    },
    "revenue": {
        "name": "收入",
        "unit": "元",
        "description": "当月商业合作/变现总收入",
    },
}


def create_monthly_kpi(year: int, month: int, targets: dict,
                       stage: str = "growth") -> dict:
    """创建月度 KPI 目标。

    Args:
        year: 年份
        month: 月份
        targets: KPI 目标值（格式: {dimension: target_value}）
        stage: 账号阶段

    Returns:
        KPI 目标对象
    """
    kpi = {
        "period": f"{year}-{month:02d}",
        "type": "monthly",
        "stage": stage,
        "targets": {},
        "created_at": datetime.now().isoformat(),
        "status": "active",
    }

    for dim, value in targets.items():
        if dim in KPI_DIMENSIONS:
            kpi["targets"][dim] = {
                "name": KPI_DIMENSIONS[dim]["name"],
                "target": value,
                "actual": None,
                "achievement_rate": None,
                "unit": KPI_DIMENSIONS[dim]["unit"],
            }

    return kpi


def update_kpi_actuals(kpi: dict, actuals: dict) -> dict:
    """更新 KPI 实际值并计算达成率。

    Args:
        kpi: KPI 目标对象
        actuals: 实际值（格式: {dimension: actual_value}）

    Returns:
        更新后的 KPI 对象
    """
    for dim, value in actuals.items():
        if dim in kpi["targets"]:
            target = kpi["targets"][dim]
            target["actual"] = value
            if target["target"] and target["target"] > 0:
                target["achievement_rate"] = round(value / target["target"] * 100, 1)
            else:
                target["achievement_rate"] = 0

    kpi["updated_at"] = datetime.now().isoformat()
    return kpi


def format_kpi_report(kpi: dict) -> str:
    """格式化 KPI 报告为 Markdown。"""
    report = f"# KPI 报告 — {kpi['period']}\n\n"
    report += f"账号阶段: {kpi['stage']} | 状态: {kpi['status']}\n\n"
    report += "| 指标 | 目标 | 实际 | 达成率 |\n"
    report += "|------|------|------|--------|\n"

    for dim, target in kpi["targets"].items():
        actual_str = f"{target['actual']:,}" if target["actual"] is not None else "—"
        rate_str = f"{target['achievement_rate']}%" if target["achievement_rate"] is not None else "—"
        status = ""
        if target["achievement_rate"] is not None:
            if target["achievement_rate"] >= 100:
                status = " ✅"
            elif target["achievement_rate"] >= 80:
                status = " ⚠️"
            else:
                status = " ❌"
        report += f"| {target['name']} | {target['target']:,}{target['unit']} | {actual_str}{target['unit']} | {rate_str}{status} |\n"

    return report


def save_kpi(kpi: dict, data_dir: Path) -> Path:
    """保存 KPI 到文件。"""
    kpi_dir = data_dir / "运营" / "KPI"
    kpi_dir.mkdir(parents=True, exist_ok=True)
    filepath = kpi_dir / f"kpi-{kpi['period']}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(kpi, f, ensure_ascii=False, indent=2)
    return filepath
