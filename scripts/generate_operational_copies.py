#!/usr/bin/env python3
"""
基于运营逻辑框架生成14条文案初稿
使用: 数据/文案/14条运营逻辑文案框架与参数配置.json
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def load_framework(framework_path: Path) -> dict:
    """加载运营逻辑框架"""
    with open(framework_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_copy_draft(copy_config: dict) -> str:
    """
    为单条文案生成草稿内容
    """
    title = copy_config.get("title")
    pillar = copy_config.get("pillar")
    platform = copy_config.get("platform")
    framework = copy_config.get("framework", {})
    params = copy_config.get("copywriter_params", {})

    # 构建草稿内容
    content = f"""# {title}

**文案ID**: {copy_config.get('id')}
**内容支柱**: {pillar}
**发布平台**: {platform}
**钩子类型**: {copy_config.get('hook_type')}
**CTA方式**: {copy_config.get('cta_type')}
**选题原因**: {copy_config.get('data_reason')}

---

## 文案框架

### 标题
{framework.get('title', title)}

### 开篇 (Hook)
{framework.get('open', '')}

### 问题陈述
{framework.get('problem', '')}

### 转折点
{framework.get('turning_point', '')}

### 解决方案
{framework.get('solution', '')}

### 行动号召 (CTA)
{framework.get('cta', '')}

---

## 撰写参数

**主题**: {params.get('topic', '')}

**核心观点**: {params.get('brief', '')}

**语调**: {params.get('tone', '')}

**关键词**: {', '.join(params.get('key_phrases', []))}

**目标受众**: {params.get('target_audience', '')}

---

## 撰写指南

基于「{pillar}」支柱的选题逻辑：

1. **钩子设计**: 使用「{copy_config.get('hook_type')}」钩子，符合历史高赞内容特征
2. **平台优化**: 针对{platform}平台的内容特性进行调整
3. **CTA选择**: 采用「{copy_config.get('cta_type')}」方式，数据显示转化率更高
4. **身体部位**: 重点突出「{copy_config.get('body_category')}」
5. **选题根据**: {copy_config.get('data_reason', '')}

---

## 内容初稿（待补充）

[此处为文案正文，遵循上述框架和参数进行撰写]

---

**生成时间**: {datetime.now().isoformat()}
**版本**: 初稿 v0.1
"""

    return content

def main():
    root_path = Path(__file__).parent.parent
    framework_path = root_path / "数据/文案/14条运营逻辑文案框架与参数配置.json"
    drafts_path = root_path / "数据/文案/草稿"

    print("="*70)
    print("🚀 基于运营逻辑框架生成14条文案初稿")
    print("="*70)

    # 加载框架
    framework = load_framework(framework_path)
    print(f"✅ 已加载框架: {len(framework['copies'])}条文案")

    # 按支柱分组
    copies_by_pillar = {}
    for copy in framework["copies"]:
        pillar = copy.get("pillar")
        if pillar not in copies_by_pillar:
            copies_by_pillar[pillar] = []
        copies_by_pillar[pillar].append(copy)

    # 生成文案
    drafts_path.mkdir(parents=True, exist_ok=True)
    generated_count = 0

    for pillar in sorted(copies_by_pillar.keys()):
        copies_in_pillar = copies_by_pillar[pillar]
        print(f"\n📌 生成【{pillar}】支柱 ({len(copies_in_pillar)}条)")

        for copy_config in copies_in_pillar:
            copy_id = copy_config.get("id")
            title = copy_config.get("title")

            # 生成草稿
            draft_content = generate_copy_draft(copy_config)

            # 保存文件
            output_file = drafts_path / f"{copy_id}.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(draft_content)

            print(f"  ✅ {copy_id}: {title[:40]}...")
            generated_count += 1

    # 生成汇总报告
    summary = {
        "campaign": {
            "name": framework.get("campaign_name"),
            "date": framework.get("campaign_date"),
            "generated_at": datetime.now().isoformat(),
        },
        "statistics": {
            "total": len(framework["copies"]),
            "generated": generated_count,
        },
        "framework_info": {
            "selection_logic": framework.get("selection_logic"),
            "pillars": list(copies_by_pillar.keys()),
        },
        "copies": [
            {
                "id": c.get("id"),
                "title": c.get("title"),
                "pillar": c.get("pillar"),
                "platform": c.get("platform"),
                "body_category": c.get("body_category"),
                "hook_type": c.get("hook_type"),
                "cta_type": c.get("cta_type"),
                "data_reason": c.get("data_reason"),
                "file": f"数据/文案/草稿/{c.get('id')}.md",
            }
            for c in framework["copies"]
        ]
    }

    summary_path = root_path / "数据/文案/汇总报告/14条文案汇总（运营逻辑版）.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # 打印总结
    print("\n" + "="*70)
    print("✅ 文案生成完成")
    print("="*70)
    print(f"\n📊 生成统计:")
    print(f"  - 总文案数: {generated_count}/{len(framework['copies'])}")
    print(f"  - 内容支柱: {len(copies_by_pillar)}种")
    print(f"\n📁 输出位置:")
    print(f"  - 初稿: {drafts_path}/OC-*.md")
    print(f"  - 汇总: {summary_path}")

    print(f"\n🎯 内容支柱分布:")
    for pillar in sorted(copies_by_pillar.keys()):
        count = len(copies_by_pillar[pillar])
        if pillar == "psychology":
            print(f"  🌊 {pillar}: {count}条 (蓝海创新项目)")
        else:
            print(f"  ✓ {pillar}: {count}条")

    print("\n✅ Phase C.B 运营逻辑版本完成!")

if __name__ == "__main__":
    main()
