"""Publisher Agent — 发布 Agent，Checklist 生成与规格校验。

用法：
    from tools.agents.publisher import PublisherAgent
    agent = PublisherAgent()
    result = agent.checklist(platform="douyin", copy_text=approved_copy)
"""

from .base import BaseAgent


class PublisherAgent(BaseAgent):
    """发布 Agent：发布 Checklist、规格校验、最佳时间建议。"""

    REQUIRED_DOCS = ["douyin_playbook"]

    def _build_system_prompt(self) -> str:
        platforms = self._load_config("platforms")

        return f"""你是「邪修宗」内容团队的发布 Agent。你的任务是在内容发布前进行最终质检。

<platforms>
{platforms}
</platforms>

{self._docs_block("douyin_playbook", "抖音运营手册")}

## 发布 Checklist 项目

### 内容合规
- [ ] 无医疗/绝对化声明
- [ ] 无竞品水印或提及
- [ ] 无未授权音乐/素材
- [ ] 无导流到站外的话术
- [ ] 无联系方式（手机号/微信号）

### 平台规格
- [ ] 视频分辨率符合平台要求
- [ ] 视频时长在推荐范围内
- [ ] 标题字数符合限制
- [ ] 描述/正文字数符合限制
- [ ] 话题标签数量合规
- [ ] 封面尺寸正确，安全区内无关键信息被裁切

### 品牌一致性
- [ ] 品牌水印已添加
- [ ] 字幕使用指定字体和样式
- [ ] 品牌色系正确
- [ ] 宗门元素植入合规

### 发布设置
- [ ] 发布时间在最佳时段内
- [ ] 话题标签已添加
- [ ] @相关账号（如有合作）
- [ ] 评论区维护团队已通知

## 注意
当前所有平台 API 未接入，你只负责生成 Checklist 和建议，不执行实际发布。
"""

    def checklist(self, platform: str, copy_text: str, video_info: str = "") -> str:
        """生成发布前 Checklist。"""
        video_section = f"## 视频信息\n{video_info}" if video_info else ""
        user_msg = f"""请为以下内容生成发布前 Checklist：

**目标平台**: {platform}

## 文案内容
{copy_text}

{video_section}

请逐项检查 Checklist，标注 ✅ 通过 / ❌ 未通过 / ⚠️ 需确认。
未通过项请说明原因和修改建议。
最后给出最佳发布时间建议（具体到小时）。"""
        return self.run(user_msg)

    def suggest_time(self, platform: str, pillar: str, day_of_week: str = "") -> str:
        """建议最佳发布时间。"""
        user_msg = f"""请推荐发布时间：

- 平台: {platform}
- 内容支柱: {pillar}
{f"- 星期: {day_of_week}" if day_of_week else ""}

输出 Top 3 推荐时段，附理由。"""
        return self.run(user_msg)
