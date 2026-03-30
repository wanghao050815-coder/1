#!/usr/bin/env python3
"""
文案部门 CLI 工具

用于文案创建、管理、审核和话术库维护的命令行工具。

用法:
    python copy_cli.py create   --type <类型> --platform <平台>
    python copy_cli.py list     [--status <状态>] [--platform <平台>]
    python copy_cli.py review   --id <文案编号>
    python copy_cli.py approve  --id <文案编号>
    python copy_cli.py library  [--pillar <支柱>] [--platform <平台>]
    python copy_cli.py stats    [--days <天数>]
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

CONFIG_DIR = Path(__file__).parent.parent / "配置"
DATA_DIR = Path(__file__).parent.parent.parent / "数据" / "文案"

COPY_TYPES = {
    "script": "视频脚本",
    "title": "标题+描述",
    "cover": "封面文案",
    "note": "小红书笔记",
    "weibo": "微博博文",
    "wechat": "微信推文",
    "comment": "互动话术",
    "live": "直播口播稿",
    "commercial": "商务合作文案",
    "community": "社群话术",
}

PLATFORMS = ["douyin", "xiaohongshu", "weibo", "bilibili", "wechat"]

PLATFORM_NAMES = {
    "douyin": "抖音",
    "xiaohongshu": "小红书",
    "weibo": "微博",
    "bilibili": "B站",
    "wechat": "微信",
}

STATUSES = ["draft", "review", "revision", "approved", "published", "archived"]

STATUS_LABELS = {
    "draft": "草稿",
    "review": "审核中",
    "revision": "修改中",
    "approved": "已通过",
    "published": "已发布",
    "archived": "已归档",
}

CONTENT_PILLARS = {
    "training": "训练方法",
    "nutrition": "营养饮食",
    "transformation": "体型变化",
    "lifestyle": "健康生活方式",
    "qa": "互动问答",
    "sect_ip": "宗门IP",
}

# 各平台文案模板
TEMPLATES = {
    "douyin_script": """# 抖音视频脚本

## 基本信息
- 文案编号: {copy_id}
- 内容支柱: {pillar}
- 预估时长: ___秒
- 关联内容编号: ___

## 脚本正文

### [0-3秒] Hook 开场
> （痛点/反常识/数字冲击）

___

### [3-10秒] 问题阐述
> （引发共鸣）

___

### [10-45秒] 核心内容

**要点一：**
[画面：___]
___

**要点二：**
[画面：___]
___

**要点三：**
[画面：___]
___

### [45-55秒] 总结收尾
> （金句/宗门梗）

___

### [55-60秒] CTA
> （关注/评论/收藏引导）

___

## 标题
___

## 描述文案
___

## 话题标签
#___ #___ #___
""",
    "xiaohongshu_note": """# 小红书笔记文案

## 基本信息
- 文案编号: {copy_id}
- 内容支柱: {pillar}
- 关联内容编号: ___

## 标题（15-20字，含数字或疑问句）
___

## 正文

### 第一段：痛点共鸣（2-3句）
___

### 干货要点

1. ___
2. ___
3. ___
4. ___
5. ___

### 结尾：互动引导
___

## 话题标签
#___ #___ #___
""",
    "weibo_post": """# 微博博文

## 基本信息
- 文案编号: {copy_id}
- 内容支柱: {pillar}

## 正文（140字内）

> Hook（1句话）：___
>
> 核心观点（2-3句）：___
>
> 互动提问：___

## 话题标签
#___ #___
""",
    "bilibili_script": """# B站长视频脚本

## 基本信息
- 文案编号: {copy_id}
- 内容支柱: {pillar}
- 预估时长: ___分___秒
- 关联内容编号: ___

## 标题（10-25字，信息量大，引发好奇心）
___

## 视频描述（100-300字）
___

## 脚本正文

### [0:00-0:30] 开场 Hook
> （信息量大的开场白，直接抛出核心问题/结论）

___

### [0:30-2:00] 背景铺垫
> （为什么这件事重要/常见误区/大家都在犯的错）

___

### [2:00-6:00] 核心内容

**知识点一：**
[画面描述：___]
___

**知识点二：**
[画面描述：___]
___

**知识点三：**
[画面描述：___]
___

### [6:00-7:30] 实操演示/总结
> （实际动作演示 + 易错点提醒）

___

### [7:30-8:00] 收尾 CTA
> （求三连：一键三连 + 收藏备用 + 评论区见）

___

## 弹幕互动点设计
- [时间点1] 弹幕引导: ___
- [时间点2] 弹幕引导: ___

## 话题标签
#___ #___ #___
""",
    "wechat_article": """# 微信公众号推文

## 基本信息
- 文案编号: {copy_id}
- 内容支柱: {pillar}
- 关联内容编号: ___

## 标题（15-25字，制造好奇心/紧迫感）
___

## 摘要（显示在订阅号消息列表，50字内）
___

## 正文

### 开头（制造好奇心，前100字决定打开率）
___

### 第一部分：问题/痛点
> （场景化描述读者的困扰）

___

### 第二部分：核心观点/干货
> （多图文穿插，每300字建议配一张图）

**要点一：**
___

**要点二：**
___

**要点三：**
___

### 第三部分：实操建议/案例
> （具体可执行的步骤或真实案例）

___

### 结尾：总结+CTA
> （金句收尾 + 在看/分享引导 + 关注引导）

___

## 封面图文案建议
___

## 阅读原文链接（如有）
___
""",
    "commercial_copy": """# 商务合作文案

## 基本信息
- 文案编号: {copy_id}
- 内容支柱: {pillar}
- 合作品牌: ___
- 合作形式: 纯佣 / CPS / 定制内容 / 品牌植入
- 目标平台: ___

## 合作方要求
- 必须露出的信息: ___
- 禁止提及的内容: ___
- 品牌 Slogan: ___

## 文案正文

### Hook 开场（自然引入，不能硬广）
> （从自身经历/痛点切入，自然过渡到产品）

___

### 使用场景/个人体验
> （真实使用感受，结合训练/生活场景）

___

### 产品核心卖点（2-3个）
**卖点一：**
___

**卖点二：**
___

### 行动号召（优惠/链接/口令）
___

## 自检清单
- [ ] 内容自然，不像硬广
- [ ] 品牌露出符合合作方要求
- [ ] 无夸大/绝对化表述
- [ ] 已标注「广告」/「合作」标识
- [ ] 宗门术语使用合规（商务合作中低强度）
- [ ] 未提及竞品

## 备注
___
""",
}


def load_config():
    """加载平台配置"""
    config_path = CONFIG_DIR / "platforms.yaml"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


def ensure_data_dir():
    """确保数据目录存在"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "草稿").mkdir(exist_ok=True)
    (DATA_DIR / "已发布").mkdir(exist_ok=True)
    (DATA_DIR / "归档").mkdir(exist_ok=True)
    (DATA_DIR / "金句库").mkdir(exist_ok=True)
    (DATA_DIR / "素材库").mkdir(exist_ok=True)


def generate_copy_id():
    """生成文案编号"""
    today = datetime.now().strftime("%Y%m%d")
    ensure_data_dir()
    existing = list(DATA_DIR.glob(f"**/*{today}*.json"))
    seq = len(existing) + 1
    return f"CP-{today}-{seq:03d}"


def get_template(copy_type, platform):
    """获取对应模板"""
    key = f"{platform}_{copy_type}"
    if key in TEMPLATES:
        return TEMPLATES[key]
    # 通用模板
    type_name = COPY_TYPES.get(copy_type, copy_type)
    platform_name = PLATFORM_NAMES.get(platform, platform)
    return f"""# {platform_name} - {type_name}

## 基本信息
- 文案编号: {{copy_id}}
- 内容支柱: {{pillar}}
- 平台: {platform_name}
- 类型: {type_name}

## 正文
___

## 备注
___
"""


@click.group()
def cli():
    """文案部门 CLI 工具 — 文案创建、管理、审核和话术库维护"""
    pass


@cli.command()
@click.option("--type", "copy_type", required=True,
              type=click.Choice(list(COPY_TYPES.keys())),
              help="文案类型")
@click.option("--platform", required=True,
              type=click.Choice(PLATFORMS),
              help="目标平台")
@click.option("--pillar", default="training",
              type=click.Choice(list(CONTENT_PILLARS.keys())),
              help="内容支柱")
def create(copy_type, platform, pillar):
    """创建新文案草稿"""
    ensure_data_dir()
    copy_id = generate_copy_id()
    template = get_template(copy_type, platform)
    pillar_name = CONTENT_PILLARS.get(pillar, pillar)

    content = template.format(copy_id=copy_id, pillar=pillar_name)

    # 保存元数据
    metadata = {
        "copy_id": copy_id,
        "type": copy_type,
        "type_name": COPY_TYPES[copy_type],
        "platform": platform,
        "platform_name": PLATFORM_NAMES[platform],
        "pillar": pillar,
        "pillar_name": pillar_name,
        "status": "draft",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "author": "",
        "reviewer": "",
        "revision_count": 0,
    }

    meta_path = DATA_DIR / "草稿" / f"{copy_id}.json"
    draft_path = DATA_DIR / "草稿" / f"{copy_id}.md"

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(content)

    console.print(Panel(
        f"[bold green]文案草稿已创建[/bold green]\n\n"
        f"编号: [bold]{copy_id}[/bold]\n"
        f"类型: {COPY_TYPES[copy_type]}\n"
        f"平台: {PLATFORM_NAMES[platform]}\n"
        f"支柱: {pillar_name}\n\n"
        f"草稿文件: {draft_path}\n"
        f"元数据: {meta_path}",
        title="新文案",
    ))


@cli.command("list")
@click.option("--status", type=click.Choice(STATUSES), default=None,
              help="按状态筛选")
@click.option("--platform", type=click.Choice(PLATFORMS), default=None,
              help="按平台筛选")
@click.option("--type", "copy_type", type=click.Choice(list(COPY_TYPES.keys())),
              default=None, help="按类型筛选")
def list_copies(status, platform, copy_type):
    """列出文案列表"""
    ensure_data_dir()
    all_files = list(DATA_DIR.rglob("*.json"))

    if not all_files:
        console.print("[yellow]暂无文案记录[/yellow]")
        return

    table = Table(title="文案列表")
    table.add_column("编号", style="bold")
    table.add_column("类型")
    table.add_column("平台")
    table.add_column("支柱")
    table.add_column("状态")
    table.add_column("创建时间")
    table.add_column("修改轮次")

    for fp in sorted(all_files):
        with open(fp, "r", encoding="utf-8") as f:
            meta = json.load(f)

        if status and meta.get("status") != status:
            continue
        if platform and meta.get("platform") != platform:
            continue
        if copy_type and meta.get("type") != copy_type:
            continue

        status_label = STATUS_LABELS.get(meta.get("status", ""), meta.get("status", ""))
        table.add_row(
            meta.get("copy_id", ""),
            meta.get("type_name", ""),
            meta.get("platform_name", ""),
            meta.get("pillar_name", ""),
            status_label,
            meta.get("created_at", "")[:10],
            str(meta.get("revision_count", 0)),
        )

    console.print(table)


@cli.command()
@click.option("--id", "copy_id", required=True, help="文案编号")
def review(copy_id):
    """查看文案详情并进入审核"""
    ensure_data_dir()
    meta_files = list(DATA_DIR.rglob(f"{copy_id}.json"))

    if not meta_files:
        console.print(f"[red]未找到文案: {copy_id}[/red]")
        return

    meta_path = meta_files[0]
    draft_path = meta_path.with_suffix(".md")

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    # 显示元数据
    console.print(Panel(
        f"编号: [bold]{meta['copy_id']}[/bold]\n"
        f"类型: {meta.get('type_name', '')}\n"
        f"平台: {meta.get('platform_name', '')}\n"
        f"支柱: {meta.get('pillar_name', '')}\n"
        f"状态: {STATUS_LABELS.get(meta.get('status', ''), '')}\n"
        f"修改轮次: {meta.get('revision_count', 0)}\n"
        f"创建时间: {meta.get('created_at', '')}\n"
        f"更新时间: {meta.get('updated_at', '')}",
        title=f"文案详情 - {copy_id}",
    ))

    # 显示文案内容
    if draft_path.exists():
        with open(draft_path, "r", encoding="utf-8") as f:
            content = f.read()
        console.print(Panel(Markdown(content), title="文案内容"))

    # 更新状态为审核中
    if meta.get("status") == "draft":
        meta["status"] = "review"
        meta["updated_at"] = datetime.now().isoformat()
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        console.print("[green]状态已更新为「审核中」[/green]")


@cli.command()
@click.option("--id", "copy_id", required=True, help="文案编号")
def approve(copy_id):
    """审核通过文案"""
    ensure_data_dir()
    meta_files = list(DATA_DIR.rglob(f"{copy_id}.json"))

    if not meta_files:
        console.print(f"[red]未找到文案: {copy_id}[/red]")
        return

    meta_path = meta_files[0]
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    meta["status"] = "approved"
    meta["updated_at"] = datetime.now().isoformat()

    # 移动到 approved 目录
    approved_path = DATA_DIR / "已发布" / f"{copy_id}.json"
    with open(approved_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # 移动 markdown 文件
    draft_md = meta_path.with_suffix(".md")
    if draft_md.exists():
        approved_md = DATA_DIR / "已发布" / f"{copy_id}.md"
        approved_md.write_text(draft_md.read_text(encoding="utf-8"), encoding="utf-8")

    console.print(Panel(
        f"[bold green]文案已审核通过[/bold green]\n\n"
        f"编号: {copy_id}\n"
        f"类型: {meta.get('type_name', '')}\n"
        f"平台: {meta.get('platform_name', '')}",
        title="审核通过",
    ))


@cli.command()
@click.option("--pillar", type=click.Choice(list(CONTENT_PILLARS.keys())),
              default=None, help="按内容支柱筛选")
@click.option("--platform", type=click.Choice(PLATFORMS),
              default=None, help="按平台筛选")
def library(pillar, platform):
    """查看文案话术库"""
    ensure_data_dir()
    library_dir = DATA_DIR / "素材库"

    table = Table(title="文案话术库")
    table.add_column("分类", style="bold")
    table.add_column("平台")
    table.add_column("内容摘要")
    table.add_column("互动数据")

    library_files = list(library_dir.rglob("*.json"))

    if not library_files:
        console.print("[yellow]话术库暂无内容。高互动文案审核通过后会自动收录。[/yellow]")
        console.print("\n[dim]手动添加：将 JSON 文件放入 数据/文案/素材库/ 目录[/dim]")
        return

    for fp in sorted(library_files):
        with open(fp, "r", encoding="utf-8") as f:
            entry = json.load(f)
        if pillar and entry.get("pillar") != pillar:
            continue
        if platform and entry.get("platform") != platform:
            continue
        table.add_row(
            CONTENT_PILLARS.get(entry.get("pillar", ""), ""),
            PLATFORM_NAMES.get(entry.get("platform", ""), ""),
            entry.get("summary", "")[:40],
            entry.get("engagement", ""),
        )

    console.print(table)


@cli.command()
@click.option("--days", default=30, help="统计天数")
def stats(days):
    """文案部门数据统计"""
    ensure_data_dir()
    cutoff = datetime.now() - timedelta(days=days)
    all_files = list(DATA_DIR.rglob("*.json"))

    total = 0
    by_status = {}
    by_platform = {}
    by_type = {}

    for fp in all_files:
        with open(fp, "r", encoding="utf-8") as f:
            meta = json.load(f)
        created = meta.get("created_at", "")
        if created and datetime.fromisoformat(created) < cutoff:
            continue

        total += 1
        s = meta.get("status", "unknown")
        by_status[s] = by_status.get(s, 0) + 1
        p = meta.get("platform_name", "unknown")
        by_platform[p] = by_platform.get(p, 0) + 1
        t = meta.get("type_name", "unknown")
        by_type[t] = by_type.get(t, 0) + 1

    console.print(Panel(
        f"[bold]近 {days} 天文案统计[/bold]\n\n"
        f"总数: {total}\n\n"
        f"[bold]按状态:[/bold]\n" +
        "\n".join(f"  {STATUS_LABELS.get(k, k)}: {v}" for k, v in sorted(by_status.items())) +
        f"\n\n[bold]按平台:[/bold]\n" +
        "\n".join(f"  {k}: {v}" for k, v in sorted(by_platform.items())) +
        f"\n\n[bold]按类型:[/bold]\n" +
        "\n".join(f"  {k}: {v}" for k, v in sorted(by_type.items())),
        title="文案部门统计",
    ))


if __name__ == "__main__":
    cli()
