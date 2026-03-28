"""Analytics Agent — 数据分析 Agent，KPI 追踪与趋势洞察。

用法：
    from tools.agents.analytics import AnalyticsAgent
    agent = AnalyticsAgent()
    result = agent.weekly_report(data_text)
    result = agent.kpi_check(data_text)
"""

from .base import BaseAgent


class AnalyticsAgent(BaseAgent):
    """数据分析 Agent：周报生成、KPI 检测、趋势洞察。"""

    REQUIRED_DOCS = ["content_pillars"]

    def _build_system_prompt(self) -> str:
        kpis = self._load_config("kpis")
        platforms = self._load_config("platforms")

        return f"""你是「邪修宗」内容团队的数据分析 Agent。你的任务是追踪 KPI、生成报告、发现趋势。

## KPI 目标体系
<kpis>
{kpis}
</kpis>

<platforms>
{platforms}
</platforms>

{self._docs_block("content_pillars", "内容支柱体系")}

## 分析原则
- 数据说话，不主观臆断
- 偏差超过 ±20% 必须标红告警
- 每个洞察必须附带可执行建议
- 对比维度：周环比、月同比、平台间横比
- 不只看绝对值，关注趋势方向

## 报告结构
1. 数据概览（各平台核心指标 vs 目标）
2. Top 3 表现最佳内容（成功原因分析）
3. Bottom 3 表现最差内容（失败原因分析）
4. KPI 告警项（偏差 ≥ ±20%）
5. 内容配比审计
6. 关键洞察（3-5条）
7. 下周优化建议

## 宗门 IP 专项指标
- 私域社群月增长率目标: 10%
- 月度 UGC 数量目标: 50 条
- 宗门术语使用率目标: 20%
- 老粉回看率目标: 30%
- 社区 NPS 目标: 60
"""

    def weekly_report(self, raw_data: str) -> str:
        """根据原始数据生成周报。"""
        user_msg = f"""请根据以下原始数据生成本周数据周报：

## 原始数据
{raw_data}

请按报告结构输出完整周报，所有指标与 KPI 目标对比。"""
        return self.run(user_msg)

    def kpi_check(self, raw_data: str) -> str:
        """快速 KPI 健康检查。"""
        user_msg = f"""请快速检查以下数据中是否有 KPI 偏差超过 ±20% 的告警项：

{raw_data}

只输出告警项（如有），每项包含：指标名 → 目标值 → 实际值 → 偏差% → 建议动作。
如果全部正常，输出「✅ 所有 KPI 在正常范围内」。"""
        return self.run(user_msg)

    def content_insights(self, performance_data: str) -> str:
        """从内容表现数据中提取选题洞察。"""
        user_msg = f"""请分析以下内容表现数据，提取可指导下周选题的洞察：

{performance_data}

输出：
1. 哪些话题/支柱表现最好，为什么
2. 哪些平台/时段效率最高
3. 受众偏好信号（评论关键词、收藏模式）
4. 具体的下周选题建议（3-5个方向）"""
        return self.run(user_msg)
