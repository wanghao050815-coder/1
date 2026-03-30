#!/usr/bin/env python3
"""
邪修宗运营经验总结脚本 - 分析337条历史文案数据
基于真实数据提取成功模式、钩子效果、平台差异等洞察
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any

def load_copy_library() -> Dict[str, Any]:
    """加载文案库数据"""
    lib_path = Path(__file__).parent.parent / "数据/文案/素材库/copy-library.json"
    with open(lib_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_by_dimension(entries: List[Dict]) -> Dict[str, Any]:
    """按维度分析：品类、钩子类型、平台、CTA类型"""

    # 按品类分析（category）
    category_stats = defaultdict(lambda: {"count": 0, "total_likes": 0, "total_engagement": 0, "entries": []})
    for entry in entries:
        cat = entry.get("category", "Unknown")
        category_stats[cat]["count"] += 1
        category_stats[cat]["total_likes"] += entry.get("likes", 0)
        category_stats[cat]["entries"].append({
            "title": entry.get("title"),
            "likes": entry.get("likes", 0),
            "hook_type": entry.get("hook_type"),
            "cta_type": entry.get("cta_type"),
            "platform": entry.get("platform"),
        })

    # 计算平均值并排序
    for cat in category_stats:
        stats = category_stats[cat]
        stats["avg_likes"] = stats["total_likes"] / stats["count"]
        stats["top_entries"] = sorted(
            stats["entries"],
            key=lambda x: x["likes"],
            reverse=True
        )[:3]

    # 按平均赞数排序
    sorted_categories = sorted(
        category_stats.items(),
        key=lambda x: x[1]["avg_likes"],
        reverse=True
    )

    return {
        "by_category": dict(sorted_categories),
        "total_categories": len(category_stats)
    }

def analyze_hook_types(entries: List[Dict]) -> Dict[str, Any]:
    """分析钩子类型的效果"""
    hook_stats = defaultdict(lambda: {"count": 0, "total_likes": 0, "entries": []})

    for entry in entries:
        hook = entry.get("hook_type", "Unknown")
        hook_stats[hook]["count"] += 1
        hook_stats[hook]["total_likes"] += entry.get("likes", 0)
        hook_stats[hook]["entries"].append({
            "title": entry.get("title"),
            "likes": entry.get("likes", 0),
            "category": entry.get("category"),
            "platform": entry.get("platform"),
        })

    # 计算平均值并排序
    for hook in hook_stats:
        stats = hook_stats[hook]
        stats["avg_likes"] = stats["total_likes"] / stats["count"]
        stats["top_entries"] = sorted(
            stats["entries"],
            key=lambda x: x["likes"],
            reverse=True
        )[:3]

    sorted_hooks = sorted(
        hook_stats.items(),
        key=lambda x: x[1]["avg_likes"],
        reverse=True
    )

    return {
        "by_hook_type": dict(sorted_hooks),
        "effectiveness_ranking": [
            {"hook_type": k, "avg_likes": v["avg_likes"], "count": v["count"]}
            for k, v in sorted_hooks
        ]
    }

def analyze_platform_differences(entries: List[Dict]) -> Dict[str, Any]:
    """分析抖音 vs 小红书的差异"""
    platform_stats = defaultdict(lambda: {"count": 0, "total_likes": 0, "categories": defaultdict(int), "hooks": defaultdict(int)})

    for entry in entries:
        platform = entry.get("platform", "Unknown").lower()
        platform_stats[platform]["count"] += 1
        platform_stats[platform]["total_likes"] += entry.get("likes", 0)
        platform_stats[platform]["categories"][entry.get("category")] += 1
        platform_stats[platform]["hooks"][entry.get("hook_type")] += 1

    for platform in platform_stats:
        stats = platform_stats[platform]
        stats["avg_likes"] = stats["total_likes"] / stats["count"]
        stats["top_category"] = max(
            stats["categories"].items(),
            key=lambda x: x[1]
        )[0] if stats["categories"] else None
        stats["preferred_hook"] = max(
            stats["hooks"].items(),
            key=lambda x: x[1]
        )[0] if stats["hooks"] else None

    return {
        "by_platform": dict(platform_stats),
    }

def analyze_cta_types(entries: List[Dict]) -> Dict[str, Any]:
    """分析CTA类型的效果"""
    cta_stats = defaultdict(lambda: {"count": 0, "total_likes": 0, "avg_likes": 0})

    for entry in entries:
        cta = entry.get("cta_type", "Unknown")
        cta_stats[cta]["count"] += 1
        cta_stats[cta]["total_likes"] += entry.get("likes", 0)

    for cta in cta_stats:
        cta_stats[cta]["avg_likes"] = cta_stats[cta]["total_likes"] / cta_stats[cta]["count"]

    sorted_ctas = sorted(
        cta_stats.items(),
        key=lambda x: x[1]["avg_likes"],
        reverse=True
    )

    return {
        "by_cta_type": dict(sorted_ctas),
        "effectiveness_ranking": [
            {"cta_type": k, "avg_likes": v["avg_likes"], "count": v["count"]}
            for k, v in sorted_ctas
        ]
    }

def identify_success_patterns(entries: List[Dict]) -> Dict[str, Any]:
    """识别成功模式：高赞文案的共同特征"""
    # 找出赞数最高的20条文案
    top_entries = sorted(entries, key=lambda x: x.get("likes", 0), reverse=True)[:20]

    # 统计特征
    feature_freq = {
        "categories": defaultdict(int),
        "hooks": defaultdict(int),
        "platforms": defaultdict(int),
        "ctas": defaultdict(int),
    }

    for entry in top_entries:
        feature_freq["categories"][entry.get("category")] += 1
        feature_freq["hooks"][entry.get("hook_type")] += 1
        feature_freq["platforms"][entry.get("platform")] += 1
        feature_freq["ctas"][entry.get("cta_type")] += 1

    return {
        "top_20_entries": [
            {
                "id": e.get("id"),
                "title": e.get("title"),
                "likes": e.get("likes"),
                "category": e.get("category"),
                "hook_type": e.get("hook_type"),
                "platform": e.get("platform"),
                "cta_type": e.get("cta_type"),
            }
            for e in top_entries
        ],
        "success_pattern_features": {
            "most_common_category": max(feature_freq["categories"].items(), key=lambda x: x[1])[0] if feature_freq["categories"] else None,
            "most_common_hook": max(feature_freq["hooks"].items(), key=lambda x: x[1])[0] if feature_freq["hooks"] else None,
            "most_common_platform": max(feature_freq["platforms"].items(), key=lambda x: x[1])[0] if feature_freq["platforms"] else None,
            "most_common_cta": max(feature_freq["ctas"].items(), key=lambda x: x[1])[0] if feature_freq["ctas"] else None,
        }
    }

def generate_operational_insights_report(library: Dict[str, Any]) -> Dict[str, Any]:
    """生成完整的运营洞察报告"""
    entries = library.get("entries", [])

    print("📊 正在分析337条文案历史数据...")

    category_analysis = analyze_by_dimension(entries)
    hook_analysis = analyze_hook_types(entries)
    platform_analysis = analyze_platform_differences(entries)
    cta_analysis = analyze_cta_types(entries)
    success_patterns = identify_success_patterns(entries)

    report = {
        "report_title": "邪修宗运营经验总结报告",
        "generated_at": "",
        "data_summary": {
            "total_entries": len(entries),
            "total_categories": len(set(e.get("category") for e in entries)),
            "total_platforms": len(set(e.get("platform") for e in entries)),
        },
        "category_analysis": category_analysis,
        "hook_type_analysis": hook_analysis,
        "platform_analysis": platform_analysis,
        "cta_type_analysis": cta_analysis,
        "success_patterns": success_patterns,
    }

    return report

def save_report(report: Dict[str, Any], output_path: Path):
    """保存报告为JSON"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"✅ 报告已保存: {output_path}")

def print_summary(report: Dict[str, Any]):
    """打印总结信息"""
    print("\n" + "="*70)
    print("🎯 运营经验总结 - 关键洞察")
    print("="*70)

    # 品类排序
    print("\n📁 品类效果排序 (按平均赞数):")
    categories = report["category_analysis"]["by_category"]
    for i, (cat, stats) in enumerate(categories.items(), 1):
        print(f"  {i}. {cat}: 平均{stats['avg_likes']:,.0f}赞 ({stats['count']}条)")
        if i >= 5:  # 只显示top 5
            break

    # 钩子类型排序
    print("\n🎣 钩子类型效果排序 (按平均赞数):")
    hooks = report["hook_type_analysis"]["effectiveness_ranking"]
    for i, hook_data in enumerate(hooks[:5], 1):
        print(f"  {i}. {hook_data['hook_type']}: 平均{hook_data['avg_likes']:,.0f}赞 ({hook_data['count']}条)")

    # 平台差异
    print("\n📱 平台差异:")
    platforms = report["platform_analysis"]["by_platform"]
    for platform, stats in platforms.items():
        print(f"  {platform}: 平均{stats['avg_likes']:,.0f}赞, Top品类={stats['top_category']}, 优选钩子={stats['preferred_hook']}")

    # CTA类型效果
    print("\n💬 CTA类型效果排序:")
    ctas = report["cta_type_analysis"]["effectiveness_ranking"]
    for i, cta_data in enumerate(ctas[:5], 1):
        print(f"  {i}. {cta_data['cta_type']}: 平均{cta_data['avg_likes']:,.0f}赞 ({cta_data['count']}条)")

    # 成功模式
    print("\n⭐ 高赞文案 (Top 20) 共同特征:")
    pattern = report["success_patterns"]["success_pattern_features"]
    print(f"  最常见品类: {pattern['most_common_category']}")
    print(f"  最常见钩子: {pattern['most_common_hook']}")
    print(f"  最常见平台: {pattern['most_common_platform']}")
    print(f"  最常见CTA: {pattern['most_common_cta']}")

    print("\n" + "="*70)

def main():
    """主执行流程"""
    library = load_copy_library()
    report = generate_operational_insights_report(library)

    # 保存JSON报告
    output_json = Path(__file__).parent.parent / "docs/C-运营经验总结报告.json"
    save_report(report, output_json)

    # 打印摘要
    print_summary(report)

    # 生成Markdown版本的报告
    output_md = Path(__file__).parent.parent / "docs/C-运营经验总结报告.md"
    generate_markdown_report(report, output_md)

    print(f"\n✅ 运营分析完成！")
    print(f"  - JSON报告: {output_json}")
    print(f"  - Markdown报告: {output_md}")

    return report

def generate_markdown_report(report: Dict[str, Any], output_path: Path):
    """生成Markdown格式的报告"""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    md_content = f"""# 邪修宗运营经验总结报告

**数据源**: 337条历史文案 + 互动数据
**分析时间**: {report.get('generated_at', '2026-03-30')}

## 📊 数据总览

- **总文案数**: {report['data_summary']['total_entries']}
- **品类数**: {report['data_summary']['total_categories']}
- **平台数**: {report['data_summary']['total_platforms']}

---

## 🎯 关键洞察

### 1️⃣ 品类效果排序 (按平均赞数)

"""

    categories = report["category_analysis"]["by_category"]
    for i, (cat, stats) in enumerate(categories.items(), 1):
        md_content += f"| {i} | {cat} | {stats['avg_likes']:,.0f} | {stats['count']} |\n"

    md_content += f"""
### 2️⃣ 钩子类型效果排序

"""

    hooks = report["hook_type_analysis"]["effectiveness_ranking"]
    for i, hook_data in enumerate(hooks, 1):
        md_content += f"| {i} | {hook_data['hook_type']} | {hook_data['avg_likes']:,.0f} | {hook_data['count']} |\n"

    md_content += f"""
### 3️⃣ CTA类型效果排序

"""

    ctas = report["cta_type_analysis"]["effectiveness_ranking"]
    for i, cta_data in enumerate(ctas, 1):
        md_content += f"| {i} | {cta_data['cta_type']} | {cta_data['avg_likes']:,.0f} | {cta_data['count']} |\n"

    md_content += f"""
### 4️⃣ 高赞内容 (Top 20) 共同特征

- **最常见品类**: {report['success_patterns']['success_pattern_features']['most_common_category']}
- **最常见钩子**: {report['success_patterns']['success_pattern_features']['most_common_hook']}
- **最常见平台**: {report['success_patterns']['success_pattern_features']['most_common_platform']}
- **最常见CTA**: {report['success_patterns']['success_pattern_features']['most_common_cta']}

### 5️⃣ 平台差异洞察

"""

    platforms = report["platform_analysis"]["by_platform"]
    for platform, stats in platforms.items():
        md_content += f"- **{platform.upper()}**: 平均{stats['avg_likes']:,.0f}赞, 最优品类={stats['top_category']}, 优选钩子={stats['preferred_hook']}\n"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

if __name__ == "__main__":
    main()
