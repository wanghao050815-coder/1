"""CLI 入口 — 邪修宗 Agent 系统。

用法：
    python -m tools.agents copywrite --topic "跑步膝盖疼" --platform douyin --pillar training
    python -m tools.agents copywrite --topic "减脂早餐坑" --platform all
    python -m tools.agents plan --count 14 --theme "春季户外训练"
    python -m tools.agents brief --topic "跑步膝盖疼" --platform douyin
    python -m tools.agents community --action triage --input comments.txt
    python -m tools.agents analytics --action weekly --input data.txt
    python -m tools.agents publish --platform douyin --input copy.txt
    python -m tools.agents review --input draft.md
"""

import click
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown

console = Console()


def render(text: str):
    """Rich markdown 渲染输出。"""
    console.print(Markdown(text))


def read_input(input_path: str | None, fallback: str = "") -> str:
    """从文件或 fallback 读取输入。"""
    if input_path:
        p = Path(input_path)
        if p.exists():
            return p.read_text(encoding="utf-8")
        console.print(f"[red]文件不存在: {input_path}[/red]")
        raise SystemExit(1)
    return fallback


@click.group()
def cli():
    """🔥 邪修宗 Agent 系统 — 邪修正道，百炼飞仙"""
    pass


# ── Copywriter Agent ─────────────────────────────────


@cli.command()
@click.option("--topic", "-t", required=True, help="选题标题/描述")
@click.option(
    "--platform", "-p", default="douyin",
    type=click.Choice(["douyin", "xiaohongshu", "weibo", "bilibili", "wechat", "all"]),
    help="目标平台",
)
@click.option(
    "--pillar", "-l", default="training",
    type=click.Choice(["training", "nutrition", "lifestyle", "trending", "brand", "sect_ip"]),
    help="内容支柱",
)
@click.option("--brief", "-b", default="", help="详细 Brief（可选）")
@click.option("--tone", default="", help="语气指定（可选）")
@click.option("--no-save", is_flag=True, help="不保存草稿")
@click.option("--model", "-m", default=None, help="模型覆盖（如 claude-opus-4-20250918）")
def copywrite(topic, platform, pillar, brief, tone, no_save, model):
    """✍️  生成文案 — Copywriter Agent"""
    from .copywriter import CopywriterAgent

    console.print(f"\n[bold gold1]⚔️ 邪修宗·文案部[/bold gold1]")
    console.print(f"选题: [cyan]{topic}[/cyan] | 平台: [green]{platform}[/green] | 支柱: [yellow]{pillar}[/yellow]\n")

    with console.status("[bold gold1]修炼中...文案生成中...[/bold gold1]"):
        agent = CopywriterAgent(model=model) if model else CopywriterAgent()
        result = agent.generate(
            topic=topic, platform=platform, pillar=pillar,
            brief=brief, tone=tone, save=not no_save,
        )

    render(result)


@cli.command()
@click.option("--input", "-i", "input_path", required=True, help="待审核的文案文件路径")
@click.option("--model", "-m", default=None, help="模型覆盖")
def review(input_path, model):
    """🔍 审核文案 — 品牌一致性检查"""
    from .copywriter import CopywriterAgent

    draft = read_input(input_path)
    console.print(f"\n[bold gold1]⚔️ 邪修宗·文案审核[/bold gold1]\n")

    with console.status("[bold gold1]审核中...[/bold gold1]"):
        agent = CopywriterAgent(model=model) if model else CopywriterAgent()
        result = agent.review(draft)

    render(result)


# ── Planner Agent ─────────────────────────────────────


@cli.command()
@click.option("--count", "-n", default=14, help="选题数量")
@click.option("--theme", default="", help="本周主题线索（可选）")
@click.option("--week-start", default="", help="周一日期（如 2026-04-06）")
@click.option("--constraints", default="", help="额外约束（可选）")
@click.option("--model", "-m", default=None, help="模型覆盖")
def plan(count, theme, week_start, constraints, model):
    """📋 规划选题 — Planner Agent"""
    from .planner import PlannerAgent

    console.print(f"\n[bold gold1]⚔️ 邪修宗·策划部[/bold gold1]")
    console.print(f"选题数: [cyan]{count}[/cyan]\n")

    with console.status("[bold gold1]策划中...[/bold gold1]"):
        agent = PlannerAgent(model=model) if model else PlannerAgent()
        result = agent.plan_week(count=count, theme=theme, week_start=week_start, constraints=constraints)

    render(result)


@cli.command()
@click.option("--topic", "-t", required=True, help="选题标题")
@click.option("--platform", "-p", default="douyin", help="目标平台")
@click.option("--pillar", "-l", default="training", help="内容支柱")
@click.option("--context", default="", help="补充背景（可选）")
@click.option("--model", "-m", default=None, help="模型覆盖")
def brief(topic, platform, pillar, context, model):
    """📝 生成 Brief — Planner Agent"""
    from .planner import PlannerAgent

    console.print(f"\n[bold gold1]⚔️ 邪修宗·Brief 生成[/bold gold1]\n")

    with console.status("[bold gold1]生成中...[/bold gold1]"):
        agent = PlannerAgent(model=model) if model else PlannerAgent()
        result = agent.generate_brief(topic=topic, platform=platform, pillar=pillar, context=context)

    render(result)


# ── Community Agent ───────────────────────────────────


@cli.command()
@click.option(
    "--action", "-a", required=True,
    type=click.Choice(["triage", "reply", "ugc"]),
    help="操作类型",
)
@click.option("--input", "-i", "input_path", default=None, help="输入文件路径")
@click.option("--comment", "-c", default="", help="单条评论内容（reply 模式）")
@click.option("--model", "-m", default=None, help="模型覆盖")
def community(action, input_path, comment, model):
    """💬 社区管理 — Community Agent"""
    from .community import CommunityAgent

    console.print(f"\n[bold gold1]⚔️ 邪修宗·社区部[/bold gold1]\n")

    agent = CommunityAgent(model=model) if model else CommunityAgent()

    with console.status("[bold gold1]处理中...[/bold gold1]"):
        if action == "triage":
            text = read_input(input_path, "")
            if not text:
                console.print("[red]请用 --input 指定评论文件[/red]")
                return
            result = agent.triage(text)
        elif action == "reply":
            if not comment:
                console.print("[red]请用 --comment 指定评论内容[/red]")
                return
            result = agent.draft_reply(comment)
        elif action == "ugc":
            text = read_input(input_path, "")
            result = agent.detect_ugc(text)
        else:
            result = "未知操作"

    render(result)


# ── Analytics Agent ───────────────────────────────────


@cli.command()
@click.option(
    "--action", "-a", required=True,
    type=click.Choice(["weekly", "kpi", "insights"]),
    help="操作类型",
)
@click.option("--input", "-i", "input_path", required=True, help="数据文件路径")
@click.option("--model", "-m", default=None, help="模型覆盖")
def analytics(action, input_path, model):
    """📊 数据分析 — Analytics Agent"""
    from .analytics import AnalyticsAgent

    console.print(f"\n[bold gold1]⚔️ 邪修宗·数据部[/bold gold1]\n")

    data = read_input(input_path)
    agent = AnalyticsAgent(model=model) if model else AnalyticsAgent()

    with console.status("[bold gold1]分析中...[/bold gold1]"):
        if action == "weekly":
            result = agent.weekly_report(data)
        elif action == "kpi":
            result = agent.kpi_check(data)
        elif action == "insights":
            result = agent.content_insights(data)
        else:
            result = "未知操作"

    render(result)


# ── Publisher Agent ───────────────────────────────────


@cli.command()
@click.option("--platform", "-p", required=True, help="目标平台")
@click.option("--input", "-i", "input_path", required=True, help="已审核文案文件路径")
@click.option("--video-info", default="", help="视频规格信息（可选）")
@click.option("--model", "-m", default=None, help="模型覆盖")
def publish(platform, input_path, video_info, model):
    """🚀 发布检查 — Publisher Agent"""
    from .publisher import PublisherAgent

    console.print(f"\n[bold gold1]⚔️ 邪修宗·发布检查[/bold gold1]\n")

    copy_text = read_input(input_path)
    agent = PublisherAgent(model=model) if model else PublisherAgent()

    with console.status("[bold gold1]检查中...[/bold gold1]"):
        result = agent.checklist(platform=platform, copy_text=copy_text, video_info=video_info)

    render(result)


if __name__ == "__main__":
    cli()
