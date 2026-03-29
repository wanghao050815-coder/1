# 历史文案素材库

将你过往表现好的文案/脚本放在这个目录下，Copywriter Agent 会自动读取作为风格参考。

## 支持的文件格式

- `.md` / `.txt` — 纯文本文案
- `.json` — 结构化文案（见下方格式）

## 推荐的 JSON 格式

```json
{
  "title": "视频标题",
  "platform": "douyin",
  "pillar": "training",
  "hook": "开头3秒钩子文案",
  "script": "完整脚本正文...",
  "description": "视频描述文案",
  "hashtags": ["#健身", "#减脂"],
  "engagement": "点赞1.2w 评论800 收藏3000",
  "notes": "为什么这条效果好的简要分析"
}
```

## 也可以直接丢纯文本

不需要严格格式，直接把你觉得写得好的文案贴进 `.md` 文件即可。
Agent 会自动从中学习你的语气、句式、用词习惯。

## 文件命名建议

```
[平台]_[主题关键词].[格式]
```

例如：
- `douyin_跑步膝盖疼.md`
- `xiaohongshu_早餐误区.txt`
- `douyin_圆肩矫正.json`
