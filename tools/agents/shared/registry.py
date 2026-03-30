"""Agent 注册表 — 按需加载 Agent，最大化上下文隔离。

每个 Agent 只加载自己需要的文档和数据，避免不必要的 token 开销。
"""

# Agent 类型 → 导入路径映射
AGENT_REGISTRY = {
    "copywriter": {
        "module": "tools.agents.copywriter",
        "class": "CopywriterAgent",
        "description": "文案生成 Agent",
        "required_docs": ["brand_voice", "super_ip", "copywriting_sop", "douyin_playbook", "content_pillars"],
        "loads_library": True,
        "loads_style_dna": True,
    },
    "operations": {
        "module": "tools.agents.operations",
        "class": "OperationsAgent",
        "description": "运营策略 Agent",
        "required_docs": ["brand_voice", "content_pillars"],
        "loads_library": False,
        "loads_style_dna": False,
    },
    "planner": {
        "module": "tools.agents.planner",
        "class": "PlannerAgent",
        "description": "内容规划 Agent",
        "required_docs": ["content_pillars", "copywriting_sop"],
        "loads_library": False,
        "loads_style_dna": False,
    },
    "community": {
        "module": "tools.agents.community",
        "class": "CommunityAgent",
        "description": "社区管理 Agent",
        "required_docs": ["brand_voice", "super_ip"],
        "loads_library": False,
        "loads_style_dna": False,
    },
    "analytics": {
        "module": "tools.agents.analytics",
        "class": "AnalyticsAgent",
        "description": "数据分析 Agent",
        "required_docs": ["content_pillars"],
        "loads_library": False,
        "loads_style_dna": False,
    },
    "publisher": {
        "module": "tools.agents.publisher",
        "class": "PublisherAgent",
        "description": "发布检查 Agent",
        "required_docs": ["brand_voice"],
        "loads_library": False,
        "loads_style_dna": False,
    },
    "librarian": {
        "module": "tools.agents.librarian",
        "class": "LibrarianAgent",
        "description": "素材库管理 Agent",
        "required_docs": ["brand_voice", "copywriting_sop"],
        "loads_library": True,
        "loads_style_dna": True,
    },
    "coach": {
        "module": "tools.agents.coach",
        "class": "CoachAgent",
        "description": "私教计划 Agent",
        "required_docs": ["brand_voice", "coach_standards"],
        "loads_library": False,
        "loads_style_dna": False,
    },
}


def get_agent_info(agent_type: str) -> dict | None:
    """获取 Agent 的注册信息。"""
    return AGENT_REGISTRY.get(agent_type)


def list_agents() -> list[dict]:
    """列出所有已注册的 Agent。"""
    return [
        {"type": k, **v}
        for k, v in AGENT_REGISTRY.items()
    ]


def estimate_token_usage(agent_type: str) -> str:
    """估算 Agent 的 token 使用量级。

    基于加载的文档数量和库资源给出粗略估算。
    """
    info = AGENT_REGISTRY.get(agent_type)
    if not info:
        return "未知"

    doc_count = len(info["required_docs"])
    loads_lib = info["loads_library"]
    loads_dna = info["loads_style_dna"]

    # 粗略估算
    base_tokens = 2000  # system prompt 基础
    doc_tokens = doc_count * 3000  # 每份文档约 3000 tokens
    lib_tokens = 5000 if loads_lib else 0  # 库摘要约 5000 tokens
    dna_tokens = 2000 if loads_dna else 0  # 风格DNA约 2000 tokens

    total = base_tokens + doc_tokens + lib_tokens + dna_tokens

    if total < 10000:
        return f"低 (~{total:,} tokens)"
    elif total < 20000:
        return f"中 (~{total:,} tokens)"
    else:
        return f"高 (~{total:,} tokens)"
