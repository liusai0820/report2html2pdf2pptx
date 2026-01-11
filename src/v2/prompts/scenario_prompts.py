"""
场景专属 Prompt 配置

@input:  scenario 场景类型字符串
@output: get_scenario_prompts(scenario) -> 包含 outline_guide, content_style, speech_tone 的字典
@pos:    为不同汇报场景提供专属的 Prompt 指导

⚠️ 一旦我被更新，务必更新：
   1. 我的头部注释
   2. /src/v2/prompts/_FOLDER.md
"""

from typing import Dict

# ============================================================================
# 场景专属 Prompt 配置
# ============================================================================

SCENARIO_PROMPTS = {
    # ==================== 咨询研究/汇报 ====================
    "consulting": {
        "outline_guide": """
## 🎭 SCENARIO: Consulting Report (咨询研究)
[TONE]: McKinsey-Formal | Data-Driven | Insight-First | Objective
[STRUCTURE]: Pyramid (SCQA) | Top-Down | MECE Sections | Issue-Tree
[CONTENT]: Hypothesis→Evidence | So-What Analysis | Actionable Recommendations
[AUDIENCE]: C-Suite | Decision Makers | Board | Investors
""",
        "content_style": """
## 🎭 SCENARIO STYLE: Consulting
- **Layout**: High-Density Bento Grid | 2-3 Column
- **Data**: Charts > Text | Quantified Conclusions | Benchmarks
- **Visual**: Clean Swiss | Minimal Decoration | Focus on Data
- **Typography**: Bold Headlines | Tight Hierarchy | No Fluff
""",
        "speech_tone": """
**场景：咨询研究汇报**
- 语调：专业客观、数据驱动、洞察先行
- 结构：结论先行→数据支撑→建议行动
- 禁忌：模糊表述、无数据结论、过度谦虚
- 金句模式："数据显示..."、"基于分析..."、"建议采取..."
"""
    },

    # ==================== 年终述职/总结 ====================
    "annual_review": {
        "outline_guide": """
## 🎭 SCENARIO: Annual Review (年终述职)
[TONE]: Achievement-Oriented | Reflective | Forward-Looking | Humble-Confident
[STRUCTURE]: Timeline+Milestones | Goal-Progress-Next | Before-After
[CONTENT]: Contribution→Learning→Growth→Plan | Quantified Achievements
[AUDIENCE]: Leadership | HR | Peers | Self-Reflection
""",
        "content_style": """
## 🎭 SCENARIO STYLE: Annual Review
- **Layout**: Timeline View | Progress Cards | Comparison Tables
- **Data**: YoY Growth | Target-vs-Actual | Milestone Markers
- **Visual**: Achievement Badges | Progress Bars | Growth Arrows
- **Typography**: Celebratory Highlights | Personal Voice
""",
        "speech_tone": """
**场景：年终述职**
- 语调：自信而不自夸、反思而不推诿、展望而不空洞
- 结构：回顾成果→总结经验→反思不足→明年计划
- 禁忌：过度自夸、逃避问题、空洞承诺
- 金句模式："这一年完成了..."、"从中学到..."、"下一年将..."
"""
    },

    # ==================== 公司/项目介绍 ====================
    "company_intro": {
        "outline_guide": """
## 🎭 SCENARIO: Company/Project Intro (公司介绍)
[TONE]: Confident | Vision-Driven | Story-Telling | Inspiring
[STRUCTURE]: Hero-Problem-Solution | Why-What-How | Origin→Now→Future
[CONTENT]: Mission+Vision | Market Opportunity | Competitive Edge | Team
[AUDIENCE]: Investors | Partners | Clients | Talent
""",
        "content_style": """
## 🎭 SCENARIO STYLE: Company Intro
- **Layout**: Hero Images | Bold Full-Width | Brand-First
- **Data**: Market Size | Growth Trajectory | Social Proof
- **Visual**: Cinematic | High-Impact | Logo Prominent
- **Typography**: Bold Display | Aspirational Headlines
""",
        "speech_tone": """
**场景：公司/项目介绍**
- 语调：自信有感染力、讲故事、激发共鸣
- 结构：痛点引入→解决方案→为何是我们→合作邀约
- 禁忌：自说自话、缺乏差异化、无社会证明
- 金句模式："我们的使命是..."、"市场规模达..."、"已服务..."
"""
    },

    # ==================== 学术研究/答辩 ====================
    "academic": {
        "outline_guide": """
## 🎭 SCENARIO: Academic/Thesis (学术答辩)
[TONE]: Rigorous | Evidence-Based | Methodical | Scholarly
[STRUCTURE]: Literature-Gap-Method-Result-Discussion | Hypothesis-Driven
[CONTENT]: Research Question | Methodology | Findings | Contribution | Limitation
[AUDIENCE]: Committee | Professors | Peers | Academic Community
""",
        "content_style": """
## 🎭 SCENARIO STYLE: Academic
- **Layout**: Clean Academic | Figure-Centric | Citation-Ready
- **Data**: Statistical Charts | Research Figures | Reference Tables
- **Visual**: Minimal | Formal | Diagram-Heavy | Numbered Figures
- **Typography**: Serif-Friendly | Clear Hierarchy | Footnote-Ready
""",
        "speech_tone": """
**场景：学术答辩**
- 语调：严谨客观、有理有据、谦逊但自信
- 结构：研究背景→方法论→核心发现→贡献与局限→未来方向
- 禁忌：过度主观、忽略局限性、无文献支撑
- 金句模式："研究表明..."、"实验结果显示..."、"本研究的贡献在于..."
"""
    },

    # ==================== 创意/营销 ====================
    "creative": {
        "outline_guide": """
## 🎭 SCENARIO: Creative/Marketing (创意营销)
[TONE]: Bold | Inspiring | Trend-Forward | Emotionally-Engaging
[STRUCTURE]: Hook-Story-CTA | Emotional Arc | Problem-Agitate-Solve
[CONTENT]: Big Idea | Creative Concept | Campaign Mechanics | Expected Impact
[AUDIENCE]: Marketers | Creative Teams | Brands | Consumers
""",
        "content_style": """
## 🎭 SCENARIO STYLE: Creative
- **Layout**: Asymmetric | Dynamic | Full-Bleed Images
- **Data**: Engagement Metrics | Viral Stats | User Stories
- **Visual**: Bold Colors | Trend-Aware | Moodboard-Style
- **Typography**: Expressive | Playful | Impactful Quotes
""",
        "speech_tone": """
**场景：创意营销提案**
- 语调：充满激情、引发共鸣、创意先行
- 结构：洞察引爆→创意概念→执行方案→预期效果
- 禁忌：平淡无奇、缺乏情感、只谈执行不谈创意
- 金句模式："想象一下..."、"我们的洞察是..."、"这将引发..."
"""
    },

    # ==================== 政府公文 ====================
    "government": {
        "outline_guide": """
## 🎭 SCENARIO: Government Report (政府公文)
[TONE]: Authoritative | Formal | Policy-Oriented | Public-Serving
[STRUCTURE]: Background-Policy-Implementation-Outlook | 总-分-总
[CONTENT]: Policy Context | Implementation Progress | Challenges | Next Steps
[AUDIENCE]: Officials | Public | Media | Stakeholders
""",
        "content_style": """
## 🎭 SCENARIO STYLE: Government
- **Layout**: Hierarchical | Symmetrical | Red-Gold Accents
- **Data**: Policy Metrics | Coverage Stats | Implementation Timeline
- **Visual**: Formal | Emblem-Ready | Clean Official
- **Typography**: Formal Serif | Clear Hierarchy | Numbered Points
""",
        "speech_tone": """
**场景：政府工作报告**
- 语调：庄重权威、为民服务、实事求是
- 结构：总体成绩→重点工作→存在问题→下步计划
- 禁忌：夸大其词、回避问题、形式主义
- 金句模式："在...指导下..."、"全面完成..."、"下一步将..."
"""
    },
}

# 场景别名映射（兼容旧版字符串匹配）
SCENARIO_ALIASES = {
    "汇报": "consulting",
    "报告": "consulting",
    "研究": "consulting",
    "咨询": "consulting",
    "述职": "annual_review",
    "年终": "annual_review",
    "总结": "annual_review",
    "介绍": "company_intro",
    "公司": "company_intro",
    "项目": "company_intro",
    "答辩": "academic",
    "论文": "academic",
    "学术": "academic",
    "评审": "academic",
    "创意": "creative",
    "营销": "creative",
    "政府": "government",
    "公文": "government",
}


def get_scenario_prompts(scenario: str) -> Dict[str, str]:
    """
    获取场景专有 Prompt

    Args:
        scenario: 场景类型字符串 (如 'consulting', 'annual_review' 或中文关键词)

    Returns:
        包含 outline_guide, content_style, speech_tone 的字典
    """
    # 直接匹配
    if scenario in SCENARIO_PROMPTS:
        return SCENARIO_PROMPTS[scenario]

    # 别名匹配
    for keyword, mapped_scenario in SCENARIO_ALIASES.items():
        if keyword in scenario:
            return SCENARIO_PROMPTS[mapped_scenario]

    # 默认返回咨询风格
    return SCENARIO_PROMPTS["consulting"]
