# 工具套件使用说明

本目录包含健身博主团队工作流系统的所有命令行工具。

---

## 目录结构

```
tools/
├── config/                # 配置文件
│   ├── platforms.yaml     # 平台参数
│   ├── team.yaml          # 团队成员
│   └── kpis.yaml          # KPI目标
├── content_calendar/      # 内容日历工具
├── analytics/             # 数据分析工具
├── publishing/            # 发布核查工具
├── community/             # 社区管理工具
├── copywriting/           # 文案部门工具
└── utils/                 # 公共工具模块
```

---

## 前置要求

- **Python 3.9+**（推荐 3.11）
- pip 或 pip3

验证 Python 版本：
```bash
python3 --version
```

---

## 安装

### 1. 克隆仓库并进入工具目录

```bash
git clone <repo-url>
cd <repo>/tools
```

### 2. 创建虚拟环境（推荐）

```bash
python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux
# .venv\Scripts\activate    # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

---

## 配置

所有配置文件位于 `config/` 目录。首次使用前需编辑以下文件：

### config/platforms.yaml

填写各平台的账号 ID 和主页链接：

```yaml
# 将 "[账号ID]" 替换为真实账号
handle: "your_real_handle"
url: "https://www.douyin.com/user/your_id"
```

### config/team.yaml

填写团队成员信息及通知 Webhook：

```yaml
notification_channels:
  wecom_webhook: "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
  dingtalk_webhook: "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN"
```

### config/kpis.yaml

根据账号当前阶段调整 KPI 目标值（默认值适用于成长期账号）。

---

## 工具使用说明

### 内容日历工具 (`content_calendar/calendar_cli.py`)

#### 查看本周内容计划

```bash
python content_calendar/calendar_cli.py view
python content_calendar/calendar_cli.py view --week 2024-03-18
```

#### 添加新内容条目

```bash
python content_calendar/calendar_cli.py add
# 交互式填写：标题、内容支柱、平台、发布时间等
```

#### 更新内容状态

```bash
python content_calendar/calendar_cli.py status --id CB-001 --status scripting
python content_calendar/calendar_cli.py status --id CB-001 --status editing
```

可用状态：`idea` → `brief` → `scripting` → `filming` → `editing` → `review` → `scheduled` → `published`

#### 检查排期冲突

```bash
python content_calendar/calendar_cli.py conflicts
```

#### 导出周简报

```bash
python content_calendar/calendar_cli.py export --week 2024-03-18
python content_calendar/calendar_cli.py export --week 2024-03-18 --format markdown
```

---

### 数据分析工具 (`analytics/analytics_cli.py`)

#### 拉取各平台数据

```bash
# 拉取所有平台近7天数据
python analytics/analytics_cli.py pull --platform all --days 7

# 只拉取抖音数据
python analytics/analytics_cli.py pull --platform douyin --days 14
```

#### 生成周报

```bash
python analytics/analytics_cli.py report --week 2024-03-18
```

#### 生成月报

```bash
python analytics/analytics_cli.py report --month 2024-03
```

#### 趋势检测

```bash
python analytics/analytics_cli.py trends --days 30
```

#### 跨平台对比

```bash
python analytics/analytics_cli.py compare --platform douyin xiaohongshu --metric engagement_rate
python analytics/analytics_cli.py compare --platform douyin bilibili --metric new_followers
```

---

### 发布核查工具 (`publishing/publish_cli.py`)

#### 运行发布检查清单

```bash
python publishing/publish_cli.py checklist --platform douyin --id CB-001
python publishing/publish_cli.py checklist --platform xiaohongshu --id CB-002
```

#### 验证素材规格

```bash
python publishing/publish_cli.py validate --platform douyin --file /path/to/video.mp4
python publishing/publish_cli.py validate --platform xiaohongshu --file /path/to/image.jpg
```

#### 记录发布信息

```bash
python publishing/publish_cli.py log --id CB-001 --platform douyin --post-url https://www.douyin.com/video/xxxx
```

---

### 社区管理工具 (`community/community_cli.py`)

#### 评论分类处理

```bash
# 处理抖音近24小时评论
python community/community_cli.py triage --platform douyin --hours 24

# 处理小红书近48小时评论
python community/community_cli.py triage --platform xiaohongshu --hours 48
```

#### 获取回复建议

```bash
python community/community_cli.py respond --comment-id COMMENT_ID_123
```

#### 升级处理

```bash
python community/community_cli.py escalate --comment-id COMMENT_ID_123 --reason "涉及医疗建议，需创作者亲自回复"
```

#### 社区健康报告

```bash
python community/community_cli.py report --days 7
```

---

### 文案部门工具 (`copywriting/copy_cli.py`)

#### 创建文案草稿

```bash
# 创建抖音视频脚本
python copywriting/copy_cli.py create --type script --platform douyin --pillar training

# 创建小红书笔记
python copywriting/copy_cli.py create --type note --platform xiaohongshu --pillar nutrition

# 创建微博博文
python copywriting/copy_cli.py create --type weibo --platform weibo
```

可用文案类型：`script`（视频脚本）、`title`（标题+描述）、`cover`（封面文案）、`note`（小红书笔记）、`weibo`（微博博文）、`wechat`（微信推文）、`comment`（互动话术）、`live`（直播口播稿）、`commercial`（商务合作文案）、`community`（社群话术）

#### 查看文案列表

```bash
# 查看所有文案
python copywriting/copy_cli.py list

# 按状态筛选
python copywriting/copy_cli.py list --status draft
python copywriting/copy_cli.py list --status review

# 按平台筛选
python copywriting/copy_cli.py list --platform douyin
```

可用状态：`draft` → `review` → `revision` → `approved` → `published` → `archived`

#### 审核文案

```bash
python copywriting/copy_cli.py review --id CP-20240318-001
```

#### 审核通过

```bash
python copywriting/copy_cli.py approve --id CP-20240318-001
```

#### 查看话术库

```bash
# 查看全部话术库
python copywriting/copy_cli.py library

# 按支柱和平台筛选
python copywriting/copy_cli.py library --pillar training --platform douyin
```

#### 文案统计

```bash
# 近30天统计
python copywriting/copy_cli.py stats

# 自定义天数
python copywriting/copy_cli.py stats --days 7
```

---

## 数据文件位置

| 类型 | 路径 |
|------|------|
| 内容日历 | `../data/content_calendar/` |
| 分析数据 | `../data/analytics/` |
| 发布日志 | `../data/publishing_logs/` |
| 回复模板 | `../data/response_templates/` |
| 文案数据 | `../data/copywriting/` |

---

## 常见问题

**Q: 运行时报 `ModuleNotFoundError`**
A: 确认已激活虚拟环境并执行 `pip install -r requirements.txt`。

**Q: 平台 API 返回错误**
A: 检查 `config/platforms.yaml` 中 `api_enabled` 是否为 `true`，以及 API 密钥是否配置。未配置 API 时，系统会自动使用 Mock 数据（适合开发测试）。

**Q: 时区显示不正确**
A: 所有工具内部统一使用 CST（UTC+8）。如果显示异常，检查系统时区设置。

**Q: Webhook 通知未收到**
A: 检查 `config/team.yaml` 中的 webhook URL 是否正确，以及网络是否可访问企业微信/钉钉服务器。

---

## 开发说明

- 所有工具遵循 PEP 8 代码规范
- 新增功能请在 `utils/` 中添加可复用组件
- 日志文件默认输出到终端，可通过环境变量 `LOG_FILE=/path/to/log.json` 启用文件日志
