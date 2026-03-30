#!/usr/bin/env python3
"""
基于运营洞察创建数据驱动的14条文案框架
不依赖API，直接基于已分析的历史数据
"""

import json
from pathlib import Path

def load_insights():
    """加载运营洞察"""
    insights_path = Path(__file__).parent.parent / "docs/C-运营经验总结报告.json"
    with open(insights_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_data_driven_framework(insights: dict) -> dict:
    """
    基于运营洞察创建框架

    策略：
    1. 利用高效钩子: 反问梗式(126K)、感叹堆积式(84K)优先
    2. 利用高效CTA: 效果承诺型(87K)、行动鼓励型(65K)优先
    3. 充分利用腹肌/核心(43.8K平均) + 背部(26.7K)
    4. 跨维度组合，避免单一品类
    5. Douyin优先(更高赞数)，部分用Xiaohongshu
    """

    framework = {
        "campaign_name": "四维痛点系列首发",
        "campaign_date": "2025-07-01 ~ 2025-07-14",
        "campaign_description": "基于337条历史文案数据分析生成的14条新文案",
        "strategy_note": "融合最高效的钩子类型、CTA方式、品类组合",
        "copies": [
            # ========== 财务与职业维度 (4条) ==========
            # PC-001: 利用反问梗式(最高效) + 效果承诺型 + 腹肌/核心
            {
                "id": "PC-001",
                "title": "背阔肌1厘米，年薪差10万？加入邪修带你抄近路！",
                "dimension": "financial",
                "platform": "douyin",
                "body_category": "背部",
                "hook_type": "反问梗式",  # 历史平均126K赞
                "cta_type": "效果承诺型",  # 历史平均87K赞
                "framework": {
                    "title": "背阔肌1厘米，年薪差10万？加入邪修带你抄近路！",
                    "open": "开篇用数据对比引发焦虑（背阔肌与收入关系）",
                    "problem": "描述职场人士因身材不够而被忽视的痛点",
                    "turning_point": "引出邪修的秘法（抄近路）",
                    "solution": "背部训练的具体方案（快速见效）",
                    "cta": "承诺效果（3个月内看到显著变化）"
                },
                "copywriter_params": {
                    "topic": "背部肌肉与职场竞争力",
                    "brief": "背阔肌发达代表气质和能力，投资健身=投资职业生涯",
                    "tone": "权威、快速、直接",
                    "key_phrases": ["年薪", "气质", "背阔肌", "秘法", "抄近路"],
                    "target_audience": "30-45岁职场人士，追求升职加薪"
                }
            },
            # PC-002: 感叹堆积式(第二高效84K) + 行动鼓励型 + Xiaohongshu
            {
                "id": "PC-002",
                "title": "【职场背肌】气质是无形的财富，这个部位弱，升职就难",
                "dimension": "financial",
                "platform": "xiaohongshu",
                "body_category": "背部",
                "hook_type": "感叹堆积式",  # 历史平均84K赞
                "cta_type": "行动鼓励型",  # 历史平均65K赞
                "framework": {
                    "title": "【职场背肌】气质是无形的财富，这个部位弱，升职就难",
                    "open": "感叹式开篇强调气质的重要性",
                    "problem": "背部不够导致气质差、升职机会少",
                    "turning_point": "气质的生物学原理（正确部位训练才有效）",
                    "solution": "背部训练的核心方法",
                    "cta": "鼓励用户立即行动，给出具体方案"
                },
                "copywriter_params": {
                    "topic": "背部气质与职场形象",
                    "brief": "背部是气质的代表，强背=强气质=更多机会",
                    "tone": "温暖、鼓励、科学",
                    "key_phrases": ["气质", "背肌", "升职", "无形资产", "机会"],
                    "target_audience": "职场女性和男性，追求形象提升"
                }
            },
            # PC-003: 问题递进式 + 效果承诺型 + 体态纠正
            {
                "id": "PC-003",
                "title": "为什么老板重用有身材的人？这个秘密你必须知道",
                "dimension": "financial",
                "platform": "douyin",
                "body_category": "体态纠正",
                "hook_type": "问题递进式",  # 历史平均29K赞
                "cta_type": "效果承诺型",
                "framework": {
                    "title": "为什么老板重用有身材的人？这个秘密你必须知道",
                    "open": "提出问题：为什么身材好的人升职快",
                    "problem": "职场中身材确实影响机会分配",
                    "turning_point": "深层原因：自律、能量、第一印象",
                    "solution": "3个月体态纠正计划",
                    "cta": "承诺升职机会增加"
                },
                "copywriter_params": {
                    "topic": "身材与职场机会的关联",
                    "brief": "自律的身材 = 高效能的信号",
                    "tone": "揭秘、权威、数据支持",
                    "key_phrases": ["老板", "身材", "秘密", "自律", "升职"],
                    "target_audience": "职场人士，想快速升职"
                }
            },
            # PC-004: 陈述式 + 自然收尾型 (虽然不是最高效，但Top 20常见)
            {
                "id": "PC-004",
                "title": "【职业蜕变】3个月身材改变，职场竞争力提升的秘密",
                "dimension": "financial",
                "platform": "xiaohongshu",
                "body_category": "综合",
                "hook_type": "陈述式",  # Top 20常见
                "cta_type": "自然收尾型",  # Top 20常见
                "framework": {
                    "title": "【职业蜕变】3个月身材改变，职场竞争力提升的秘密",
                    "open": "案例：3个月身材改变带来职场变化",
                    "problem": "职场竞争中身材确实产生差异",
                    "turning_point": "邪修宗的3个月综合计划",
                    "solution": "具体的身材改变路线",
                    "cta": "自然激励，可加入社群看更多案例"
                },
                "copywriter_params": {
                    "topic": "3个月职业蜕变案例",
                    "brief": "身材变化 = 职场能量提升 = 机会倍增",
                    "tone": "温暖、鼓励、案例驱动",
                    "key_phrases": ["3个月", "蜕变", "职业", "秘密", "竞争力"],
                    "target_audience": "想快速改变的职场人士"
                }
            },

            # ========== 心理与自信维度 (3条) ==========
            # PC-005: 反问梗式 + 行动鼓励型 + 腹肌/核心
            {
                "id": "PC-005",
                "title": "你还在为自己的身体自卑？这个秘法改变了100个人",
                "dimension": "psychological",
                "platform": "douyin",
                "body_category": "腹肌/核心",
                "hook_type": "反问梗式",  # 最高效
                "cta_type": "行动鼓励型",
                "framework": {
                    "title": "你还在为自己的身体自卑？这个秘法改变了100个人",
                    "open": "反问式触发：你是否还在自卑",
                    "problem": "身体不好导致的自卑心理",
                    "turning_point": "邪修的秘法改变了100个人",
                    "solution": "腹肌训练的心理学突破",
                    "cta": "鼓励加入，成为下一个改变的人"
                },
                "copywriter_params": {
                    "topic": "身体自信与心理突破",
                    "brief": "腹肌不仅是外表，更是内在自信",
                    "tone": "共鸣、鼓励、社群感",
                    "key_phrases": ["自卑", "秘法", "改变", "自信", "100个人"],
                    "target_audience": "有身体焦虑的人群"
                }
            },
            # PC-006: 感叹堆积式 + 自然收尾型 + 小红书
            {
                "id": "PC-006",
                "title": "30天自信心重塑计划，从身体改变开始",
                "dimension": "psychological",
                "platform": "xiaohongshu",
                "body_category": "腹肌/核心",
                "hook_type": "感叹堆积式",  # 第二高效
                "cta_type": "自然收尾型",
                "framework": {
                    "title": "30天自信心重塑计划，从身体改变开始",
                    "open": "感叹式：多少人因为身体失去自信",
                    "problem": "身体焦虑导致的心理问题",
                    "turning_point": "30天快速重塑计划",
                    "solution": "身体改变→心理改变的具体步骤",
                    "cta": "自然推进，邀请参与社群"
                },
                "copywriter_params": {
                    "topic": "30天心理重塑与身体改变",
                    "brief": "从改变身体开始重塑内在自信",
                    "tone": "温暖、科学、循序渐进",
                    "key_phrases": ["30天", "自信", "重塑", "身体改变", "心理"],
                    "target_audience": "心理焦虑的人群"
                }
            },
            # PC-007: 问题递进式 + 效果承诺型
            {
                "id": "PC-007",
                "title": "从自卑到自信的44天秘法，宗主教你",
                "dimension": "psychological",
                "platform": "douyin",
                "body_category": "综合",
                "hook_type": "反问梗式",
                "cta_type": "效果承诺型",
                "framework": {
                    "title": "从自卑到自信的44天秘法，宗主教你",
                    "open": "反问：你还要自卑多久",
                    "problem": "自卑心理的根源与表现",
                    "turning_point": "44天秘法的科学原理",
                    "solution": "具体的自信重建步骤",
                    "cta": "承诺44天内看到心理改变"
                },
                "copywriter_params": {
                    "topic": "44天自信心理重建",
                    "brief": "宗主44年经验总结成44天秘法",
                    "tone": "权威、承诺、数据驱动",
                    "key_phrases": ["44天", "秘法", "自信", "宗主", "自卑"],
                    "target_audience": "需要心理突破的人"
                }
            },

            # ========== 社交与魅力维度 (3条) ==========
            # PC-008: 感叹堆积式 + 行动鼓励型 + 胸肌/肩部
            {
                "id": "PC-008",
                "title": "吸引力提升的生物学原理，这就是为什么他更受欢迎",
                "dimension": "social",
                "platform": "douyin",
                "body_category": "胸肌/肩部",
                "hook_type": "感叹堆积式",
                "cta_type": "行动鼓励型",
                "framework": {
                    "title": "吸引力提升的生物学原理，这就是为什么他更受欢迎",
                    "open": "感叹式：为什么有人更受欢迎",
                    "problem": "身材影响社交吸引力",
                    "turning_point": "生物学原理（宽肩膀 = 吸引力信号）",
                    "solution": "胸肌肩部训练方案",
                    "cta": "鼓励立即开始变得更有魅力"
                },
                "copywriter_params": {
                    "topic": "身体吸引力与社交成功",
                    "brief": "宽肩膀、挺胸是吸引力的生物学标志",
                    "tone": "科学、激励、自信",
                    "key_phrases": ["吸引力", "生物学", "受欢迎", "肩部", "魅力"],
                    "target_audience": "想提升社交吸引力的人"
                }
            },
            # PC-009: 问题递进式 + 自然收尾型 + 小红书
            {
                "id": "PC-009",
                "title": "为什么健身的人更受欢迎？这3个原因你必须知道",
                "dimension": "social",
                "platform": "xiaohongshu",
                "body_category": "综合",
                "hook_type": "问题递进式",
                "cta_type": "自然收尾型",
                "framework": {
                    "title": "为什么健身的人更受欢迎？这3个原因你必须知道",
                    "open": "问题式开篇：为什么健身人更受欢迎",
                    "problem": "社交中身材确实产生差异",
                    "turning_point": "3个深层原因（不仅是身体，还有心态）",
                    "solution": "如何通过健身提升社交价值",
                    "cta": "自然激励，邀请分享经历"
                },
                "copywriter_params": {
                    "topic": "健身与社交成功的关联",
                    "brief": "健身改变的不仅是身体，还有人生",
                    "tone": "温暖、教育性、引人思考",
                    "key_phrases": ["受欢迎", "原因", "健身", "身体", "心态"],
                    "target_audience": "社交焦虑或想改变的人"
                }
            },
            # PC-010: 反问梗式 + 效果承诺型
            {
                "id": "PC-010",
                "title": "约到心仪的人的秘密，从改变身材开始",
                "dimension": "social",
                "platform": "douyin",
                "body_category": "胸肌/肩部/腹肌",
                "hook_type": "反问梗式",
                "cta_type": "效果承诺型",
                "framework": {
                    "title": "约到心仪的人的秘密，从改变身材开始",
                    "open": "反问：你知道约到心仪的人的秘密吗",
                    "problem": "身材不够导致的社交失败",
                    "turning_point": "秘密：先改变自己的身材",
                    "solution": "胸肌肩部腹肌的综合训练",
                    "cta": "承诺改变身材后社交机会增加"
                },
                "copywriter_params": {
                    "topic": "身材改变与社交成功",
                    "brief": "身材好 = 自信 = 吸引力 = 更多约会机会",
                    "tone": "性感、权威、承诺",
                    "key_phrases": ["约到", "秘密", "心仪", "身材", "改变"],
                    "target_audience": "单身或想脱单的人"
                }
            },

            # ========== 健康与亚健康维度 (3条) ==========
            # PC-011: 反问梗式 + 行动鼓励型 + 腹肌/核心
            {
                "id": "PC-011",
                "title": "代谢问题的宗门解决方案，不挨饿也能瘦",
                "dimension": "health",
                "platform": "douyin",
                "body_category": "腹肌/核心",
                "hook_type": "反问梗式",
                "cta_type": "行动鼓励型",
                "framework": {
                    "title": "代谢问题的宗门解决方案，不挨饿也能瘦",
                    "open": "反问式反驳常见减脂误区（节食）",
                    "problem": "亚健康的代谢问题",
                    "turning_point": "邪修的秘法：提升代谢而非节食",
                    "solution": "核心训练提升代谢的具体方案",
                    "cta": "鼓励用户尝试，承诺看到效果"
                },
                "copywriter_params": {
                    "topic": "代谢优化与健康减脂",
                    "brief": "提升代谢 = 健康减脂 = 长期瘦身",
                    "tone": "权威、健康导向、反驳伪科学",
                    "key_phrases": ["代谢", "不挨饿", "秘法", "瘦身", "健康"],
                    "target_audience": "减脂需求的健康人群"
                }
            },
            # PC-012: 感叹堆积式 + 自然收尾型 + 小红书
            {
                "id": "PC-012",
                "title": "【上班族康复】腰痛、颈椎、疲劳...一个秘法全解决",
                "dimension": "health",
                "platform": "xiaohongshu",
                "body_category": "体态纠正/核心",
                "hook_type": "感叹堆积式",
                "cta_type": "自然收尾型",
                "framework": {
                    "title": "【上班族康复】腰痛、颈椎、疲劳...一个秘法全解决",
                    "open": "感叹式列举上班族的健康问题",
                    "problem": "职业病导致的多个健康问题",
                    "turning_point": "一个秘法解决多个问题的原理",
                    "solution": "体态纠正的具体康复方案",
                    "cta": "自然邀请尝试，分享更多康复案例"
                },
                "copywriter_params": {
                    "topic": "职业病康复与体态纠正",
                    "brief": "从姿态纠正开始，解决职业病",
                    "tone": "温暖、科学、关怀",
                    "key_phrases": ["上班族", "腰痛", "颈椎", "疲劳", "一个秘法"],
                    "target_audience": "上班族和久坐人群"
                }
            },
            # PC-013: 陈述式 + 效果承诺型
            {
                "id": "PC-013",
                "title": "颈椎腰椎的终极秘法，宗主20年的训练心得",
                "dimension": "health",
                "platform": "douyin",
                "body_category": "体态纠正",
                "hook_type": "陈述式",
                "cta_type": "效果承诺型",
                "framework": {
                    "title": "颈椎腰椎的终极秘法，宗主20年的训练心得",
                    "open": "陈述式开篇：宗主20年经验",
                    "problem": "颈椎腰椎问题的普遍性",
                    "turning_point": "宗主总结的终极秘法",
                    "solution": "具体的康复训练步骤",
                    "cta": "承诺改善颈椎腰椎问题"
                },
                "copywriter_params": {
                    "topic": "脊椎健康与康复秘法",
                    "brief": "宗主20年经验 = 最可靠的康复方案",
                    "tone": "权威、专业、值得信赖",
                    "key_phrases": ["颈椎", "腰椎", "秘法", "宗主", "20年"],
                    "target_audience": "有脊椎问题的中年人"
                }
            },

            # ========== 综合维度 (1条) ==========
            # PC-014: 综合4维痛点
            {
                "id": "PC-014",
                "title": "整体蜕变的44天计划，从财务+心理+社交的三维突破",
                "dimension": "integrated",
                "platform": "xiaohongshu",
                "body_category": "综合",
                "hook_type": "陈述式",
                "cta_type": "效果承诺型",
                "framework": {
                    "title": "整体蜕变的44天计划，从财务+心理+社交的三维突破",
                    "open": "陈述式：44天整体蜕变的可能性",
                    "problem": "单一维度的改变不够，需要综合提升",
                    "turning_point": "邪修宗的三维突破模型",
                    "solution": "财务职业+心理自信+社交魅力的综合方案",
                    "cta": "承诺44天看到全面蜕变"
                },
                "copywriter_params": {
                    "topic": "44天多维度人生蜕变",
                    "brief": "身体改变只是开始，更大的是人生改变",
                    "tone": "激励、全面、蜕变导向",
                    "key_phrases": ["44天", "蜕变", "财务", "心理", "社交"],
                    "target_audience": "想全面改变人生的人"
                }
            },
        ]
    }

    return framework

def save_framework(framework: dict, output_path: Path):
    """保存框架为JSON"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(framework, f, ensure_ascii=False, indent=2)
    print(f"✅ 框架已保存: {output_path}")

def main():
    """主流程"""
    print("="*70)
    print("📋 Phase C.B.2 - 生成数据驱动的14条文案框架")
    print("="*70)

    # 加载运营洞察
    insights = load_insights()
    print(f"✅ 已加载运营洞察")

    # 创建框架
    framework = create_data_driven_framework(insights)
    print(f"✅ 框架已创建: {len(framework['copies'])}条文案")

    # 保存框架
    output_path = Path(__file__).parent.parent / "数据/文案/14条痛点文案框架与参数配置.json"
    save_framework(framework, output_path)

    # 打印摘要
    print("\n" + "="*70)
    print("📊 框架概览")
    print("="*70)

    dimensions = {}
    platforms = {}
    hook_types = {}
    cta_types = {}

    for copy in framework["copies"]:
        dim = copy["dimension"]
        dimensions[dim] = dimensions.get(dim, 0) + 1

        plat = copy["platform"]
        platforms[plat] = platforms.get(plat, 0) + 1

        hook = copy["hook_type"]
        hook_types[hook] = hook_types.get(hook, 0) + 1

        cta = copy["cta_type"]
        cta_types[cta] = cta_types.get(cta, 0) + 1

    print("\n📁 维度分布:")
    for dim, count in sorted(dimensions.items()):
        print(f"  {dim}: {count}条")

    print("\n📱 平台分布:")
    for plat, count in sorted(platforms.items()):
        print(f"  {plat}: {count}条")

    print("\n🎣 钩子类型分布:")
    for hook, count in sorted(hook_types.items()):
        print(f"  {hook}: {count}条")

    print("\n💬 CTA类型分布:")
    for cta, count in sorted(cta_types.items()):
        print(f"  {cta}: {count}条")

    print("\n✅ Phase C.B.2 完成!")

if __name__ == "__main__":
    main()
