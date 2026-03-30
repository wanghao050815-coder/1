"""Analytics Agent — 数据分析 Agent，KPI 追踪与趋势洞察。

用法：
    from tools.agents.analytics import AnalyticsAgent
    agent = AnalyticsAgent()
    result = agent.weekly_report(data_text)
    result = agent.kpi_check(data_text)
"""

from .base import BaseAgent
from pathlib import Path


class AnalyticsAgent(BaseAgent):
    """增强的数据分析 Agent：周报生成、KPI 检测、趋势洞察、智能分析。"""

    REQUIRED_DOCS = ["content_pillars"]

    def __init__(self, model: str = None, account_id: str = None):
        super().__init__(model=model, account_id=account_id)
        # 集成分析工具
        from tools.analytics.metrics_engine import MetricsCalculator
        from tools.analytics.insights_engine import InsightsEngine
        from tools.analytics.report_generator import ReportGenerator

        self.metrics_calc = MetricsCalculator(self.repo_root / "数据", self.account_id)
        self.insights_gen = InsightsEngine(self.repo_root / "数据", self.account_id)
        self.report_gen = ReportGenerator(self.repo_root / "数据", self.account_id)

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

    def comprehensive_analysis(self, metrics_data: str, copies_performance: str) -> str:
        """综合分析：指标 + 内容表现

        综合多维度数据进行深度分析，包括：
        - 指标诊断（对标KPI）
        - 内容诊断（高低表现分析）
        - 模式识别（高互动文案的共同特征）
        - 趋势预测（未来7日预测）

        Args:
            metrics_data: 账号指标数据
            copies_performance: 内容表现数据

        Returns:
            综合分析报告
        """
        user_msg = f"""请进行综合数据分析：

## 账号指标
{metrics_data}

## 内容表现
{copies_performance}

请输出：
1. 指标诊断（对标KPI，指出偏差和风险）
2. 内容诊断（TOP 3和BOTTOM 3文案分析）
3. 高互动模式识别（钩子、CTA、选题的共同特征）
4. 趋势预测（未来7天粉丝和互动的预测）
5. 可执行建议（按优先级排序，3-5条）"""
        return self.run(user_msg)

    def health_diagnosis(self, account_metrics: str) -> str:
        """账号健康度诊断

        综合评估账号的各项指标，给出健康度评分和改进建议

        Args:
            account_metrics: 账号指标数据

        Returns:
            健康度诊断报告
        """
        user_msg = f"""请诊断该账号的健康度，给出综合评分和改进建议：

## 账号指标
{account_metrics}

请评估：
1. 整体健康度评分（0-100）
2. 关键指标评价（强项/弱项）
3. 与行业标准的对标
4. 3个月改进目标和路径
5. 需要立即改善的3个关键指标"""
        return self.run(user_msg)

    def forecasting_analysis(self, historical_data: str) -> str:
        """趋势预测和未来展望

        基于历史数据预测未来表现

        Args:
            historical_data: 过去30天的历史数据

        Returns:
            预测报告
        """
        user_msg = f"""请基于历史数据预测未来表现：

## 历史数据
{historical_data}

请输出：
1. 粉丝增长预测（未来7-30天）
2. 互动率趋势预测
3. 高风险信号预警
4. 机会窗口识别"""
        return self.run(user_msg)
