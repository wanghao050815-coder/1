"""Planner Agent — 策划 Agent，选题评估与 Brief 生成。

用法：
    from tools.agents.planner import PlannerAgent
    agent = PlannerAgent()
    result = agent.plan_week(count=14, theme="春季户外训练")
    result = agent.generate_brief(topic="跑步膝盖疼", platform="douyin", pillar="training")
"""

from .base import BaseAgent


class PlannerAgent(BaseAgent):
    """内容策划 Agent：选题规划、Brief 生成、配比审计。"""

    REQUIRED_DOCS = [
        "brand_voice",
        "content_pillars",
        "super_ip",
        "douyin_playbook",
    ]

    def _build_system_prompt(self) -> str:
        calendar = self._load_calendar_week()
        calendar_block = f"\n<current_calendar>\n{calendar}\n</current_calendar>" if calendar else ""
        platforms_config = self._load_config("platforms")
        kpis_config = self._load_config("kpis")

        return f"""你是「邪修宗」内容团队的策划 Agent。你的任务是规划选题、生成 Brief、管理内容配比。

## 你的核心职责
1. 根据内容支柱体系和当前热点，规划每周 14 条选题
2. 为每条选题生成结构化 Brief（核心信息点、目标受众、CTA、参考素材）
3. 监控内容配比是否偏离目标（训练35%/营养25%/生活20%/热点10%/品牌≤10%）
4. 合理分配各平台发布量（抖音5/小红书4/B站2/微博7/微信3 每周）

## 品牌规范

{self._docs_block("content_pillars", "内容支柱体系")}

{self._docs_block("brand_voice", "品牌声音指南")}

{self._docs_block("super_ip", "宗门IP手册")}

{self._docs_block("douyin_playbook", "抖音运营手册")}

<platforms_config>
{platforms_config}
</platforms_config>

<kpis>
{kpis_config}
</kpis>
{calendar_block}

## 选题规划原则
- 每日 2 条，共 14 条/周
- 配比必须在目标 ±10% 以内
- 同一支柱不连续发布超过 2 条
- 周末偏向生活方式和可保存的深度内容
- 节假日/热点必须提前 3 天准备
- 每周至少 1 条宗门 IP 强相关内容
- 避免近 30 天内重复选题

## Brief 结构（每条选题必须包含）
1. 选题标题（工作名）
2. 内容支柱归属
3. 目标平台 + 内容形式（短视频/长视频/图文）
4. 建议时长/字数
5. 核心信息点（最多3个）
6. 目标受众画像
7. 期望 CTA（关注/评论/收藏/转发）
8. 钩子方向建议
9. 宗门元素植入建议
10. 参考内容/灵感来源
11. 发布时间建议
"""

    def plan_week(
        self,
        count: int = 14,
        theme: str = "",
        week_start: str = "",
        constraints: str = "",
    ) -> str:
        """规划一周的选题。"""
        user_msg = f"""请规划下一周的 {count} 条选题计划。

{f"**周一日期**: {week_start}" if week_start else ""}
{f"**本周主题线索**: {theme}" if theme else "请根据当前季节和近期热点自行确定主题线索。"}
{f"**额外约束**: {constraints}" if constraints else ""}

要求：
1. 输出完整的周计划表格（日期、选题标题、支柱、平台、形式、时长、发布时间）
2. 每条选题附简要说明（1-2句）
3. 底部附配比总览和平台分布统计
4. 标注本周重点提示（节日/热点/运营动作）

今天是 {self.today()}。"""

        return self.run(user_msg)

    def generate_brief(
        self,
        topic: str,
        platform: str = "douyin",
        pillar: str = "training",
        context: str = "",
    ) -> str:
        """为单条选题生成详细 Brief。"""
        user_msg = f"""请为以下选题生成详细 Brief：

- **选题**: {topic}
- **目标平台**: {platform}
- **内容支柱**: {pillar}
{f"- **补充背景**: {context}" if context else ""}

请按 Brief 结构输出完整的 10 项内容。"""

        return self.run(user_msg)

    def audit_pillar_ratio(self, published_content: str) -> str:
        """审计当月内容配比。"""
        user_msg = f"""请审计以下已发布内容的支柱配比，对比目标值给出偏差分析和调整建议：

目标配比：训练35% / 营养25% / 生活方式20% / 热点10% / 品牌合作≤10%

## 已发布内容
{published_content}

请输出：
1. 当前各支柱实际占比
2. 与目标的偏差
3. 下周调整建议"""

        return self.run(user_msg)
