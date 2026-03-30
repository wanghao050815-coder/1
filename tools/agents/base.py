"""Base agent class — 所有 Agent 的基础设施。"""

import json
import os
from datetime import datetime
from pathlib import Path

from anthropic import Anthropic

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class BaseAgent:
    """Base class for all content team agents."""

    # 子类覆盖：需要注入 system prompt 的品牌文档 key
    REQUIRED_DOCS: list[str] = []

    # 文档 key → 相对路径映射
    DOC_MAP = {
        "brand_voice": "文档/品牌/brand-voice-guide.md",
        "content_pillars": "文档/品牌/content-pillars.md",
        "super_ip": "文档/品牌/super-ip.md",
        "visual_identity": "文档/品牌/visual-identity.md",
        "copywriting_sop": "文档/文案/copywriting-sop.md",
        "douyin_playbook": "文档/平台/douyin-playbook.md",
        "coach_standards": "文档/会员服务/训练标准.md",
    }

    def __init__(self, model: str = None):
        self.client = Anthropic()
        self.model = model or os.getenv("AGENT_MODEL", "claude-sonnet-4-20250514")
        self.repo_root = REPO_ROOT
        self._doc_cache: dict[str, str] = {}

    # ── 文档加载 ────────────────────────────────────────

    def _load_doc(self, relative_path: str) -> str:
        path = self.repo_root / relative_path
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def _load_brand_docs(self) -> dict[str, str]:
        if not self._doc_cache:
            for key in self.REQUIRED_DOCS:
                if key in self.DOC_MAP:
                    self._doc_cache[key] = self._load_doc(self.DOC_MAP[key])
        return self._doc_cache

    def _load_config(self, name: str) -> str:
        return self._load_doc(f"tools/配置/{name}.yaml")

    def _load_library(self, topic: str = "", platform: str = "",
                       pillar: str = "", max_entries: int = 30) -> str:
        """加载历史高互动文案库（支持相关性检索和分类索引）。

        Args:
            topic: 当前选题关键词，用于相关性筛选
            platform: 目标平台，用于平台筛选
            pillar: 内容支柱，用于分类筛选
            max_entries: 最大返回条目数（控制 token 开销）
        """
        import json as _json
        library_dir = self.repo_root / "数据" / "文案" / "素材库"
        if not library_dir.exists():
            return ""

        # 加载主库文件 copy-library.json
        main_lib = library_dir / "copy-library.json"
        entries = []
        if main_lib.exists():
            try:
                data = _json.loads(main_lib.read_text(encoding="utf-8"))
                entries = data.get("entries", [])
            except (_json.JSONDecodeError, KeyError):
                pass

        if not entries:
            return ""

        # 相关性筛选：按 platform、pillar、topic 关键词过滤
        filtered = entries
        if platform:
            platform_match = [e for e in filtered if e.get("platform", "") == platform]
            if platform_match:
                filtered = platform_match
        if pillar:
            pillar_match = [e for e in filtered if e.get("pillar", "") == pillar]
            if pillar_match:
                filtered = pillar_match
        if topic:
            keywords = [w for w in topic.split() if len(w) > 1]
            if keywords:
                topic_match = [
                    e for e in filtered
                    if any(kw in e.get("title", "") or kw in e.get("content", "")
                           or kw in e.get("category", "") for kw in keywords)
                ]
                if topic_match:
                    filtered = topic_match

        # 按互动数据排序（likes 降序），取 top N
        filtered.sort(key=lambda x: x.get("likes", 0), reverse=True)
        top_entries = filtered[:max_entries]

        # 格式化为紧凑的文本摘要
        texts = []
        for e in top_entries:
            entry = f"### [{e.get('category', '?')}] {e.get('title', '无标题')}"
            entry += f"\n赞: {e.get('likes', 0):,} | 评: {e.get('comments', 0):,} | 转: {e.get('shares', 0):,}"
            if e.get("hook_type"):
                entry += f"\n钩子类型: {e['hook_type']}"
            if e.get("cta_type"):
                entry += f"\nCTA类型: {e['cta_type']}"
            content = e.get("content", "")
            if len(content) > 150:
                content = content[:150] + "..."
            entry += f"\n正文: {content}"
            texts.append(entry)

        header = f"（共 {len(entries)} 条，筛选后展示 {len(top_entries)} 条高互动文案）"
        return header + "\n\n" + "\n\n---\n\n".join(texts)

    def _load_style_dna(self) -> str:
        """加载风格 DNA 手册（如存在）。"""
        path = self.repo_root / "数据" / "文案" / "风格DNA.md"
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def _load_calendar_week(self, week: str = None) -> str:
        """加载指定周的 content calendar。"""
        cal_dir = self.repo_root / "数据" / "内容日历"
        if not cal_dir.exists():
            return ""
        if week:
            target = cal_dir / f"{week}-topics.md"
            if target.exists():
                return target.read_text(encoding="utf-8")
        # 返回最新的
        files = sorted(cal_dir.glob("*-topics.md"), reverse=True)
        return files[0].read_text(encoding="utf-8") if files else ""

    # ── System prompt 构建 ────────────────────────────

    def _build_system_prompt(self) -> str:
        """子类覆盖此方法构建完整 system prompt。"""
        raise NotImplementedError

    def _docs_block(self, key: str, title: str = None) -> str:
        """将文档包装成 XML block 注入 prompt。"""
        docs = self._load_brand_docs()
        content = docs.get(key, "")
        if not content:
            return ""
        tag = title or key
        return f"<{tag}>\n{content}\n</{tag}>"

    # ── API 调用 ──────────────────────────────────────

    def run(self, user_message: str) -> str:
        system_prompt = self._build_system_prompt()
        response = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text

    def run_with_history(self, messages: list[dict], system_prompt: str = None) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            system=system_prompt or self._build_system_prompt(),
            messages=messages,
        )
        return response.content[0].text

    # ── 工具方法 ──────────────────────────────────────

    def save_draft(self, content: str, metadata: dict, filename: str = None) -> Path:
        """保存文案草稿到 data/copywriting/drafts/。"""
        drafts_dir = self.repo_root / "数据" / "文案" / "草稿"
        drafts_dir.mkdir(parents=True, exist_ok=True)

        if not filename:
            ts = datetime.now().strftime("%Y%m%d-%H%M%S")
            platform = metadata.get("platform", "multi")
            pillar = metadata.get("pillar", "general")
            filename = f"CP-{ts}-{platform}-{pillar}.md"

        filepath = drafts_dir / filename

        header = "---\n"
        for k, v in metadata.items():
            header += f"{k}: {v}\n"
        header += f"created: {datetime.now().isoformat()}\n"
        header += "status: draft\n---\n\n"

        filepath.write_text(header + content, encoding="utf-8")
        return filepath

    def save_member_plan(self, username: str, plan_type: str, content: str) -> Path:
        """保存会员计划到 数据/会员服务/计划输出/{用户名}_{周}/。"""
        week = datetime.now().strftime("%YW%W")
        output_dir = self.repo_root / "数据" / "会员服务" / "计划输出" / f"{username}_{week}"
        output_dir.mkdir(parents=True, exist_ok=True)

        filename_map = {
            "warmup": "体态热身.md",
            "training": "训练计划.md",
            "diet": "饮食方案.md",
        }
        filename = filename_map.get(plan_type, f"{plan_type}.md")
        filepath = output_dir / filename
        filepath.write_text(content, encoding="utf-8")
        return filepath

    @staticmethod
    def today() -> str:
        return datetime.now().strftime("%Y-%m-%d")
