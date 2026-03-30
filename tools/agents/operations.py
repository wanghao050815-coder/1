"""Operations Agent — 运营 Agent，策略规划 + 采播执行的 AI 驱动。

用法：
    from tools.agents.operations import OperationsAgent
    agent = OperationsAgent()
    result = agent.diagnose_stage(followers=25000, growth_rate=0.08)
    result = agent.plan_month(year=2026, month=4)
    result = agent.optimize_schedule(week_start="2026-04-06", posts=[...])
"""

import json
from .base import BaseAgent


class OperationsAgent(BaseAgent):
    """运营策略 Agent — 账号诊断、KPI规划、内容排期的 AI 驱动。

    注入文档：brand_voice（调性参考）、content_pillars（支柱体系）、
    copywriting_sop（产出规范）。
    独立分区设计：仅加载运营所需文档，不加载文案库等大型资源。
    """

    REQUIRED_DOCS = [
        "brand_voice",
        "content_pillars",
    ]

    def _build_system_prompt(self) -> str:
        kpi_config = self._load_config("kpis")
        kpi_block = f"\n<kpi_config>\n{kpi_config}\n</kpi_config>" if kpi_config else ""

        platform_config = self._load_config("platforms")
        platform_block = f"\n<platform_config>\n{platform_config}\n</platform_config>" if platform_config else ""

        calendar = self._load_calendar_week()
        calendar_block = f"\n<content_calendar>\n{calendar}\n</content_calendar>" if calendar else ""

        return f"""你是「邪修宗」内容团队的运营策略 Agent。你的任务是为健身博主「邪健仙」提供账号运营策略和执行规划。

## 你的核心职责
1. **账号诊断**：分析当前账号数据，判断生命周期阶段，给出运营建议
2. **KPI 规划**：制定月度/季度 KPI 目标，跟踪达成情况
3. **内容配比**：根据账号阶段和数据表现，优化内容支柱配比
4. **发布排期**：规划每周发布计划，优化发布时间
5. **趋势洞察**：基于数据分析识别增长机会和风险

## 品牌背景
{self._docs_block("brand_voice", "品牌声音指南")}
{self._docs_block("content_pillars", "内容支柱体系")}
{kpi_block}
{platform_block}
{calendar_block}

## 输出要求
- 所有建议必须具体、可执行
- 用数据支撑每个决策
- 给出优先级排序（P0/P1/P2/P3）
- 考虑资源约束（1人团队 vs 多人团队）

## 账号生命周期阶段
- **冷启动期**（0-1万粉）：高频测试，找爆款模型
- **增长期**（1-50万粉）：放大爆款，建立矩阵
- **稳定期**（50万+）：精品内容，商业变现
- **衰退期**（连续掉粉）：创新内容，寻找新增长点
"""

    def diagnose_stage(self, followers: int, growth_rate: float = 0,
                       engagement_rate: float = 0, extra_context: str = "") -> str:
        """诊断账号当前阶段并给出运营策略建议。"""
        user_msg = f"""请诊断以下账号的运营状态并给出详细策略建议：

## 账号数据
- 当前粉丝数: {followers:,}
- 月增长率: {growth_rate:.1%}
- 互动率: {engagement_rate:.1%}
{f"- 补充信息: {extra_context}" if extra_context else ""}

请输出：
1. 当前账号阶段判断及理由
2. 该阶段的核心运营策略
3. 本月最优先的3件事（P0级别）
4. 内容支柱配比建议
5. 风险提醒"""

        return self.run(user_msg)

    def plan_month(self, year: int, month: int, stage: str = "growth",
                   context: str = "") -> str:
        """制定月度运营计划。"""
        user_msg = f"""请制定 {year}年{month}月 的运营计划：

## 基本信息
- 账号阶段: {stage}
{f"- 补充背景: {context}" if context else ""}

请输出：
1. 本月KPI目标（含具体数值）
2. 内容支柱配比及周发布排期框架
3. 重要节点/热点日历（如有）
4. 本月运营重点（按优先级P0-P3）
5. 资源需求和时间分配建议"""

        return self.run(user_msg)

    def optimize_schedule(self, week_start: str, posts: list[dict],
                          platform_data: str = "") -> str:
        """优化一周的发布排期。"""
        posts_text = json.dumps(posts, ensure_ascii=False, indent=2)
        platform_block = f"## 平台数据参考\n{platform_data}" if platform_data else ""
        user_msg = f"""请优化以下一周的发布排期：

## 周起始日期
{week_start}

## 待排期内容
{posts_text}

{platform_block}

请输出：
1. 优化后的每日发布计划（含具体时间）
2. 各条内容的发布顺序建议（先发哪条、后发哪条）
3. 时间优化理由（为什么选择这个时间）
4. 内容之间的关联和互推策略
5. 备选方案（如果某条内容延期）"""

        return self.run(user_msg)

    def review_performance(self, data: str) -> str:
        """复盘上周/上月运营数据。"""
        user_msg = f"""请复盘以下运营数据，给出分析和改进建议：

## 运营数据
{data}

请输出：
1. 关键指标达成情况（对比目标）
2. 本期亮点（做得好的）
3. 本期问题（需要改进的）
4. 数据洞察（发现了什么规律/趋势）
5. 下期改进建议（具体可执行）"""

        return self.run(user_msg)
