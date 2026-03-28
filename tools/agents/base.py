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
        "brand_voice": "docs/brand/brand-voice-guide.md",
        "content_pillars": "docs/brand/content-pillars.md",
        "super_ip": "docs/brand/super-ip.md",
        "visual_identity": "docs/brand/visual-identity.md",
        "copywriting_sop": "docs/copywriting/copywriting-sop.md",
        "douyin_playbook": "docs/platforms/douyin-playbook.md",
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
        return self._load_doc(f"tools/config/{name}.yaml")

    def _load_library(self) -> str:
        """加载历史高互动文案库。"""
        library_dir = self.repo_root / "data" / "copywriting" / "library"
        if not library_dir.exists():
            return ""
        texts = []
        for f in sorted(library_dir.glob("*.md")):
            texts.append(f"### {f.stem}\n{f.read_text(encoding='utf-8')}")
        return "\n\n---\n\n".join(texts) if texts else ""

    def _load_calendar_week(self, week: str = None) -> str:
        """加载指定周的 content calendar。"""
        cal_dir = self.repo_root / "data" / "content_calendar"
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
        drafts_dir = self.repo_root / "data" / "copywriting" / "drafts"
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

    @staticmethod
    def today() -> str:
        return datetime.now().strftime("%Y-%m-%d")
