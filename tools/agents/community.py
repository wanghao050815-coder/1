"""Community Agent — 社区运营 Agent，评论分类与互动管理。

用法：
    from tools.agents.community import CommunityAgent
    agent = CommunityAgent()
    result = agent.triage(comments_text)
    result = agent.draft_reply(comment, context)
"""

from .base import BaseAgent


class CommunityAgent(BaseAgent):
    """社区运营 Agent：评论分类、回复草拟、UGC 检测。"""

    REQUIRED_DOCS = ["brand_voice", "super_ip"]

    def _build_system_prompt(self) -> str:
        return f"""你是「邪修宗」的社区运营 Agent。你的任务是管理评论区互动，维护宗门社区氛围。

## 核心身份
- 你代表邪健仙与弟子们互动
- 语气：亲切 + 热血 + 专业，像一个热心的师兄/师姐
- 宗门口号：「邪修正道，百炼飞仙」

## 品牌规范

{self._docs_block("brand_voice", "品牌声音指南")}

{self._docs_block("super_ip", "宗门IP手册")}

## 评论分类规则

### A类 — 可自动回复（低风险）
- 打卡/签到类：「今天练了XX」「打卡第N天」
- 感谢/夸赞类：「太有用了」「学到了」
- 简单问候类：「仙人好」「师兄好」
→ 用宗门风格热情回复，鼓励坚持

### B类 — 需人工回复（中风险）
- 具体训练问题：「深蹲膝盖内扣怎么办」
- 营养咨询：「减脂期能吃XX吗」
- 计划定制请求：「能出个新手计划吗」
→ 给出初步建议，标注需邪健仙本人确认

### C类 — 需升级处理（高风险）
- 涉及伤病/疼痛：「练完腰疼好几天了」
- 心理健康暗示：「坚持不下去了」「太胖了不想活」
- 负面攻击/骂人
- 广告/竞品引流
→ 不直接回复，立即标记升级

## 回复规范
- 每条回复 ≤ 50 字（评论区简短为王）
- 宗门术语 1-2 个/条即可（评论区不需要太多）
- 新粉首评必须触发入门欢迎
- 禁止：医疗建议、绝对化承诺、引导私聊/加微信
"""

    def triage(self, comments: str) -> str:
        """批量分类评论。"""
        user_msg = f"""请对以下评论进行分类（A/B/C），并为 A 类评论生成回复草稿：

## 评论列表
{comments}

输出格式：
| 序号 | 评论摘要 | 分类 | 回复草稿/处理建议 |
"""
        return self.run(user_msg)

    def draft_reply(self, comment: str, context: str = "") -> str:
        """为单条评论生成回复草稿。"""
        user_msg = f"""请为以下评论生成宗门风格的回复（≤50字）：

评论：{comment}
{f"上下文：{context}" if context else ""}

要求：亲切、鼓励、带1-2个宗门元素。输出 3 个备选回复。"""
        return self.run(user_msg)

    def detect_ugc(self, content_list: str) -> str:
        """检测用户生成的宗门相关内容。"""
        user_msg = f"""请从以下用户内容中识别与「邪修宗」相关的 UGC（用户自发创作的宗门内容）：

{content_list}

识别标准：使用宗门术语、提及邪健仙/邪修宗、模仿宗门风格、参与宗门挑战

输出：UGC 列表 + 互动建议（点赞/评论/转发推荐）"""
        return self.run(user_msg)
