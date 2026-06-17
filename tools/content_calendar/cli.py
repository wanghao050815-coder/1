"""
content_calendar CLI — 内容日历命令行工具

用法：
    python -m tools.content_calendar.cli view          # 查看本周日历
    python -m tools.content_calendar.cli add            # 添加内容
    python -m tools.content_calendar.cli status          # 更新状态
    python -m tools.content_calendar.cli conflicts       # 检查排期冲突
    python -m tools.content_calendar.cli export          # 导出周报
    python -m tools.content_calendar.cli stats           # 产能统计
"""

import click
from datetime import datetime, timedelta

from . import (
    ContentItem,
    ContentCalendar,
    Scheduler,
    ConflictChecker,
    Status,
    VALID_PILLARS,
    GROWTH_POTENTIAL_LEVELS,
)

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel

    HAS_RICH = True
except ImportError:
    HAS_RICH = False


console = Console() if HAS_RICH else None


def _print(text: str):
    if console:
        console.print(text)
    else:
        print(text)


def _get_calendar():
    return ContentCalendar()


# ─── CLI Group ───────────────────────────────────────────────

@click.group()
def cli():
    """内容日历管理工具 — 服务于300万粉丝增长目标"""
    pass


# ─── view ────────────────────────────────────────────────────

@cli.command()
@click.option("--week", default=0, help="周偏移量：0=本周，-1=上周，1=下周")
@click.option("--platform", default=None, help="按平台筛选")
@click.option("--status", default=None, help="按状态筛选")
def view(week, platform, status):
    """查看内容日历"""
    cal = _get_calendar()
    items = cal.query(platform=platform, status=status, week_offset=week)

    if not items:
        _print("本周暂无排期内容")
        return

    if HAS_RICH:
        now = datetime.now()
        days_since_monday = now.weekday()
        target_monday = now - timedelta(days=days_since_monday) + timedelta(weeks=week)
        week_label = target_monday.strftime("%m/%d") + " ~ " + (target_monday + timedelta(days=6)).strftime("%m/%d")

        table = Table(title=f"内容日历 — {week_label}")
        table.add_column("ID", style="dim", width=8)
        table.add_column("标题", min_width=20)
        table.add_column("平台", width=8)
        table.add_column("状态", width=10)
        table.add_column("排期时间", width=18)
        table.add_column("增长潜力", width=8)
        table.add_column("负责人", width=8)

        # 按排期时间排序
        items.sort(key=lambda x: x.scheduled_time or "9999")

        for item in items:
            potential_style = {
                "high": "[bold green]高[/]",
                "medium": "[yellow]中[/]",
                "low": "[dim]低[/]",
            }
            status_style = {
                "idea": "[dim]创意[/]",
                "brief": "[blue]Brief[/]",
                "script": "[cyan]脚本[/]",
                "filming": "[magenta]拍摄中[/]",
                "editing": "[yellow]剪辑中[/]",
                "review": "[red]审核中[/]",
                "scheduled": "[green]已排期[/]",
                "published": "[bold green]已发布[/]",
            }
            sched = item.scheduled_time[:16] if item.scheduled_time else "-"
            table.add_row(
                item.id,
                item.title,
                item.platform,
                status_style.get(item.status, item.status),
                sched,
                potential_style.get(item.growth_potential, item.growth_potential),
                item.assignee or "-",
            )

        console.print(table)
    else:
        for item in items:
            sched = item.scheduled_time[:16] if item.scheduled_time else "未排期"
            print(f"[{item.id}] {item.title} | {item.platform} | {item.status} | {sched} | 潜力:{item.growth_potential}")


# ─── add ─────────────────────────────────────────────────────

@cli.command()
@click.option("--title", prompt="内容标题", help="内容标题")
@click.option(
    "--platform",
    prompt="目标平台",
    type=click.Choice(["douyin", "xiaohongshu", "weibo", "bilibili", "wechat", "tiktok"]),
    help="目标平台",
)
@click.option(
    "--pillar",
    prompt="内容支柱",
    type=click.Choice(VALID_PILLARS),
    help="内容支柱",
)
@click.option(
    "--growth-potential",
    prompt="增长潜力 (high/medium/low)",
    type=click.Choice(GROWTH_POTENTIAL_LEVELS),
    default="medium",
    help="预估增长潜力",
)
@click.option("--assignee", default=None, help="负责人")
@click.option("--series", default=None, help="系列名称（如属于系列内容）")
def add(title, platform, pillar, growth_potential, assignee, series):
    """添加新内容到日历"""
    cal = _get_calendar()
    item = ContentItem(
        title=title,
        platform=platform,
        pillar=pillar,
        growth_potential=growth_potential,
        assignee=assignee,
        is_series=bool(series),
        series_name=series,
    )
    cal.add(item)
    _print(f"已添加: [{item.id}] {item.title} ({item.platform}) 增长潜力: {item.growth_potential}")


# ─── status ──────────────────────────────────────────────────

@cli.command()
@click.argument("item_id")
@click.argument("new_status", type=click.Choice([s.value for s in Status]))
def status(item_id, new_status):
    """更新内容状态（沿流水线推进）"""
    cal = _get_calendar()
    try:
        item = cal.update_status(item_id, new_status)
        _print(f"已更新: [{item.id}] {item.title} → {new_status}")
    except (KeyError, ValueError) as e:
        _print(f"错误: {e}")


# ─── conflicts ───────────────────────────────────────────────

@cli.command()
def conflicts():
    """检查排期冲突"""
    cal = _get_calendar()
    checker = ConflictChecker(cal)
    issues = checker.check_all()

    if not issues:
        _print("没有发现排期冲突")
        return

    _print(f"发现 {len(issues)} 个冲突:\n")
    for i, issue in enumerate(issues, 1):
        severity_icon = {"high": "🔴", "medium": "🟡", "low": "🔵"}.get(issue["severity"], "⚪")
        _print(f"  {severity_icon} {i}. [{issue['type']}] {issue['message']}")


# ─── export ──────────────────────────────────────────────────

@cli.command()
@click.option("--week", default=0, help="周偏移量：0=本周，-1=上周")
@click.option("--output", default=None, help="输出文件路径（默认打印到终端）")
def export(week, output):
    """导出周报 Markdown"""
    cal = _get_calendar()
    items = cal.query(week_offset=week)

    now = datetime.now()
    days_since_monday = now.weekday()
    target_monday = now - timedelta(days=days_since_monday) + timedelta(weeks=week)
    week_label = target_monday.strftime("%Y-%m-%d") + " 至 " + (target_monday + timedelta(days=6)).strftime("%Y-%m-%d")

    lines = [
        f"# 内容周报 — {week_label}\n",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n",
        "## 内容列表\n",
        "| 标题 | 平台 | 状态 | 排期 | 增长潜力 | 负责人 |",
        "|------|------|------|------|----------|--------|",
    ]

    items.sort(key=lambda x: x.scheduled_time or "9999")
    for item in items:
        sched = item.scheduled_time[:16] if item.scheduled_time else "-"
        lines.append(
            f"| {item.title} | {item.platform} | {item.status} | {sched} | {item.growth_potential} | {item.assignee or '-'} |"
        )

    stats = cal.stats()
    lines.extend([
        "\n## 产能统计\n",
        f"- 总内容数: {stats['total']}",
        f"- 高增长潜力: {stats['by_growth_potential'].get('high', 0)}",
        f"- 中增长潜力: {stats['by_growth_potential'].get('medium', 0)}",
        f"- 低增长潜力: {stats['by_growth_potential'].get('low', 0)}",
    ])

    md = "\n".join(lines)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(md)
        _print(f"已导出到 {output}")
    else:
        print(md)


# ─── stats ───────────────────────────────────────────────────

@cli.command()
def stats():
    """产能和增长潜力分布统计"""
    cal = _get_calendar()
    s = cal.stats()

    if HAS_RICH:
        console.print(Panel(f"[bold]总内容数: {s['total']}[/]", title="内容日历统计"))

        # 状态分布
        table = Table(title="按状态分布")
        table.add_column("状态", width=12)
        table.add_column("数量", justify="right", width=8)
        for status_val in [st.value for st in Status]:
            count = s["by_status"].get(status_val, 0)
            table.add_row(status_val, str(count))
        console.print(table)

        # 平台分布
        table2 = Table(title="按平台分布")
        table2.add_column("平台", width=12)
        table2.add_column("数量", justify="right", width=8)
        for platform, count in sorted(s["by_platform"].items()):
            table2.add_row(platform, str(count))
        console.print(table2)

        # 增长潜力分布
        table3 = Table(title="增长潜力分布")
        table3.add_column("潜力", width=12)
        table3.add_column("数量", justify="right", width=8)
        for level in GROWTH_POTENTIAL_LEVELS:
            table3.add_row(level, str(s["by_growth_potential"].get(level, 0)))
        console.print(table3)
    else:
        print(f"总内容数: {s['total']}")
        print(f"按状态: {s['by_status']}")
        print(f"按平台: {s['by_platform']}")
        print(f"按增长潜力: {s['by_growth_potential']}")


# ─── Entry Point ─────────────────────────────────────────────

if __name__ == "__main__":
    cli()
