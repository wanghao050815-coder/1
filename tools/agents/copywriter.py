"""Copywriter Agent — 文案 Agent，核心生成模块。

用法：
    from tools.agents.copywriter import CopywriterAgent
    agent = CopywriterAgent()
    result = agent.generate(platform="douyin", pillar="training", topic="跑步膝盖疼")
"""

from .base import BaseAgent


class CopywriterAgent(BaseAgent):
    """多平台文案生成 Agent。

    注入文档：brand_voice（全文）、super_ip（话语体系+运营规范）、
    copywriting_sop（平台公式）、douyin_playbook（钩子+文案结构）、content_pillars。
    """

    REQUIRED_DOCS = [
        "brand_voice",
        "super_ip",
        "copywriting_sop",
        "douyin_playbook",
        "content_pillars",
    ]

    # 各平台文案规格
    PLATFORM_SPECS = {
        "douyin": {
            "title_len": "10-20字",
            "desc_len": "50-150字",
            "hashtags": "最多5个",
            "key": "完播率为王，前3秒钩子决定生死",
            "structure": "钩子(0-3s) → 问题提出(3-10s) → 核心内容(10-45s) → 总结(45-55s) → CTA(55-60s)",
        },
        "xiaohongshu": {
            "title_len": "15-20字，含数字或问句",
            "desc_len": "300-800字",
            "hashtags": "最多10个",
            "key": "收藏率为王，实用干货+结构清晰",
            "structure": "标题(数字+痛点) → 共情开头 → 3-5个要点(带emoji分隔) → 互动引导",
        },
        "weibo": {
            "title_len": "无独立标题",
            "desc_len": "140字以内",
            "hashtags": "2-3个",
            "key": "碎片化传播，话题感+转发欲",
            "structure": "钩子 → 核心观点 → 互动提问 → 话题标签",
        },
        "bilibili": {
            "title_len": "10-25字",
            "desc_len": "100-300字",
            "hashtags": "最多5个",
            "key": "投币率=内容质量信号，深度内容+弹幕互动",
            "structure": "标题(信息量大) → 时间轴描述 → 核心知识点 → 求三连CTA",
        },
        "wechat": {
            "title_len": "15-25字，制造好奇心",
            "desc_len": "按文章长度定",
            "hashtags": "无",
            "key": "打开率为王，标题决定一切",
            "structure": "悬念标题 → 好奇心开头 → 多图文穿插 → 深度总结 → 在看/分享CTA",
        },
    }

    # 宗门术语植入强度
    SECT_INTENSITY = {
        "training": ("低", "术语替换2-3个 + 片尾口号「邪修正道，百炼飞仙」"),
        "nutrition": ("低", "术语替换2-3个 + 片尾口号"),
        "lifestyle": ("中", "自然使用弟子/修炼/闭关等称呼，4-5个术语"),
        "trending": ("低", "仅片尾口号，热点内容以通用性为主"),
        "brand": ("低", "仅片尾品牌露出，不混用宗门和商业"),
        "sect_ip": ("高", "大量使用宗门体系，入门仪式、宗训引用、弟子互动"),
    }

    def _build_system_prompt(self, topic: str = "", platform: str = "",
                               pillar: str = "") -> str:
        library = self._load_library(topic=topic, platform=platform, pillar=pillar)
        library_block = f"\n<copy_library>\n{library}\n</copy_library>" if library else ""
        style_dna = self._load_style_dna()
        style_dna_block = f"\n<写作风格DNA>\n{style_dna}\n</写作风格DNA>" if style_dna else ""

        return f"""你是「邪修宗」内容团队的首席文案 Agent。你的任务是根据选题 Brief 生成符合品牌调性的多平台文案。

## 你的核心身份
- 你为健身博主「邪健仙」撰写文案
- 邪健仙的人设：硬核教练 + 亲切学长 + 热血掌门 三位一体
- 核心调性：「我走的是野路子，但每一步都验证过」
- 宗门口号：「邪修正道，百炼飞仙」

## 品牌规范文档（必须严格遵守）

{self._docs_block("brand_voice", "品牌声音指南")}

{self._docs_block("super_ip", "宗门IP手册")}

{self._docs_block("copywriting_sop", "文案SOP")}

{self._docs_block("douyin_playbook", "抖音运营手册")}

{self._docs_block("content_pillars", "内容支柱体系")}
{library_block}
{style_dna_block}

## 输出要求

**重要：如果存在「写作风格 DNA」，你必须模仿其中记录的写作习惯（钩子偏好、句式特征、词汇指纹、CTA 模式）。品牌规范是硬约束，风格 DNA 是软约束——在不违反品牌规范的前提下，尽可能贴近创作者的个人风格。**

### 对于每个平台，你必须输出：
1. **标题** — 严格遵守字数限制
2. **描述/正文** — 按平台公式结构撰写
3. **开头钩子** — 前3秒/首句，使用经过验证的钩子公式
4. **话题标签** — 按公式：1泛流量 + 2精准垂类 + 1品牌词
5. **封面文案建议** — 按封面文案公式（问题型/数字型/对比型/否定型）
6. **CTA** — 明确的行动号召

### 宗门术语植入规则：
- 根据内容支柱动态调整植入强度
- 每条文案 3-5 个宗门术语（不可超过）
- 首次出现的术语用括号注释日常含义，方便新粉理解
- 绝对不能：用宗门身份排斥非粉丝、过度中二化、商业施压

### 品牌声音自检（每条文案必过）：
- [ ] 读出来像「一个人在说话」？
- [ ] 去掉品牌名，粉丝能认出是我们的内容？
- [ ] 有具体可执行的建议？
- [ ] 语气和内容类型匹配？
- [ ] 无禁用词？
- [ ] 宗门术语使用合规？

### 禁止事项：
- 医疗声明（治疗/治愈/药物替代）
- 绝对化用语（100%/必须/一定）
- 竞品提及
- 夸大效果（三天减十斤）
- 导流到站外（微信号等）
"""

    def generate(
        self,
        topic: str,
        platform: str = "douyin",
        pillar: str = "training",
        brief: str = "",
        tone: str = "",
        save: bool = True,
    ) -> str:
        """生成指定平台的文案。

        Args:
            topic: 选题标题/描述
            platform: 目标平台 (douyin/xiaohongshu/weibo/bilibili/wechat/all)
            pillar: 内容支柱 (training/nutrition/lifestyle/trending/brand/sect_ip)
            brief: 可选的详细 Brief
            tone: 可选的语气指定
            save: 是否保存草稿到 data/copywriting/drafts/
        """
        if platform == "all":
            return self._generate_all_platforms(topic, pillar, brief, tone, save)

        specs = self.PLATFORM_SPECS.get(platform, self.PLATFORM_SPECS["douyin"])
        intensity, intensity_desc = self.SECT_INTENSITY.get(pillar, ("低", "术语2-3个"))

        user_msg = f"""## 选题信息
- **选题**: {topic}
- **目标平台**: {platform}
- **内容支柱**: {pillar}
- **宗门植入强度**: {intensity}（{intensity_desc}）
{f"- **详细Brief**: {brief}" if brief else ""}
{f"- **语气要求**: {tone}" if tone else ""}

## 平台规格
- 标题字数: {specs['title_len']}
- 描述字数: {specs['desc_len']}
- 话题标签: {specs['hashtags']}
- 平台核心: {specs['key']}
- 内容结构: {specs['structure']}

请严格按照以上规格和品牌规范，输出完整的文案方案。"""

        system_prompt = self._build_system_prompt(
            topic=topic, platform=platform, pillar=pillar
        )
        result = self.run_with_history(
            [{"role": "user", "content": user_msg}],
            system_prompt=system_prompt,
        )

        if save:
            path = self.save_draft(result, {
                "topic": topic,
                "platform": platform,
                "pillar": pillar,
                "tone": tone or "default",
            })
            result += f"\n\n---\n📁 草稿已保存: {path}"

        return result

    def _generate_all_platforms(
        self, topic: str, pillar: str, brief: str, tone: str, save: bool
    ) -> str:
        """为所有平台生成文案。"""
        intensity, intensity_desc = self.SECT_INTENSITY.get(pillar, ("低", "术语2-3个"))

        platform_specs_text = ""
        for name, specs in self.PLATFORM_SPECS.items():
            platform_specs_text += f"""
### {name}
- 标题字数: {specs['title_len']}
- 描述字数: {specs['desc_len']}
- 话题标签: {specs['hashtags']}
- 平台核心: {specs['key']}
- 内容结构: {specs['structure']}
"""

        user_msg = f"""## 选题信息
- **选题**: {topic}
- **目标平台**: 全平台（抖音、小红书、微博、B站、微信公众号）
- **内容支柱**: {pillar}
- **宗门植入强度**: {intensity}（{intensity_desc}）
{f"- **详细Brief**: {brief}" if brief else ""}
{f"- **语气要求**: {tone}" if tone else ""}

## 各平台规格
{platform_specs_text}

请为以上 5 个平台分别输出完整文案方案。每个平台独立一个章节，包含：标题、描述/正文、开头钩子、话题标签、封面文案建议、CTA。

注意：同一选题在不同平台的表达方式应该有明显差异，不是简单改字数，而是根据平台用户习惯重新构思。"""

        system_prompt = self._build_system_prompt(
            topic=topic, platform="all", pillar=pillar
        )
        result = self.run_with_history(
            [{"role": "user", "content": user_msg}],
            system_prompt=system_prompt,
        )

        if save:
            path = self.save_draft(result, {
                "topic": topic,
                "platform": "all",
                "pillar": pillar,
                "tone": tone or "default",
            })
            result += f"\n\n---\n📁 草稿已保存: {path}"

        return result

    def review(self, draft: str) -> str:
        """审核已有文案，给出品牌一致性评分和修改建议。"""
        user_msg = f"""请审核以下文案草稿，从以下维度评分（满分10）并给出修改建议：

1. **信息准确性**（30%）— 健身/营养知识是否正确
2. **品牌一致性**（25%）— 是否符合邪健仙的人设和品牌声音指南
3. **平台适配性**（20%）— 是否符合目标平台的格式和用户习惯
4. **互动驱动力**（15%）— CTA 是否有效，能否引发评论/收藏/转发
5. **创意新颖度**（10%）— 钩子是否吸引人，有没有新意

同时检查：
- 是否有禁用词
- 宗门术语使用是否合规（3-5个/条，首次出现有注释）
- 是否有夸大/绝对化表述

## 待审核文案

{draft}"""

        return self.run(user_msg)

    def rewrite(self, draft: str, feedback: str) -> str:
        """根据审核反馈重写文案。"""
        user_msg = f"""请根据审核反馈修改以下文案。保持原有选题和结构，只修改指出的问题。

## 原稿
{draft}

## 审核反馈
{feedback}

请输出修改后的完整文案。"""

        return self.run(user_msg)
