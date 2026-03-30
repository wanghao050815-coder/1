# 文案部门 FAQ

## 工具使用

### Q: 如何创建新文案？
```bash
# CLI 方式
python tools/copywriting/copy_cli.py create --type script --platform douyin --pillar training

# Agent 方式（需要 ANTHROPIC_API_KEY）
python -m tools.agents copywrite --topic "跑步膝盖疼" --platform douyin --pillar training
```

### Q: 如何审核文案？
```bash
# 查看详情并进入审核
python tools/copywriting/copy_cli.py review --id CP-20260401-001

# AI 审核（需要 API）
python -m tools.agents review --input 数据/文案/草稿/CP-20260401-001.md
```

### Q: 文案保存在哪里？
- 草稿：`数据/文案/草稿/`
- 已发布：`数据/文案/已发布/`
- 归档：`数据/文案/归档/`
- 金句库：`数据/文案/金句库/`（高互动文案自动入库）
- 素材库：`数据/文案/素材库/`（历史文案数据库）

### Q: 支持哪些平台？
抖音、小红书、微博、B站、微信公众号。每个平台有独立的文案模板和规格要求。

### Q: 支持哪些文案类型？
视频脚本、标题+描述、封面文案、小红书笔记、微博博文、微信推文、B站长视频脚本、商务合作文案。

---

## 文案创作

### Q: 宗门术语怎么用？
- 每条文案 3-5 个术语，不可超过
- 只用**真实验证**的术语：秘法、宗主、邪修、正派、先修、宗门弟子
- **绝对不用**虚构术语（心法、绝学、道法等在真实文案中从未出现）
- 首次出现的术语用括号注释日常含义

### Q: 高赞文案有什么规律？
参考 `数据/文案/风格DNA.md`，核心规律：
1. 6层标准结构：标题→开篇→问题→转折→方案→CTA
2. 反问+梗式钩子效果最好（141K-232K赞）
3. 效果承诺型CTA优于乞求式CTA
4. 口语化 > 书面语

### Q: 哪些内容绝对不能写？
- 医疗声明（治疗/治愈/药物替代）
- 绝对化用语（100%/必须/一定）
- 竞品提及
- 夸大效果（三天减十斤）
- 导流到站外

---

## 运营相关

### Q: 如何诊断账号阶段？
```bash
python -m tools.agents diagnose --followers 25000 --growth-rate 0.08 --engagement-rate 0.05
```

### Q: 如何制定月度计划？
```bash
python -m tools.agents ops-plan --year 2026 --month 4 --stage growth
```

### Q: 如何录入发布数据（复盘用）？
数据由用户手动提供，通过 `tools/operations/feedback/performance_tracker.py` 的 `record_performance()` 函数录入。
