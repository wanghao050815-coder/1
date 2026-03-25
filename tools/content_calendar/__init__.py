"""
content_calendar - 内容日历管理模块

提供内容生产流水线的完整数据模型和管理工具，包括：
- ContentItem: 单条内容的数据模型
- ContentCalendar: 日历的 CRUD 操作和查询
- Scheduler: 基于平台最优时段的自动排期建议
- ConflictChecker: 排期冲突检测
"""

import json
import os
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional

import yaml


# ─── 常量 ────────────────────────────────────────────────────

CONFIG_DIR = Path(__file__).parent.parent / "config"
DEFAULT_DATA_FILE = Path(__file__).parent / "data" / "calendar.json"

VALID_PILLARS = [
    "训练方法",
    "营养饮食",
    "体型变化",
    "健康生活方式",
    "互动问答",
    "宗门IP",
]

# 8阶段内容流水线
class Status(str, Enum):
    IDEA = "idea"
    BRIEF = "brief"
    SCRIPT = "script"
    FILMING = "filming"
    EDITING = "editing"
    REVIEW = "review"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"

# 合法的状态转换（只能向前推进，或从 review 打回 script）
VALID_TRANSITIONS = {
    Status.IDEA: [Status.BRIEF],
    Status.BRIEF: [Status.SCRIPT],
    Status.SCRIPT: [Status.FILMING],
    Status.FILMING: [Status.EDITING],
    Status.EDITING: [Status.REVIEW],
    Status.REVIEW: [Status.SCHEDULED, Status.SCRIPT],  # 可打回
    Status.SCHEDULED: [Status.PUBLISHED],
    Status.PUBLISHED: [],
}

GROWTH_POTENTIAL_LEVELS = ["high", "medium", "low"]


# ─── ContentItem ─────────────────────────────────────────────

@dataclass
class ContentItem:
    """单条内容的数据模型"""

    title: str
    platform: str
    pillar: str
    status: str = Status.IDEA.value
    scheduled_time: Optional[str] = None  # ISO 格式 "2026-03-25T18:00:00"
    assignee: Optional[str] = None
    tags: list = field(default_factory=list)
    growth_potential: str = "medium"  # high / medium / low
    is_series: bool = False
    series_name: Optional[str] = None
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        if self.status not in [s.value for s in Status]:
            raise ValueError(
                f"无效状态: {self.status}，合法状态: {[s.value for s in Status]}"
            )
        if self.growth_potential not in GROWTH_POTENTIAL_LEVELS:
            raise ValueError(
                f"无效增长潜力: {self.growth_potential}，合法值: {GROWTH_POTENTIAL_LEVELS}"
            )

    def transition_to(self, new_status: str) -> None:
        """推进内容状态，校验合法性"""
        current = Status(self.status)
        target = Status(new_status)
        if target not in VALID_TRANSITIONS.get(current, []):
            allowed = [s.value for s in VALID_TRANSITIONS.get(current, [])]
            raise ValueError(
                f"无法从 {self.status} 转到 {new_status}，允许的目标: {allowed}"
            )
        self.status = new_status
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ContentItem":
        return cls(**data)


# ─── ContentCalendar ─────────────────────────────────────────

class ContentCalendar:
    """内容日历的 CRUD 操作和查询"""

    def __init__(self, data_file: Optional[str] = None):
        self.data_file = Path(data_file) if data_file else DEFAULT_DATA_FILE
        self.items: list[ContentItem] = []
        self._load()

    def _load(self):
        if self.data_file.exists():
            with open(self.data_file, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self.items = [ContentItem.from_dict(item) for item in raw]
        else:
            self.items = []

    def _save(self):
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump([item.to_dict() for item in self.items], f, ensure_ascii=False, indent=2)

    def add(self, item: ContentItem) -> ContentItem:
        self.items.append(item)
        self._save()
        return item

    def get(self, item_id: str) -> Optional[ContentItem]:
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    def update_status(self, item_id: str, new_status: str) -> ContentItem:
        item = self.get(item_id)
        if not item:
            raise KeyError(f"未找到内容: {item_id}")
        item.transition_to(new_status)
        self._save()
        return item

    def delete(self, item_id: str) -> bool:
        item = self.get(item_id)
        if not item:
            return False
        self.items.remove(item)
        self._save()
        return True

    def query(
        self,
        platform: Optional[str] = None,
        status: Optional[str] = None,
        pillar: Optional[str] = None,
        growth_potential: Optional[str] = None,
        week_offset: int = 0,
    ) -> list[ContentItem]:
        """筛选内容条目

        Args:
            platform: 按平台筛选
            status: 按状态筛选
            pillar: 按内容支柱筛选
            growth_potential: 按增长潜力筛选
            week_offset: 按周筛选，0=本周，-1=上周，1=下周
        """
        results = self.items[:]

        if platform:
            results = [i for i in results if i.platform == platform]
        if status:
            results = [i for i in results if i.status == status]
        if pillar:
            results = [i for i in results if i.pillar == pillar]
        if growth_potential:
            results = [i for i in results if i.growth_potential == growth_potential]

        if week_offset is not None and any(i.scheduled_time for i in results):
            now = datetime.now()
            # 计算目标周的周一和周日
            days_since_monday = now.weekday()
            target_monday = now - timedelta(days=days_since_monday) + timedelta(weeks=week_offset)
            target_monday = target_monday.replace(hour=0, minute=0, second=0, microsecond=0)
            target_sunday = target_monday + timedelta(days=6, hours=23, minutes=59, seconds=59)

            filtered = []
            for item in results:
                if item.scheduled_time:
                    try:
                        st = datetime.fromisoformat(item.scheduled_time)
                        if target_monday <= st <= target_sunday:
                            filtered.append(item)
                    except ValueError:
                        filtered.append(item)
                else:
                    # 无排期时间的内容也保留（比如还在 idea 阶段）
                    if status and status in ["idea", "brief", "script", "filming", "editing"]:
                        filtered.append(item)
            results = filtered

        return results

    def stats(self) -> dict:
        """产能和状态统计"""
        status_counts = {}
        platform_counts = {}
        growth_counts = {"high": 0, "medium": 0, "low": 0}

        for item in self.items:
            status_counts[item.status] = status_counts.get(item.status, 0) + 1
            platform_counts[item.platform] = platform_counts.get(item.platform, 0) + 1
            growth_counts[item.growth_potential] = growth_counts.get(item.growth_potential, 0) + 1

        return {
            "total": len(self.items),
            "by_status": status_counts,
            "by_platform": platform_counts,
            "by_growth_potential": growth_counts,
        }


# ─── Scheduler ───────────────────────────────────────────────

class Scheduler:
    """基于平台最优时段的自动排期建议"""

    def __init__(self, calendar: ContentCalendar, platforms_config: Optional[str] = None):
        self.calendar = calendar
        config_path = Path(platforms_config) if platforms_config else CONFIG_DIR / "platforms.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            self.platforms = yaml.safe_load(f).get("platforms", {})

    def get_optimal_times(self, platform: str) -> list[str]:
        """获取指定平台的最优发布时段"""
        pconfig = self.platforms.get(platform, {})
        return pconfig.get("posting_times_cst", pconfig.get("posting_times_utc", []))

    def suggest_slots(
        self,
        platform: str,
        date_start: str,
        date_end: str,
    ) -> list[str]:
        """在指定日期范围内，返回该平台可用的发布时段

        Args:
            platform: 平台标识（如 "douyin"）
            date_start: 起始日期 "YYYY-MM-DD"
            date_end: 结束日期 "YYYY-MM-DD"

        Returns:
            可用时段列表，ISO 格式
        """
        optimal_times = self.get_optimal_times(platform)
        if not optimal_times:
            return []

        start = datetime.strptime(date_start, "%Y-%m-%d")
        end = datetime.strptime(date_end, "%Y-%m-%d")

        # 收集已占用的时段
        occupied = set()
        for item in self.calendar.items:
            if item.platform == platform and item.scheduled_time:
                occupied.add(item.scheduled_time)

        slots = []
        current = start
        while current <= end:
            for time_str in optimal_times:
                hour, minute = map(int, time_str.split(":"))
                slot = current.replace(hour=hour, minute=minute, second=0, microsecond=0)
                slot_iso = slot.isoformat()
                if slot_iso not in occupied:
                    slots.append(slot_iso)
            current += timedelta(days=1)

        return slots

    def auto_schedule(
        self,
        item: ContentItem,
        date_start: str,
        date_end: str,
        prefer_high_traffic: bool = True,
    ) -> Optional[str]:
        """为一条内容自动建议最佳发布时间

        高增长潜力内容优先占用最佳时段（如 12:00、21:00）
        """
        available = self.suggest_slots(item.platform, date_start, date_end)
        if not available:
            return None

        if item.growth_potential == "high" and prefer_high_traffic:
            # 高潜力内容优先占晚间黄金时段
            preferred = [s for s in available if "18:00" in s or "21:00" in s or "20:00" in s]
            if preferred:
                return preferred[0]

        return available[0]


# ─── ConflictChecker ─────────────────────────────────────────

class ConflictChecker:
    """排期冲突检测"""

    SAME_PLATFORM_MIN_GAP_MINUTES = 30  # 同平台至少间隔30分钟

    def __init__(self, calendar: ContentCalendar, platforms_config: Optional[str] = None):
        self.calendar = calendar
        config_path = Path(platforms_config) if platforms_config else CONFIG_DIR / "platforms.yaml"
        with open(config_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
        self.platforms = raw.get("platforms", {})

        # 从 kpis.yaml 读取发布频率上限
        kpis_path = CONFIG_DIR / "kpis.yaml"
        if kpis_path.exists():
            with open(kpis_path, "r", encoding="utf-8") as f:
                kpis_raw = yaml.safe_load(f)
            self.kpis = kpis_raw.get("kpis", {}).get("platforms", {})
        else:
            self.kpis = {}

    def check_all(self) -> list[dict]:
        """运行所有冲突检测，返回冲突列表"""
        conflicts = []
        conflicts.extend(self.check_same_platform_gap())
        conflicts.extend(self.check_daily_overload())
        conflicts.extend(self.check_cross_platform_collision())
        return conflicts

    def check_same_platform_gap(self) -> list[dict]:
        """检测同平台30分钟内的重复排期"""
        conflicts = []
        scheduled = [
            i for i in self.calendar.items
            if i.scheduled_time and i.status in ("scheduled", "review")
        ]

        # 按平台分组
        by_platform = {}
        for item in scheduled:
            by_platform.setdefault(item.platform, []).append(item)

        for platform, items in by_platform.items():
            items.sort(key=lambda x: x.scheduled_time)
            for i in range(len(items) - 1):
                t1 = datetime.fromisoformat(items[i].scheduled_time)
                t2 = datetime.fromisoformat(items[i + 1].scheduled_time)
                gap = (t2 - t1).total_seconds() / 60
                if gap < self.SAME_PLATFORM_MIN_GAP_MINUTES:
                    conflicts.append({
                        "type": "same_platform_gap",
                        "severity": "high",
                        "message": f"[{platform}] 「{items[i].title}」和「{items[i+1].title}」间隔仅{gap:.0f}分钟，建议至少间隔30分钟",
                        "items": [items[i].id, items[i + 1].id],
                    })

        return conflicts

    def check_daily_overload(self) -> list[dict]:
        """检测单日单平台超量发布"""
        conflicts = []
        scheduled = [
            i for i in self.calendar.items
            if i.scheduled_time and i.status in ("scheduled", "review")
        ]

        # 按平台+日期分组
        by_platform_date = {}
        for item in scheduled:
            try:
                dt = datetime.fromisoformat(item.scheduled_time)
                key = (item.platform, dt.strftime("%Y-%m-%d"))
                by_platform_date.setdefault(key, []).append(item)
            except ValueError:
                continue

        for (platform, date), items in by_platform_date.items():
            # 从 kpis 获取周发布频率目标，除以7得到日均上限
            platform_kpis = self.kpis.get(platform, {})
            freq = platform_kpis.get("posting_frequency", {})
            weekly_target = freq.get("stretch", freq.get("target", 7))
            daily_max = max(1, weekly_target // 3)  # 日均上限（允许集中发布但不过分）

            if len(items) > daily_max:
                conflicts.append({
                    "type": "daily_overload",
                    "severity": "medium",
                    "message": f"[{platform}] {date} 排了{len(items)}条内容，建议日均不超过{daily_max}条",
                    "items": [i.id for i in items],
                })

        return conflicts

    def check_cross_platform_collision(self) -> list[dict]:
        """检测跨平台同一时段冲突（同一时间发布多平台可能导致运营精力分散）"""
        conflicts = []
        scheduled = [
            i for i in self.calendar.items
            if i.scheduled_time and i.status in ("scheduled", "review")
        ]

        # 按时间排序
        scheduled.sort(key=lambda x: x.scheduled_time)

        for i in range(len(scheduled) - 1):
            for j in range(i + 1, len(scheduled)):
                if scheduled[i].platform == scheduled[j].platform:
                    continue
                try:
                    t1 = datetime.fromisoformat(scheduled[i].scheduled_time)
                    t2 = datetime.fromisoformat(scheduled[j].scheduled_time)
                except ValueError:
                    continue

                gap = abs((t2 - t1).total_seconds()) / 60
                if gap < 15:  # 15分钟内跨平台发布
                    conflicts.append({
                        "type": "cross_platform_collision",
                        "severity": "low",
                        "message": (
                            f"「{scheduled[i].title}」({scheduled[i].platform}) "
                            f"和「{scheduled[j].title}」({scheduled[j].platform}) "
                            f"仅间隔{gap:.0f}分钟，运营精力可能分散"
                        ),
                        "items": [scheduled[i].id, scheduled[j].id],
                    })

        return conflicts
