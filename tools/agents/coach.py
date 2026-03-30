"""Coach Agent — 会员私教 Agent，专业力量训练计划生成。

用法：
    from tools.agents.coach import CoachAgent
    agent = CoachAgent()
    result = agent.generate_full_plan(user_profile)
    result = agent.generate_training(user_profile)
"""

from pathlib import Path

from .base import BaseAgent


class CoachAgent(BaseAgent):
    """会员私教 Agent：基于用户档案生成体态热身、训练计划、饮食方案。

    这不是一个普通健身教练。这是一个严格遵守力量训练科学的专业 Agent：
    - RPE/RIR 强度管理
    - 周期化训练方案
    - 渐进超负荷路径
    - 节奏控制（Tempo）
    - 基于体态评估的个性化热身
    - TDEE 精确计算的营养方案
    """

    REQUIRED_DOCS = ["brand_voice", "super_ip", "coach_standards"]

    def _build_system_prompt(self) -> str:
        return f"""你是「邪修宗」的私教 Agent —— 掌门邪健仙麾下的首席训练师。
你为线上 1 对 1 会员（亲传弟子）定制专业训练方案。

## 你的核心身份
- 你是一个**严肃的力量训练教练**，不是普通健身房巡场教练
- 你的计划必须体现专业性：RPE/RIR、周期化、渐进超负荷、节奏控制
- 你根据用户的训练水平和目标，选择最合适的训练方案，不是千篇一律
- 你的建议必须基于运动科学，不允许经验主义和网红健身套路
- 但你的语气保持邪修宗风格：专业中带着热血，严格中带着关怀

## 宗门文化（亲传弟子级服务）
- 称呼用户为「弟子」或直接用昵称
- 计划中可适度使用宗门术语（修炼=训练、功法=计划、渡劫=突破瓶颈等）
- 但**专业术语不能被宗门术语替代**，RPE 就是 RPE，不要用修炼用语混淆

## 品牌规范

{self._docs_block("brand_voice", "品牌声音指南")}

{self._docs_block("super_ip", "宗门IP手册")}

## 训练标准（核心知识库，必须严格遵守）

{self._docs_block("coach_standards", "力量训练标准")}

## 计划生成原则

### 体态热身计划
- 根据用户填写的体态问题，从训练标准中的体态纠正动作库匹配
- 流程：软组织放松 → 针对性拉伸 → 激活训练 → 动态热身
- 总时长控制在 10-15 分钟
- 标注伤病禁忌动作
- 给出何时可以减少纠正训练的判断标准

### 训练计划
- **根据训练年限选择周期化方案**（不是随意安排）
- **根据训练目标决定强度区间和容量**
- 每个动作必须标注：组数、次数范围、RPE/RIR、组休、节奏(Tempo)
- 动作排列：Tier 1 → Tier 2 → Tier 3
- 明确渐进超负荷规则（何时加重、加多少、失败怎么办）
- 明确 Deload 安排
- 明确阶段转换标准（何时进入下一阶段）
- 如有伤病，必须使用替代动作（参考训练标准中的伤病动作替换表）

### 饮食方案
- 用 Mifflin-St Jeor 公式计算 BMR
- 用活动系数计算 TDEE
- 根据目标调整热量（增肌+10-20% / 减脂-20-25%）
- 蛋白质按体重计算（1.6-2.2g/kg，减脂期上调至 2.0-2.4g/kg）
- 脂肪不低于 20% 总热量
- 碳水填充剩余
- 区分训练日/非训练日
- 考虑用户饮食偏好和过敏/忌口
- 给出食材替换表（灵活性）

### 输出格式
- 使用 Markdown 格式
- 大量使用表格（清晰、可执行）
- 每个部分结构化，用户可以直接照着练/吃
- 关键数字用粗体标注

### 绝对禁止
- 给出医疗诊断或治疗建议（伤病只能建议就医）
- 推荐任何处方药物或违禁补剂
- 给出超出用户当前能力的负重建议
- 使用"必须"、"100%"等绝对化表述
- 忽略用户填写的伤病信息
"""

    def _extract_username(self, profile: str) -> str:
        """从用户档案中提取昵称。"""
        for line in profile.split("\n"):
            if "姓名" in line or "昵称" in line:
                parts = line.split(":", 1)
                if len(parts) > 1 and parts[1].strip():
                    return parts[1].strip()
        return "会员"

    def generate_full_plan(self, user_profile: str, save: bool = True) -> str:
        """一次性生成三大计划（体态热身 + 训练 + 饮食）。"""
        username = self._extract_username(user_profile)

        user_msg = f"""请根据以下会员档案，生成完整的三合一计划。

## 会员档案
{user_profile}

---

请依次输出以下三个部分，每个部分用一级标题分隔：

# 一、{username} 训练前动作准备方案
（体态评估摘要 → 软组织放松 → 针对性拉伸 → 激活训练 → 动态热身 → 注意事项）

# 二、{username} 训练计划
（计划概览 → 训练分化安排 → 每日详细训练表 → 渐进超负荷规则 → Deload 协议 → 阶段转换标准）

# 三、{username} 饮食方案
（TDEE 计算 → 宏量素分配 → 训练日/非训练日餐食模板 → 食材替换表 → 补剂建议 → 注意事项）

每个部分都必须完整、可直接执行。"""

        result = self.run(user_msg)

        if save:
            # 尝试拆分三部分分别保存
            parts = self._split_plan(result)
            for plan_type, content in parts.items():
                path = self.save_member_plan(username, plan_type, content)
            # 同时保存完整版
            full_path = self.save_member_plan(username, "完整计划", result)
            result += f"\n\n---\n📁 计划已保存至: {full_path.parent}"

        return result

    def generate_warmup(self, user_profile: str, save: bool = True) -> str:
        """单独生成体态热身计划。"""
        username = self._extract_username(user_profile)

        user_msg = f"""请根据以下会员档案，只生成**训练前动作准备方案**。

## 会员档案
{user_profile}

---

输出结构：
# {username} 训练前动作准备方案

## 体态评估摘要
## A. 软组织放松（泡沫轴/筋膜球）2-3分钟
## B. 针对性拉伸 3-5分钟
## C. 激活训练 3-5分钟
## D. 动态热身 2-3分钟
## 注意事项

所有动作用表格列出（动作、组数×次数/时间、要点）。"""

        result = self.run(user_msg)
        if save:
            path = self.save_member_plan(username, "warmup", result)
            result += f"\n\n---\n📁 已保存: {path}"
        return result

    def generate_training(self, user_profile: str, save: bool = True) -> str:
        """单独生成训练计划。"""
        username = self._extract_username(user_profile)

        user_msg = f"""请根据以下会员档案，只生成**训练计划**。

## 会员档案
{user_profile}

---

输出结构：
# {username} 训练计划

## 计划概览
（目标、阶段、周期类型、频率、时长、渐进策略）

## 训练分化安排
（每日训练内容/肌群/时长 表格）

## 详细训练日
（每个训练日独立一节，每个动作标注：序号、动作名、组数、次数、RPE/RIR、组休、节奏Tempo、备注）

## 渐进超负荷规则
## Deload 协议
## 阶段转换标准

必须使用表格，每个动作完整标注所有参数。"""

        result = self.run(user_msg)
        if save:
            path = self.save_member_plan(username, "training", result)
            result += f"\n\n---\n📁 已保存: {path}"
        return result

    def generate_diet(self, user_profile: str, save: bool = True) -> str:
        """单独生成饮食方案。"""
        username = self._extract_username(user_profile)

        user_msg = f"""请根据以下会员档案，只生成**饮食方案**。

## 会员档案
{user_profile}

---

输出结构：
# {username} 饮食方案

## 营养目标
（BMR 计算过程 → TDEE → 目标热量 → 宏量素精确分配）

## 每日餐食模板
### 训练日
（表格：餐次、时间、食物组合、蛋白质g、碳水g、脂肪g、热量kcal）
### 非训练日
（同上格式）

## 食材替换表
（分类：优质蛋白/碳水来源/健康脂肪/蔬菜，每类3-4个选项+每份规格）

## 补剂建议
## 饮食注意事项

所有数字精确到克，热量精确到 kcal。"""

        result = self.run(user_msg)
        if save:
            path = self.save_member_plan(username, "diet", result)
            result += f"\n\n---\n📁 已保存: {path}"
        return result

    def adjust_plan(self, current_plan: str, feedback: str, save: bool = True) -> str:
        """根据用户反馈调整已有计划。"""
        user_msg = f"""请根据用户反馈调整以下训练计划。只修改需要调整的部分，保持其余不变。

## 当前计划
{current_plan}

## 用户反馈
{feedback}

---

请输出调整后的完整计划，并在修改处标注 **【已调整】** 方便用户对比。
同时说明调整原因。"""

        return self.run(user_msg)

    def progress_check(
        self, user_profile: str, current_plan: str, progress_data: str
    ) -> str:
        """阶段性评估，决定是否进入下一阶段。"""
        user_msg = f"""请进行阶段性训练评估。

## 用户档案
{user_profile}

## 当前执行的计划
{current_plan}

## 训练进展数据
{progress_data}

---

请评估：
1. 当前计划执行情况（力量进步、体重/体脂变化、体态改善）
2. 是否达到阶段转换标准
3. 如果达到：给出下一阶段计划建议
4. 如果未达到：分析原因（训练/饮食/恢复），给出调整建议
5. 宗门鼓励语（根据进步程度给予不同等级的认可）"""

        return self.run(user_msg)

    def _split_plan(self, full_plan: str) -> dict[str, str]:
        """尝试将完整计划拆分为三个文件。"""
        parts = {}
        current_key = None
        current_lines = []

        key_map = {
            "动作准备": "warmup",
            "热身": "warmup",
            "训练计划": "training",
            "训练方案": "training",
            "饮食方案": "diet",
            "饮食计划": "diet",
            "营养方案": "diet",
        }

        for line in full_plan.split("\n"):
            if line.startswith("# "):
                # 保存上一段
                if current_key and current_lines:
                    parts[current_key] = "\n".join(current_lines)
                # 判断新段落属于哪个 key
                current_key = None
                for keyword, key in key_map.items():
                    if keyword in line:
                        current_key = key
                        break
                current_lines = [line]
            else:
                current_lines.append(line)

        # 保存最后一段
        if current_key and current_lines:
            parts[current_key] = "\n".join(current_lines)

        return parts
