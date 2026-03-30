"""Agency Agent — 代运营 Agent，多账号交付管理"""

from .base import BaseAgent


class AgencyAgent(BaseAgent):
    """代运营 Agent - 处理多账号、生成交付物、执行代运营工作流

    主要功能：
    - 生成周报和月报
    - 管理多账号数据
    - 生成 KPI 总结和预警
    - 跨账号数据对比
    """

    REQUIRED_DOCS = ["brand_voice", "content_pillars"]

    def __init__(self, model: str = None, account_id: str = None):
        super().__init__(model=model, account_id=account_id)
        from tools.operations.agency.workflow import AgencyWorkflow
        self.workflow = AgencyWorkflow(self.account_id, self.repo_root / "数据")

    def _build_system_prompt(self) -> str:
        """构建 AgencyAgent 的系统提示词"""
        account_name = self.account_id
        if self.account_id != "B1":
            account_name = f"{self.account_id}(由B1代运营)"

        return f"""你是「邪修宗」多账号运营管理 Agent。你的任务是为代运营客户生成专业的周报、月报和 KPI 总结。

## 当前管理账号
**{account_name}**

## 你的核心职责
1. **周报生成**：基于本周文案发布和互动数据，生成代运营周报
   - 核心指标汇总（粉丝、互动率、完播率）
   - TOP 3 高互动文案分析
   - 可执行的优化建议

2. **月报分析**：汇总月度表现，分析趋势和对标数据
   - 月度趋势分析（对比上月、环比、同比）
   - KPI 达成情况（颜色标记：绿/黄/红）
   - 内容支柱效果对比
   - 策略调整建议

3. **KPI 追踪**：检查目标达成情况，生成预警
   - 关键指标偏差分析
   - 风险预警机制
   - 改进方向建议

4. **多账号协调**：管理主账号与子账号间的数据共享和权限控制

## 代运营标准

### 周报标准格式
1. **核心指标** - 粉丝增长、互动率、完播率等关键数据
2. **发布统计** - 数量统计、支柱分布、平台分布
3. **TOP 3 高互动文案** - 分析为什么这些文案表现好（钩子、CTA、选题）
4. **优化建议** - 基于数据的 3-5 条可执行建议，按优先级排序

### 月报标准格式
1. **趋势分析** - 周环比、月同比、增长加速度
2. **KPI 对标** - 目标 vs 实际，红黄绿预警标记
3. **内容支柱分析** - 各支柱 ROI 排名、最高效支柱
4. **关键洞察** - 高互动模式识别、用户反馈整理
5. **策略建议** - 下月重点调整方向

## 可用工具
- AgencyWorkflow: generate_weekly_report() / generate_monthly_report()
- 数据存储路径：账号专属目录 /数据/accounts/{account_id}/

{self._docs_block("brand_voice", "品牌声音指南")}

{self._docs_block("content_pillars", "内容支柱体系")}

## 重点强调
- 所有数据必须有来源（周报、后台数据等）
- 建议必须具体、可执行、有明确的预期效果
- 周报/月报生成后保存到账号专属目录
- 尊重子账号的权限限制（B2、B3 的权限控制）
"""

    def generate_weekly_report(self, metrics_data: str) -> str:
        """生成周报

        Args:
            metrics_data: 本周数据汇总（JSON 或文本格式）

        Returns:
            生成的周报内容
        """
        user_msg = f"""请根据以下本周数据生成代运营周报：

## 周数据
{metrics_data}

请按标准格式生成周报，重点突出可执行的优化建议。输出格式：
1. 核心指标（表格）
2. 发布统计
3. TOP 3 高互动文案分析
4. 优化建议（按优先级）
"""
        return self.run(user_msg)

    def generate_monthly_report(self, weekly_data: str, kpi_data: str) -> str:
        """生成月报

        Args:
            weekly_data: 4 周周报汇总
            kpi_data: KPI 目标和实际数据

        Returns:
            生成的月报内容
        """
        user_msg = f"""请根据以下数据生成代运营月报：

## 周报汇总（4周）
{weekly_data}

## KPI 数据
{kpi_data}

请按标准格式生成月报，突出：
1. 趋势洞察（数据变化方向）
2. KPI 达成情况（红黄绿标记）
3. 内容支柱效果对比
4. 下月策略建议
"""
        return self.run(user_msg)

    def generate_kpi_summary(self, kpi_tracking: str) -> str:
        """生成 KPI 总结和预警

        Args:
            kpi_tracking: KPI 追踪数据

        Returns:
            KPI 总结和预警信息
        """
        user_msg = f"""请根据以下 KPI 追踪数据生成总结和预警：

{kpi_tracking}

输出格式：
1. 达成情况总结（红/黄/绿标记）
2. 重点偏差项及原因分析
3. 风险预警（需要立即改善的指标）
4. 下阶段调整建议
"""
        return self.run(user_msg)

    def cross_account_insights(self, accounts_data: str) -> str:
        """跨账号数据对比和洞察

        对比多个账号（B1、B2、B3）的表现，识别最佳实践和差距

        Args:
            accounts_data: 多账号数据对比

        Returns:
            跨账号洞察分析
        """
        user_msg = f"""请分析以下多个账号的数据，给出跨账号洞察：

## 多账号数据对比
{accounts_data}

输出格式：
1. 各账号表现对比（强项/弱项）
2. 最佳实践识别（哪个账号的内容策略最优）
3. 账号间互补机制建议（如何利用多账号优势）
4. 统一管理建议
"""
        return self.run(user_msg)

    def diagnose_account_health(self, account_metrics: str) -> str:
        """诊断账号健康度

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
4. 3 个月改进目标和路径
"""
        return self.run(user_msg)
