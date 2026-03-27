# [博主名称] 健身内容团队 — 系统导航中心

## 使命宣言

我们是一支专注于健身与健康生活方式的内容创作团队，致力于通过科学、真实、有温度的内容，帮助每一位关注者建立可持续的健康习惯。我们相信，改变体型只是起点，真正的目标是让「健康」成为每个人生活方式的一部分。团队以「宗门」文化为核心，用内容连接志同道合的人，用数据驱动持续进化，用系统保障稳定输出。

---

## 系统全景：三层架构

```
┌─────────────────────────────────────────────────────────┐
│  第一层：知识层 (Knowledge Layer)                          │
│  品牌指南 · 内容支柱 · 宗门IP · 声音规范                    │
│  → 所有创作的"宪法"，回答"我们是谁、说什么、怎么说"          │
├─────────────────────────────────────────────────────────┤
│  第二层：自动化层 (Automation Layer)                       │
│  GitHub Actions · 每周数据复盘自动创建 · 发布提醒           │
│  → 把重复性工作交给机器，让人专注于创意和判断               │
├─────────────────────────────────────────────────────────┤
│  第三层：流程层 (Process Layer)                            │
│  Issue 模板 · SOP文档 · 团队规范 · 入职指南                 │
│  → 把最佳实践固化为可复用的流程，降低沟通成本               │
└─────────────────────────────────────────────────────────┘
```

---

## 我想要… 快速导航

| 我想要…                     | 去这里                                                      |
|----------------------------|-------------------------------------------------------------|
| 提交一个内容创意             | [创建 Content Request Issue](.github/ISSUE_TEMPLATE/content-request.yml) |
| 了解我们的品牌声音           | [品牌声音指南](docs/brand/brand-voice-guide.md)              |
| 查看内容支柱和选题方向       | [内容支柱文档](docs/brand/content-pillars.md)                |
| 了解宗门IP体系               | [宗门IP手册](docs/brand/super-ip.md)                        |
| 查看视觉规范                 | [视觉识别标准](docs/brand/visual-identity.md)                |
| 了解团队分工                 | [组织架构图](docs/team/org-chart.md)                        |
| 了解沟通规范                 | [团队沟通规范](docs/team/communication-norms.md)             |
| 我是新成员，从哪里开始？     | [入职指南总览](docs/team/onboarding/README.md)              |
| 我是内容编辑                 | [内容编辑入职](docs/team/onboarding/content-writer.md)      |
| 我是视频剪辑师               | [剪辑师入职](docs/team/onboarding/video-editor.md)          |
| 我是数据分析师               | [数据分析师入职](docs/team/onboarding/data-analyst.md)      |
| 我是社群运营                 | [社群运营入职](docs/team/onboarding/community-manager.md)   |
| 我是文案编辑                 | [文案部门SOP](docs/copywriting/copywriting-sop.md)          |
| 提交文案需求                 | [创建文案需求 Issue](.github/ISSUE_TEMPLATE/copywriting-request.yml) |
| 查看本周数据复盘             | [Issues → analytics 标签](../../issues?label=analytics)     |
| 配置 GitHub Projects 看板   | [项目看板配置指南](.github/PROJECT_CONFIG.md)                |
| 报告一个工具故障或流程问题   | [创建 Bug Report Issue](.github/ISSUE_TEMPLATE/bug-report.yml) |

---

## 目录结构

```
/
├── README.md                          # 本文件：导航中心
├── .github/
│   ├── workflows/
│   │   └── weekly-digest.yml         # 每周自动创建数据复盘Issue
│   ├── ISSUE_TEMPLATE/
│   │   ├── content-request.yml       # 内容创意申请
│   │   ├── copywriting-request.yml   # 文案需求申请
│   │   ├── weekly-review.yml         # 每周数据复盘
│   │   └── bug-report.yml            # 故障/流程问题报告
│   └── PROJECT_CONFIG.md             # GitHub Projects 配置指南
├── docs/
│   ├── copywriting/
│   │   └── copywriting-sop.md        # 文案部门SOP流程
│   ├── brand/
│   │   ├── brand-voice-guide.md      # 品牌声音与写作规范
│   │   ├── visual-identity.md        # 视觉识别标准
│   │   ├── content-pillars.md        # 六大内容支柱
│   │   └── super-ip.md               # 宗门超级符号手册
│   └── team/
│       ├── org-chart.md              # 组织架构与RACI矩阵
│       ├── communication-norms.md    # 团队沟通规范
│       └── onboarding/
│           ├── README.md             # 入职总览（所有新成员）
│           ├── content-writer.md     # 内容编辑入职路径
│           ├── video-editor.md       # 剪辑师入职路径
│           ├── data-analyst.md       # 数据分析师入职路径
│           └── community-manager.md  # 社群运营入职路径
```

---

## 快速开始：三步安装依赖

```bash
# 第一步：克隆仓库并进入目录
git clone https://github.com/[你的GitHub组织或用户名]/[仓库名].git && cd [仓库名]

# 第二步：安装 Python 依赖（数据分析脚本）
pip install -r requirements.txt

# 第三步：复制环境变量模板并填入你的配置
cp .env.example .env && open .env
```

> **注意：** 如果尚未创建 `requirements.txt` 和 `.env.example`，请参考数据分析师入职文档中的工具配置部分。

---

## 创作者第一周优先事项

以下是博主本人（内容总监）在系统上线第一周应完成的关键任务：

- [ ] **Day 1** — 通读品牌声音指南，确认人设关键词，填写所有 `[方括号]` 占位符
- [ ] **Day 1** — 通读内容支柱文档，确认六大支柱的比例是否符合当前账号策略
- [ ] **Day 2** — 填写宗门IP手册中的宗门名称、使命宣言、专属称呼和仪式感元素
- [ ] **Day 2** — 与视觉设计师确认品牌色值和字体，更新视觉识别文档
- [ ] **Day 3** — 为每个核心岗位发出入职邀请，让新成员阅读入职指南
- [ ] **Day 3** — 在 GitHub 中配置 Projects 看板（参考 PROJECT_CONFIG.md）
- [ ] **Day 4** — 确认 GitHub Actions 的 `weekly-digest.yml` 定时任务已正确启用
- [ ] **Day 5** — 召开第一次全团队同步会议，对齐系统使用方式和沟通规范

---

*本文件由团队系统自动维护。如需修改，请通过 PR 提交，经内容总监审批后合并。*
*最后更新：[更新日期] | 维护人：[内容总监姓名]*
