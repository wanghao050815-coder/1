#!/usr/bin/env python3
"""
邪修宗人设一致性分析器

用于评估文案是否符合邪修宗的人设特征，给出评分和改进建议。
使用OpenAI API进行深度语言分析。
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple
from anthropic import Anthropic

# =============================================================================
# 数据类
# =============================================================================

@dataclass
class PersonalityAnalysis:
    """人设分析结果"""
    copy_id: str
    original_text: str

    # 三个核心评分
    personality_consistency_score: float  # 0-100，人设一致性
    pain_point_resonance_score: float     # 0-10，痛点共鸣度
    sect_identity_strength: float         # 0-10，宗门身份强度

    # 详细反馈
    strengths: List[str]                  # 做得好的方面
    weaknesses: List[str]                 # 需要改进的方面
    suggestions: List[str]                # 改进建议

    # 改进版本
    revised_copy: str = None              # 改进后的文案（可选）

    def __post_init__(self):
        """验证评分范围"""
        assert 0 <= self.personality_consistency_score <= 100
        assert 0 <= self.pain_point_resonance_score <= 10
        assert 0 <= self.sect_identity_strength <= 10

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'copy_id': self.copy_id,
            'personality_consistency_score': round(self.personality_consistency_score, 1),
            'pain_point_resonance_score': round(self.pain_point_resonance_score, 1),
            'sect_identity_strength': round(self.sect_identity_strength, 1),
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'suggestions': self.suggestions,
            'revised_copy': self.revised_copy,
        }


# =============================================================================
# 人设分析器
# =============================================================================

class PersonalityAnalyzer:
    """邪修宗人设一致性分析器"""

    def __init__(self):
        """初始化分析器"""
        self.client = Anthropic()

        # 人设的核心特征定义
        self.personality_traits = {
            'authority': {
                'description': '权威感 — 掌握秘法的教练',
                'keywords': ['秘法', '宗主', '邪修', '传你', '教你'],
                'anti_keywords': ['建议您', '可能会', '也许', '医学证明'],
                'weight': 0.30
            },
            'differentiation': {
                'description': '差异化 — 邪修 vs 正派',
                'keywords': ['邪修', '正派', '对比', '对照', '不同'],
                'anti_keywords': [],
                'weight': 0.30
            },
            'reliability': {
                'description': '可靠性 — 效果可见',
                'keywords': ['就有', '就能', '就会', '立刻', '明显'],
                'anti_keywords': ['可能改善', '有助于', '促进', '改善'],
                'weight': 0.25
            },
            'closeness': {
                'description': '亲近感 — 一个人在说话',
                'keywords': ['我们', '咱们', '你就', '随便', '这玩意儿'],
                'anti_keywords': ['患者', '建议您', '进行', '实施'],
                'weight': 0.15
            }
        }

    def analyze_copy(self, copy_id: str, copy_text: str, dimension: str = None) -> PersonalityAnalysis:
        """
        分析单条文案的人设一致性

        Args:
            copy_id: 文案ID
            copy_text: 文案内容
            dimension: 痛点维度（可选）

        Returns:
            PersonalityAnalysis 对象
        """

        # 步骤1：计算基础评分
        trait_scores = self._calculate_trait_scores(copy_text)
        consistency_score = self._calculate_consistency_score(trait_scores)
        pain_point_score = self._evaluate_pain_point_resonance(copy_text, dimension)
        sect_identity_score = self._evaluate_sect_identity_strength(copy_text)

        # 步骤2：识别优势和劣势
        strengths, weaknesses = self._identify_strengths_and_weaknesses(
            copy_text, trait_scores, consistency_score
        )

        # 步骤3：生成改进建议
        suggestions = self._generate_suggestions(copy_text, weaknesses)

        # 步骤4：如果分数过低，生成改进版本
        revised_copy = None
        if consistency_score < 70:
            revised_copy = self._generate_revised_copy(copy_text, dimension, weaknesses)

        return PersonalityAnalysis(
            copy_id=copy_id,
            original_text=copy_text,
            personality_consistency_score=consistency_score,
            pain_point_resonance_score=pain_point_score,
            sect_identity_strength=sect_identity_score,
            strengths=strengths,
            weaknesses=weaknesses,
            suggestions=suggestions,
            revised_copy=revised_copy
        )

    def _calculate_trait_scores(self, copy_text: str) -> Dict[str, float]:
        """计算每个人设特征的评分"""
        scores = {}

        for trait_name, trait_info in self.personality_traits.items():
            keywords = trait_info['keywords']
            anti_keywords = trait_info['anti_keywords']

            # 计算关键词出现频率
            keyword_count = sum(copy_text.count(kw) for kw in keywords)
            anti_keyword_count = sum(copy_text.count(kw) for kw in anti_keywords)

            # 评分公式：关键词越多越好，反义词越多越坏
            max_count = len(keywords) * 3  # 假设最多出现3次
            score = max(0, (keyword_count - anti_keyword_count * 2) / max_count * 100)

            scores[trait_name] = min(100, score)

        return scores

    def _calculate_consistency_score(self, trait_scores: Dict[str, float]) -> float:
        """计算总体人设一致性评分"""
        weighted_score = 0
        for trait_name, score in trait_scores.items():
            weight = self.personality_traits[trait_name]['weight']
            weighted_score += score * weight
        return weighted_score

    def _evaluate_pain_point_resonance(self, copy_text: str, dimension: str = None) -> float:
        """评估痛点共鸣度（0-10）"""

        # 痛点共鸣的指标
        resonance_indicators = {
            'financial': ['职场', '薪资', '竞争力', '升职', '气质', '形象'],
            'psychological': ['自卑', '自信', '焦虑', '心理', '蜕变'],
            'social': ['吸引', '社交', '被看见', '魅力', '聚会'],
            'health': ['代谢', '疲劳', '腰痛', '颈椎', '亚健康']
        }

        # 问题陈述的强度指标
        problem_strength_indicators = ['为什么', '怎么办', '问题', '困扰', '困难']

        score = 0

        # 检查痛点相关词汇
        if dimension and dimension in resonance_indicators:
            keywords = resonance_indicators[dimension]
            keyword_count = sum(copy_text.count(kw) for kw in keywords)
            score += min(5, keyword_count)  # 最多5分

        # 检查问题表述强度
        problem_count = sum(copy_text.count(ind) for ind in problem_strength_indicators)
        score += min(5, problem_count * 0.5)  # 最多5分

        return score / 10 * 10  # 转换为0-10的评分

    def _evaluate_sect_identity_strength(self, copy_text: str) -> float:
        """评估宗门身份强度（0-10）"""

        sect_keywords = {
            '邪修': 2,
            '宗主': 2,
            '秘法': 2,
            '抄近路': 1,
            '宗门': 1,
            '对于我们': 1.5,
            '对于咱们': 1.5,
        }

        score = 0
        for kw, points in sect_keywords.items():
            count = copy_text.count(kw)
            score += count * points

        # 标准化到0-10
        return min(10, score)

    def _identify_strengths_and_weaknesses(
        self, copy_text: str, trait_scores: Dict[str, float], consistency_score: float
    ) -> Tuple[List[str], List[str]]:
        """识别优势和劣势"""

        strengths = []
        weaknesses = []

        # 识别表现好的特征
        for trait_name, score in trait_scores.items():
            trait_description = self.personality_traits[trait_name]['description']
            if score >= 70:
                strengths.append(f"✅ {trait_description} — 评分 {score:.0f}/100")
            elif score < 50:
                weaknesses.append(f"❌ {trait_description} — 评分 {score:.0f}/100，需要加强")

        # 检查禁忌词汇
        forbidden_phrases = [
            ('医学证明', '医疗相关语言'),
            ('建议您', '过度正式语言'),
            ('可能改善', '模糊承诺'),
            ('进行', '书面语'),
            ('患者', '不匹配的用词'),
        ]

        for phrase, reason in forbidden_phrases:
            if phrase in copy_text:
                weaknesses.append(f"⚠️  存在禁忌表达 '{phrase}' — {reason}")

        # 检查是否有强有力的开篇
        if not any(phrase in copy_text for phrase in ['对于我们', '对于咱们', '这玩意儿']):
            weaknesses.append("⚠️  开篇身份确立不够强——缺少'对于我们'的表述")

        # 检查是否有明确的效果承诺
        if not any(word in copy_text for word in ['就有', '就能', '就会', '立刻', '明显']):
            weaknesses.append("⚠️  效果承诺不够明确——缺少明确的效果描述")

        return strengths, weaknesses

    def _generate_suggestions(self, copy_text: str, weaknesses: List[str]) -> List[str]:
        """生成改进建议"""
        suggestions = []

        for weakness in weaknesses:
            if '身份确立' in weakness:
                suggestions.append("💡 在开篇加入'对于我们邪修来说'来建立身份")
            elif '效果承诺' in weakness:
                suggestions.append("💡 将'可能改善'改为'就有'、'就能'等更确定的表述")
            elif '医学' in weakness or '医疗' in weakness:
                suggestions.append("💡 避免医学语言，改用'改善'、'强化'等健身术语")
            elif '正式语言' in weakness:
                suggestions.append("💡 将'建议您'改为'你就这样做'，保持口语化亲近感")
            elif '宗门' in weakness:
                suggestions.append("💡 增加'秘法'、'宗主'、'邪修'等宗门术语，强化IP感")

        return suggestions

    def _generate_revised_copy(
        self, copy_text: str, dimension: str, weaknesses: List[str]
    ) -> str:
        """生成改进版本的文案"""

        prompt = f"""请根据以下反馈改进这条文案，使其更符合邪修宗的人设特征：

**原始文案：**
{copy_text}

**维度：** {dimension}

**需要改进的方面：**
{chr(10).join('- ' + w for w in weaknesses[:3])}

**改进要求：**
1. 保持原始含义和逻辑
2. 加强宗门身份感（邪修、宗主、秘法）
3. 使用口语化的亲近表达
4. 给出更明确的效果承诺
5. 避免医学和过度正式的语言

请直接输出改进后的文案，不需要解释。"""

        # 调用Claude API
        message = self.client.messages.create(
            model="claude-opus-4-6",
            max_tokens=500,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return message.content[0].text

    def batch_analyze(self, copies: Dict[str, Dict]) -> List[PersonalityAnalysis]:
        """批量分析多条文案

        Args:
            copies: {
                'PC-001': {'text': '文案内容', 'dimension': '财务'},
                ...
            }

        Returns:
            PersonalityAnalysis 列表
        """
        results = []

        for copy_id, copy_info in copies.items():
            result = self.analyze_copy(
                copy_id=copy_id,
                copy_text=copy_info['text'],
                dimension=copy_info.get('dimension')
            )
            results.append(result)

        return results

    def generate_report(self, analyses: List[PersonalityAnalysis]) -> Dict:
        """生成分析报告"""

        avg_consistency = sum(a.personality_consistency_score for a in analyses) / len(analyses)
        avg_pain_point = sum(a.pain_point_resonance_score for a in analyses) / len(analyses)
        avg_sect_identity = sum(a.sect_identity_strength for a in analyses) / len(analyses)

        # 识别需要改进的文案
        low_score_copies = [
            a.copy_id for a in analyses
            if a.personality_consistency_score < 70
        ]

        return {
            'summary': {
                'total_copies': len(analyses),
                'avg_personality_consistency_score': round(avg_consistency, 1),
                'avg_pain_point_resonance_score': round(avg_pain_point, 1),
                'avg_sect_identity_strength': round(avg_sect_identity, 1),
                'high_quality_count': len([a for a in analyses if a.personality_consistency_score >= 80]),
                'needs_revision_count': len(low_score_copies)
            },
            'low_score_copies': low_score_copies,
            'details': [a.to_dict() for a in analyses]
        }


# =============================================================================
# 主函数
# =============================================================================

def main():
    """示例使用"""

    analyzer = PersonalityAnalyzer()

    # 示例文案
    test_copy = """
    仰卧起坐？狗都不_！腹肌高效训练！宗主带你抄近路！

    对于我们邪修修来说啊，腹肌怎么练？这么跟你说啊，想练腹做卷腹，结果他妈脖子嘎嘎酸啊，腹肌没感觉。
    对于我们邪修修来说有就这一个秘法，咱们随便一躺，抬腿，手背伸直，腰压紧地面，腿往最高最远处伸，在原路返回。
    你就这样做，你的腹肌才能稳扎稳打。
    """

    # 分析
    result = analyzer.analyze_copy(
        copy_id='TEST-001',
        copy_text=test_copy,
        dimension='psychological'
    )

    print("=" * 80)
    print("人设一致性分析结果")
    print("=" * 80)
    print(f"\n文案ID: {result.copy_id}")
    print(f"人设一致性评分: {result.personality_consistency_score:.1f}/100")
    print(f"痛点共鸣度: {result.pain_point_resonance_score:.1f}/10")
    print(f"宗门身份强度: {result.sect_identity_strength:.1f}/10")

    print(f"\n✅ 优势:")
    for s in result.strengths:
        print(f"  {s}")

    print(f"\n⚠️  需要改进:")
    for w in result.weaknesses:
        print(f"  {w}")

    print(f"\n💡 建议:")
    for s in result.suggestions:
        print(f"  {s}")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
