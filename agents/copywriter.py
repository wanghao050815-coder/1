#!/usr/bin/env python3
"""
邪修宗 Copywriter Agent

用法:
    # 为单个平台生成文案
    python -m agents.copywriter --topic "跑步膝盖疼的热身动作" --platform douyin --pillar training

    # 为所有平台生成文案
    python -m agents.copywriter --topic "跑步膝盖疼的热身动作" --pillar training --all-platforms

    # 指定内容类型和额外要求
    python -m agents.copywriter --topic "清明假期户外徒步" --pillar trending --platform douyin --notes "蹭清明热点，强调户外有氧"

    # 使用 brief 文件
    python -m agents.copywriter --brief data/briefs/W14-01.md --all-platforms
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import click

from agents.config import (
    ALL_PLATFORMS,
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    DRAFTS_DIR,
    PLATFORM_NAMES,
)
from agents.prompts import build_copywriter_system_prompt


PILLAR_NAMES = {
    "training": "训练方法",
    "nutrition": "营养饮食",
    "lifestyle": "生活方式",
    "trending": "热点借势",
    "sect_ip": "宗门IP",
    "commercial": "品牌合作",
    "qa": "互动问答",
    "transformation": "体型变化",
}


def ensure_dirs():
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)


def generate_copy_id(platform: str) -> str:
    today = datetime.now().strftime("%Y%m%d")
    ensure_dirs()
    existing = list(DRAFTS_DIR.glob(f"*{today}*{platform}*.md"))
    seq = len(existing) + 1
    return f"CP-{today}-{platform}-{seq:03d}"


def call_anthropic(system_prompt: str, user_message: str) -> str:
    """调用 Anthropic API 生成文案"""
    try:
        import anthropic
    except ImportError:
        print("错误: 请先安装 anthropic SDK")
        print("  pip install anthropic")
        sys.exit(1)

    if not ANTHROPIC_API_KEY:
        print("错误: 未设置 ANTHROPIC_API_KEY 环境变量")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    message = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    return message.content[0].text


def build_user_message(
    topic: str,
    platform: str,
    pillar: str,
    notes: str = "",
    brief_content: str = "",
) -> str:
    """构建用户消息（即具体的文案需求）"""
    platform_name = PLATFORM_NAMES.get(platform, platform)
    pillar_name = PILLAR_NAMES.get(pillar, pillar)

    msg = f"""请为以下选题生成 **{platform_name}** 平台的完整文案：

## 选题信息
- **主题：** {topic}
- **目标平台：** {platform_name}
- **内容支柱：** {pillar_name}
"""

    if brief_content:
        msg += f"\n## 创作简报\n\n{brief_content}\n"

    if notes:
        msg += f"\n## 额外要求\n\n{notes}\n"

    msg += f"""
## 输出要求

请严格按照 system prompt 中定义的 **{platform_name}** 输出格式生成文案。
确保：
1. Hook 使用钩子公式
2. 宗门术语自然植入（按内容支柱「{pillar_name}」调整强度）
3. 通过自检清单全部 7 项
4. 输出完整可用的文案，不要留空白待填
"""
    return msg


def save_draft(copy_id: str, platform: str, pillar: str, topic: str, content: str) -> Path:
    """保存文案草稿和元数据"""
    ensure_dirs()

    # 保存 markdown 文案
    md_path = DRAFTS_DIR / f"{copy_id}.md"
    md_path.write_text(
        f"# {topic}\n\n"
        f"> 文案编号: {copy_id} | 平台: {PLATFORM_NAMES[platform]} | "
        f"支柱: {PILLAR_NAMES.get(pillar, pillar)} | "
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"---\n\n{content}",
        encoding="utf-8",
    )

    # 保存元数据 JSON
    meta = {
        "copy_id": copy_id,
        "topic": topic,
        "platform": platform,
        "platform_name": PLATFORM_NAMES[platform],
        "pillar": pillar,
        "pillar_name": PILLAR_NAMES.get(pillar, pillar),
        "status": "draft",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "generated_by": "copywriter_agent",
        "model": ANTHROPIC_MODEL,
        "revision_count": 0,
    }
    json_path = DRAFTS_DIR / f"{copy_id}.json"
    json_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    return md_path


@click.command()
@click.option("--topic", "-t", help="选题主题（如：跑步膝盖疼的热身动作）")
@click.option(
    "--platform", "-p",
    type=click.Choice(ALL_PLATFORMS),
    help="目标平台",
)
@click.option(
    "--pillar",
    type=click.Choice(list(PILLAR_NAMES.keys())),
    default="training",
    help="内容支柱",
)
@click.option("--all-platforms", "-a", is_flag=True, help="为所有平台生成文案")
@click.option("--notes", "-n", default="", help="额外要求/备注")
@click.option("--brief", "-b", type=click.Path(exists=True), help="Brief 文件路径")
@click.option("--dry-run", is_flag=True, help="只显示 prompt，不调用 API")
def main(topic, platform, pillar, all_platforms, notes, brief, dry_run):
    """邪修宗 Copywriter Agent — AI 文案生成"""

    # 处理 brief 文件
    brief_content = ""
    if brief:
        brief_content = Path(brief).read_text(encoding="utf-8")
        if not topic:
            # 从 brief 中提取主题（取第一个 # 标题）
            for line in brief_content.splitlines():
                if line.startswith("# "):
                    topic = line[2:].strip()
                    break

    if not topic:
        click.echo("错误: 请提供 --topic 或 --brief")
        sys.exit(1)

    # 确定要生成的平台列表
    if all_platforms:
        platforms = ALL_PLATFORMS
    elif platform:
        platforms = [platform]
    else:
        click.echo("错误: 请指定 --platform 或 --all-platforms")
        sys.exit(1)

    click.echo(f"\n🔥 邪修宗 Copywriter Agent 启动")
    click.echo(f"   选题: {topic}")
    click.echo(f"   支柱: {PILLAR_NAMES.get(pillar, pillar)}")
    click.echo(f"   平台: {', '.join(PLATFORM_NAMES[p] for p in platforms)}")
    click.echo()

    for p in platforms:
        click.echo(f"⚔️  正在为 {PLATFORM_NAMES[p]} 生成文案...")

        system_prompt = build_copywriter_system_prompt(platform=p)
        user_message = build_user_message(
            topic=topic,
            platform=p,
            pillar=pillar,
            notes=notes,
            brief_content=brief_content,
        )

        if dry_run:
            click.echo(f"\n--- System Prompt ({len(system_prompt)} chars) ---")
            click.echo(system_prompt[:500] + "\n...(truncated)")
            click.echo(f"\n--- User Message ---")
            click.echo(user_message)
            click.echo()
            continue

        content = call_anthropic(system_prompt, user_message)

        # 保存草稿
        copy_id = generate_copy_id(p)
        md_path = save_draft(copy_id, p, pillar, topic, content)

        click.echo(f"   ✅ {copy_id} → {md_path}")
        click.echo()

    if not dry_run:
        click.echo(f"🔥 全部完成！文案已保存到 {DRAFTS_DIR}/")
        click.echo(f"   使用 copy_cli.py list 查看，copy_cli.py review --id <编号> 审核")


if __name__ == "__main__":
    main()
