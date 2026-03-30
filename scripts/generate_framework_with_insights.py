#!/usr/bin/env python3
"""
基于运营洞察生成14条文案框架
融合OperationsAgent的分析建议 + 历史数据成功模式
"""

import json
import sys
from pathlib import Path

# 添加工具路径
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

from agents.operations import OperationsAgent

def load_operational_insights():
    """加载运营洞察报告"""
    insights_path = Path(__file__).parent.parent / "docs/C-运营经验总结报告.json"
    with open(insights_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_insights_for_agent(insights: dict) -> str:
    """将洞察数据格式化为Agent可读的文本"""
    categories = insights["category_analysis"]["by_category"]
    top_categories = list(categories.items())[:5]

    hooks = insights["hook_type_analysis"]["effectiveness_ranking"][:5]
    ctas = insights["cta_type_analysis"]["effectiveness_ranking"][:5]

    success_pattern = insights["success_patterns"]["success_pattern_features"]
    top_20 = insights["success_patterns"]["top_20_entries"][:5]

    text = f"""## 数据驱动的文案生成需求

基于337条历史文案数据分析，我们发现了以下成功模式：

### 品类效果排序
"""
    for i, (cat, stats) in enumerate(top_categories, 1):
        text += f"{i}. {cat}: 平均 {stats['avg_likes']:,.0f} 赞 ({stats['count']}条)\n"

    text += f"""
### 钩子类型效果排序
"""
    for i, hook in enumerate(hooks, 1):
        text += f"{i}. {hook['hook_type']}: 平均 {hook['avg_likes']:,.0f} 赞 ({hook['count']}条)\n"

    text += f"""
### CTA类型效果排序
"""
    for i, cta in enumerate(ctas, 1):
        text += f"{i}. {cta['cta_type']}: 平均 {cta['avg_likes']:,.0f} 赞 ({cta['count']}条)\n"

    text += f"""
### Top 20高赞文案共同特征
- 最常见品类: {success_pattern['most_common_category']}
- 最常见钩子: {success_pattern['most_common_hook']}
- 最常见平台: {success_pattern['most_common_platform']}
- 最常见CTA: {success_pattern['most_common_cta']}

### 近期成功案例 (Top 5)
"""
    for i, entry in enumerate(top_20, 1):
        text += f"{i}. [{entry['category']}] {entry['title']} ({entry['likes']:,}赞)\n"
        text += f"   钩子: {entry['hook_type']}, CTA: {entry['cta_type']}, 平台: {entry['platform']}\n"

    return text

def request_agent_recommendations(insights: dict) -> str:
    """请求OperationsAgent提供14条新文案的框架建议"""
    print("🤖 调用OperationsAgent进行分析...")

    agent = OperationsAgent()

    insights_text = format_insights_for_agent(insights)

    prompt = f"""{insights_text}

## 请求

基于以上数据分析，请为我们即将发布的14条新文案生成框架建议。

**需求**:
1. 四维痛点维度（财务/职业、心理/自信、社交/魅力、健康/亚健康）
2. 14条文案应该包含的具体话题和身体部位组合
3. 每条文案建议的钩子类型（基于历史效果数据）
4. 每条文案建议的CTA方式（基于历史效果数据）
5. 平台分配建议（抖音 vs 小红书，基于平台数据特性）
6. 为什么这样分配是最优的（给出数据支撑）

**约束**:
- 总共14条文案
- 避免选择历史失败的品类（如"颜值提升"）
- 优先选择历史数据显示高效的组合
- 充分利用"反问梗式"和"感叹堆积式"钩子（历史效果最好）
- 重点使用"效果承诺型"和"行动鼓励型"CTA
- 确保品类多样性，不仅是腹肌/核心

请输出结构化的建议，包含每条文案的：
- 序号和维度
- 推荐话题
- 推荐品类
- 推荐钩子类型
- 推荐CTA方式
- 推荐平台
- 数据支撑理由
"""

    recommendation = agent.run(prompt)
    return recommendation

def save_recommendations(recommendations: str, output_path: Path):
    """保存Agent的建议"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(recommendations)
    print(f"✅ Agent建议已保存: {output_path}")

def main():
    """主流程"""
    print("="*70)
    print("🚀 Phase C.B.1 - OperationsAgent 运营经验总结")
    print("="*70)

    # 加载洞察
    insights = load_operational_insights()

    # 请求Agent分析
    recommendations = request_agent_recommendations(insights)

    # 保存建议
    output_path = Path(__file__).parent.parent / "docs/C-14条文案框架建议（Agent生成）.md"
    save_recommendations(recommendations, output_path)

    print("\n" + "="*70)
    print("✅ Phase C.B.1 完成")
    print("="*70)
    print("\nOperationsAgent建议:")
    print(recommendations)

if __name__ == "__main__":
    main()
