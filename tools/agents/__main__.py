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


# ── Librarian Agent (素材库管理) ──────────────────────


@cli.command()
@click.option("--input", "-i", "input_path", required=True, help="原始文案文件或目录路径")
@click.option("--engagement", "-e", default="", help="互动数据（如'点赞1.2w 评论800 收藏3k'）")
@click.option("--model", "-m", default=None, help="模型覆盖")
def ingest(input_path, engagement, model):
    """📥 文案入库 — 分析原始文案并存入素材库"""
    from .librarian import LibrarianAgent

    console.print(f"\n[bold gold1]⚔️ 邪修宗·文案馆[/bold gold1]\n")

    agent = LibrarianAgent(model=model) if model else LibrarianAgent()
    p = Path(input_path)

    with console.status("[bold gold1]分析入库中...[/bold gold1]"):
        if p.is_dir():
            result = agent.ingest_batch(str(p))
        elif p.is_file():
            raw = p.read_text(encoding="utf-8")
            result = agent.ingest(raw, source_file=p.name, engagement=engagement)
        else:
            console.print(f"[red]路径不存在: {input_path}[/red]")
            return

    render(result)


@cli.command()
@click.option("--interactive", is_flag=True, help="交互式风格提炼（多轮问答）")
@click.option("--model", "-m", default=None, help="模型覆盖")
def analyze(interactive, model):
    """🧬 风格提炼 — 分析素材库，输出写作风格 DNA"""
    from .librarian import LibrarianAgent

    console.print(f"\n[bold gold1]⚔️ 邪修宗·风格DNA提炼[/bold gold1]\n")

    agent = LibrarianAgent(model=model) if model else LibrarianAgent()

    if interactive:
        console.print("[yellow]交互模式暂未实现，使用自动分析模式。[/yellow]\n")

    with console.status("[bold gold1]深度分析中...提炼写作DNA...[/bold gold1]"):
        result = agent.analyze_style()

    render(result)


@cli.command()
@click.option("--input", "-i", "input_path", required=True, help="已审核文案文件路径")
@click.option("--engagement", "-e", default="", help="互动数据")
@click.option("--model", "-m", default=None, help="模型覆盖")
def approve(input_path, engagement, model):
    """✅ 审核入库 — 将审核通过的文案存入素材库"""
    from .librarian import LibrarianAgent

    draft = read_input(input_path)
    console.print(f"\n[bold gold1]⚔️ 邪修宗·文案入库[/bold gold1]\n")

    with console.status("[bold gold1]分析入库中...[/bold gold1]"):
        agent = LibrarianAgent(model=model) if model else LibrarianAgent()
        result = agent.approve_to_library(draft, source_file=Path(input_path).name, engagement=engagement)

    render(result)


# ── Operations Agent (运营部门) ───────────────────────


@cli.command()
@click.option("--followers", "-f", required=True, type=int, help="当前粉丝数")
@click.option("--growth-rate", "-g", default=0.0, type=float, help="月增长率（如0.1=10%）")
@click.option("--engagement-rate", "-e", default=0.0, type=float, help="互动率")
@click.option("--context", "-c", default="", help="补充信息")
@click.option("--model", "-m", default=None, help="模型覆盖")
def diagnose(followers, growth_rate, engagement_rate, context, model):
    """🎯 账号诊断 — Operations Agent"""
    from .operations import OperationsAgent

    console.print(f"\n[bold gold1]⚔️ 邪修宗·运营部[/bold gold1]")
    console.print(f"粉丝: [cyan]{followers:,}[/cyan] | 月增长: [green]{growth_rate:.1%}[/green]\n")

    with console.status("[bold gold1]诊断中...[/bold gold1]"):
        agent = OperationsAgent(model=model) if model else OperationsAgent()
        result = agent.diagnose_stage(
            followers=followers, growth_rate=growth_rate,
            engagement_rate=engagement_rate, extra_context=context,
        )

    render(result)


@cli.command("ops-plan")
@click.option("--year", "-y", required=True, type=int, help="年份")
@click.option("--month", "-M", required=True, type=int, help="月份")
@click.option("--stage", "-s", default="growth", help="账号阶段")
@click.option("--context", "-c", default="", help="补充背景")
@click.option("--model", "-m", default=None, help="模型覆盖")
def ops_plan(year, month, stage, context, model):
    """📋 月度运营计划 — Operations Agent"""
    from .operations import OperationsAgent

    console.print(f"\n[bold gold1]⚔️ 邪修宗·运营规划[/bold gold1]")
    console.print(f"规划: [cyan]{year}年{month}月[/cyan] | 阶段: [green]{stage}[/green]\n")

    with console.status("[bold gold1]规划中...[/bold gold1]"):
        agent = OperationsAgent(model=model) if model else OperationsAgent()
        result = agent.plan_month(year=year, month=month, stage=stage, context=context)

    render(result)


@cli.command("ops-review")
@click.option("--input", "-i", "input_path", required=True, help="运营数据文件路径")
@click.option("--model", "-m", default=None, help="模型覆盖")
def ops_review(input_path, model):
    """📊 运营复盘 — Operations Agent"""
    from .operations import OperationsAgent

    data = read_input(input_path)
    console.print(f"\n[bold gold1]⚔️ 邪修宗·运营复盘[/bold gold1]\n")

    with console.status("[bold gold1]分析中...[/bold gold1]"):
        agent = OperationsAgent(model=model) if model else OperationsAgent()
        result = agent.review_performance(data)

    render(result)


# ── Coach Agent (会员私教) ────────────────────────────


@cli.command()
@click.option("--input", "-i", "input_path", required=True, help="用户档案文件路径")
@click.option(
    "--part", "-p", default="all",
    type=click.Choice(["all", "warmup", "training", "diet"]),
    help="生成哪部分计划",
)
@click.option("--no-save", is_flag=True, help="不保存计划文件")
@click.option("--model", "-m", default=None, help="模型覆盖")
def coach(input_path, part, no_save, model):
    """💪 私教计划 — Coach Agent（体态热身/训练/饮食）"""
    from .coach import CoachAgent

    profile = read_input(input_path)
    console.print(f"\n[bold gold1]⚔️ 邪修宗·私教部[/bold gold1]")
    console.print(f"计划类型: [cyan]{part}[/cyan]\n")

    agent = CoachAgent(model=model) if model else CoachAgent()
    save = not no_save

    with console.status("[bold gold1]修炼计划生成中...[/bold gold1]"):
        if part == "all":
            result = agent.generate_full_plan(profile, save=save)
        elif part == "warmup":
            result = agent.generate_warmup(profile, save=save)
        elif part == "training":
            result = agent.generate_training(profile, save=save)
        elif part == "diet":
            result = agent.generate_diet(profile, save=save)

    render(result)


@cli.command()
@click.option("--input", "-i", "input_path", required=True, help="当前计划文件路径")
@click.option("--feedback", "-f", required=True, help="用户反馈（如'卧推肩膀不舒服'）")
@click.option("--model", "-m", default=None, help="模型覆盖")
def adjust(input_path, feedback, model):
    """🔧 调整计划 — 根据用户反馈修改训练/饮食方案"""
    from .coach import CoachAgent

    plan = read_input(input_path)
    console.print(f"\n[bold gold1]⚔️ 邪修宗·计划调整[/bold gold1]\n")

    with console.status("[bold gold1]调整中...[/bold gold1]"):
        agent = CoachAgent(model=model) if model else CoachAgent()
        result = agent.adjust_plan(plan, feedback)

    render(result)


@cli.command()
@click.option("--profile", required=True, help="用户档案文件路径")
@click.option("--plan", "plan_path", required=True, help="当前计划文件路径")
@click.option("--data", "-d", required=True, help="训练进展数据（文字描述或文件路径）")
@click.option("--model", "-m", default=None, help="模型覆盖")
def progress(profile, plan_path, data, model):
    """📈 阶段评估 — 判断是否进入下一训练阶段"""
    from .coach import CoachAgent

    profile_text = read_input(profile)
    plan_text = read_input(plan_path)
    # data 可以是文件路径也可以是文字描述
    data_text = read_input(data, data)

    console.print(f"\n[bold gold1]⚔️ 邪修宗·修炼评估[/bold gold1]\n")

    with console.status("[bold gold1]评估中...[/bold gold1]"):
        agent = CoachAgent(model=model) if model else CoachAgent()
        result = agent.progress_check(profile_text, plan_text, data_text)

    render(result)


if __name__ == "__main__":
    cli()
