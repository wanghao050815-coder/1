"""Librarian Agent — 素材库管理 Agent，入库分析 + 风格提炼。

用法：
    from tools.agents.librarian import LibrarianAgent
    agent = LibrarianAgent()
    result = agent.ingest(raw_text, engagement="点赞1.2w")
    result = agent.analyze_style()
"""

import json
from datetime import datetime
from pathlib import Path

from .base import BaseAgent


class LibrarianAgent(BaseAgent):
    """素材库管理 Agent：文案入库打标、风格 DNA 提炼、日常入库闭环。"""

    REQUIRED_DOCS = ["brand_voice", "super_ip", "copywriting_sop", "content_pillars"]

    def _build_system_prompt(self) -> str:
        return f"""你是「邪修宗」内容团队的素材库管理 Agent（文案馆主）。
你的职责是分析历史文案、提取结构化信息、提炼写作风格特征。

## 品牌规范

{self._docs_block("brand_voice", "品牌声音指南")}

{self._docs_block("super_ip", "宗门IP手册")}

{self._docs_block("copywriting_sop", "文案SOP")}

{self._docs_block("content_pillars", "内容支柱体系")}

## 你的核心能力

### 1. 文案入库分析
收到原始文案后，你需要识别并输出以下结构化信息（JSON 格式）：
- platform: 判断属于哪个平台（douyin/xiaohongshu/weibo/bilibili/wechat/unknown）
- pillar: 内容支柱（training/nutrition/lifestyle/trending/brand/sect_ip）
- type: 文案类型（script/title/note/weibo_post/wechat_article/comment_template）
- title: 提取或概括标题
- hook: 提取开头钩子（前1-2句）
- body: 正文主体
- cta: 行动号召
- hashtags: 话题标签列表
- sect_terms_used: 使用的宗门术语列表
- quality_score: 按五维度打分（1-10）
  - accuracy: 信息准确性
  - brand_fit: 品牌一致性
  - platform_fit: 平台适配度
  - engagement_drive: 互动引导力
  - creativity: 创意与差异化
- style_notes: 写作风格特征简要分析（钩子类型、句式、节奏、情绪基调）

### 2. 风格提炼分析
分析整个素材库后，提炼以下维度的写作 DNA：
- 钩子偏好分布（哪类钩子用最多，效果如何）
- 句式特征（句长、常用句式、节奏模式）
- 词汇指纹（高频词、标志性表达、口头禅）
- 宗门术语使用频率和方式
- CTA 类型分布
- 平台间风格差异
- 情绪基调倾向

## 输出规范
- 入库分析：必须输出合法 JSON
- 风格分析：输出 Markdown 格式的风格 DNA 手册
- 所有评分必须基于品牌声音指南和 SOP 标准，不能随意打高分
"""

    def ingest(self, raw_text: str, source_file: str = "", engagement: str = "") -> str:
        """分析单条文案，输出结构化 JSON 并保存到素材库。"""
        engagement_info = f"\n\n互动数据: {engagement}" if engagement else ""

        user_msg = f"""请分析以下原始文案，输出结构化 JSON。

## 原始文案
{raw_text}
{engagement_info}

请严格按照以下 JSON 结构输出（不要输出其他内容，只输出 JSON）：

```json
{{
  "source_file": "{source_file or 'manual_input'}",
  "platform": "判断平台",
  "pillar": "判断支柱",
  "type": "判断类型",
  "title": "提取标题",
  "hook": "提取钩子",
  "body": "正文主体",
  "cta": "行动号召",
  "hashtags": ["标签1", "标签2"],
  "sect_terms_used": ["术语1"],
  "engagement": {{"raw": "{engagement or '未提供'}"}},
  "quality_score": {{
    "accuracy": 0,
    "brand_fit": 0,
    "platform_fit": 0,
    "engagement_drive": 0,
    "creativity": 0
  }},
  "style_notes": "风格特征分析",
  "ingested_at": "{datetime.now().strftime('%Y-%m-%d')}"
}}
```"""

        result = self.run(user_msg)

        # 尝试提取 JSON 并保存
        json_data = self._extract_json(result)
        if json_data:
            saved_path = self._save_to_library(json_data)
            return f"入库成功: {saved_path}\n\n{result}"

        return f"分析完成（需手动保存）:\n\n{result}"

    def ingest_batch(self, directory: str) -> str:
        """批量扫描目录，逐条分析入库。"""
        dir_path = Path(directory)
        if not dir_path.exists():
            return f"目录不存在: {directory}"

        files = list(dir_path.glob("*.md")) + list(dir_path.glob("*.txt"))
        if not files:
            return f"目录中没有找到 .md 或 .txt 文件: {directory}"

        results = []
        for f in sorted(files):
            if f.name.startswith("."):
                continue
            raw_text = f.read_text(encoding="utf-8")
            result = self.ingest(raw_text, source_file=f.name)
            results.append(f"### {f.name}\n{result}")

        summary = f"## 批量入库完成\n\n共处理 {len(results)} 个文件\n\n"
        return summary + "\n\n---\n\n".join(results)

    def analyze_style(self) -> str:
        """分析整个素材库，提炼写作风格 DNA。"""
        library_content = self._load_full_library()
        if not library_content:
            return "素材库为空，请先用 `ingest` 命令入库历史文案。"

        user_msg = f"""请分析以下素材库中的所有文案，提炼邪健仙的写作风格 DNA。

## 素材库内容
{library_content}

---

请输出完整的「写作风格 DNA」手册，结构如下：

# 邪健仙·写作风格 DNA

## 钩子偏好
（统计各类钩子使用频率和效果，给出比例）

## 句式特征
（平均句长、常用句式模式、节奏特点、标点习惯）

## 词汇指纹
（高频词 Top 20、标志性表达/口头禅、专业术语使用方式）

## 宗门术语使用模式
（平均每条几个、常用术语排名、植入方式偏好）

## CTA 类型分布
（关注/互动/保存/话题各占比例）

## 情绪基调
（整体倾向、不同支柱下的基调差异）

## 平台风格差异
（各平台的写法有什么不同）

## 独特优势
（与普通健身博主相比，这些文案最突出的特点是什么）

## 改进建议
（基于数据分析，哪些方面可以优化）

所有分析必须基于实际数据，引用具体例子。"""

        result = self.run(user_msg)

        # 保存风格 DNA
        dna_path = self.repo_root / "数据" / "文案" / "风格DNA.md"
        dna_path.write_text(result, encoding="utf-8")

        return f"{result}\n\n---\n📁 风格 DNA 已保存: {dna_path}"

    def approve_to_library(self, draft_text: str, source_file: str = "", engagement: str = "") -> str:
        """将已审核的文案分析后移入素材库。"""
        return self.ingest(draft_text, source_file=source_file, engagement=engagement)

    # ── 内部工具方法 ──────────────────────────────────

    def _load_full_library(self) -> str:
        """加载素材库全部内容（md + json）。"""
        library_dir = self.repo_root / "数据" / "文案" / "素材库"
        if not library_dir.exists():
            return ""

        texts = []
        # 加载 JSON 文件
        for f in sorted(library_dir.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                entry = f"### [{data.get('platform', '?')}] {data.get('title', f.stem)}\n"
                entry += f"- 支柱: {data.get('pillar', '?')} | 类型: {data.get('type', '?')}\n"
                entry += f"- 钩子: {data.get('hook', '')}\n"
                entry += f"- CTA: {data.get('cta', '')}\n"
                entry += f"- 互动: {json.dumps(data.get('engagement', {}), ensure_ascii=False)}\n"
                entry += f"- 评分: {json.dumps(data.get('quality_score', {}), ensure_ascii=False)}\n"
                entry += f"- 风格: {data.get('style_notes', '')}\n"
                entry += f"\n{data.get('body', '')}"
                texts.append(entry)
            except (json.JSONDecodeError, KeyError):
                texts.append(f"### {f.stem}\n{f.read_text(encoding='utf-8')}")

        # 加载 MD 文件（跳过 README）
        for f in sorted(library_dir.glob("*.md")):
            if f.name.lower() == "readme.md":
                continue
            texts.append(f"### {f.stem}\n{f.read_text(encoding='utf-8')}")

        return "\n\n---\n\n".join(texts) if texts else ""

    def _extract_json(self, text: str) -> dict | None:
        """从 Agent 输出中提取 JSON。"""
        # 尝试从 ```json ... ``` 代码块提取
        import re
        match = re.search(r"```json\s*\n(.*?)\n\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # 尝试直接解析整个文本
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        return None

    def _save_to_library(self, data: dict) -> Path:
        """将结构化数据保存到素材库。"""
        library_dir = self.repo_root / "数据" / "文案" / "素材库"
        library_dir.mkdir(parents=True, exist_ok=True)

        platform = data.get("platform", "unknown")
        # 从标题生成简短关键词
        title = data.get("title", "untitled")
        keyword = title[:20].replace(" ", "_").replace("/", "_")
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{platform}_{keyword}_{ts}.json"

        filepath = library_dir / filename
        filepath.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return filepath
