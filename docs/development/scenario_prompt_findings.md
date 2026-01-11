# 发现与研究记录

## 🚨 重要发现：两套独立系统

经过分析，项目存在**两套独立的演示文稿生成系统**：

### V1 系统 (已弃用 - src/_deprecated_core/)
```
src/_deprecated_core/ai_orchestrator.py → 使用 PromptEngine
src/_deprecated_prompts/prompt_engine.py → 详细的场景 Prompt（已有 1000+ 行）
src/_deprecated_prompts/scenario_prompts.py → 场景专有 Prompt（已有 700+ 行）
```
- **已有完善的场景适配**：`_get_scenario_specific_tips()` 方法提供每个场景的版式指南
- **状态**：⚠️ 已弃用，目录已重命名为 `_deprecated_*` 避免混淆

### V2 系统 (新版 - src/v2/) ⭐ 当前主力
```
src/v2/engine.py → PresentationEngine (主引擎)
src/v2/ai_designer.py → AI 设计器 (核心)
src/server.py:57-59 → 直接引用 v2 模块
src/v2_adapter.py → V2 适配器
```
- **没有引用 src/prompts/**：V2 完全独立
- **场景适配缺失**：只有颜色差异，无内容/结构差异
- **状态**：当前生产使用

### 结论
✅ **修改 ai_designer.py 是正确的**！V2 引擎需要自己的场景适配逻辑。

---

## 🔍 代码分析发现

### 1. 场景类型定义 (design_system.py:31-38)
```python
class ScenarioType(Enum):
    CONSULTING = "consulting"           # 咨询研究/汇报
    ANNUAL_REVIEW = "annual_review"     # 年终述职/总结
    COMPANY_INTRO = "company_intro"     # 公司/项目介绍
    ACADEMIC = "academic"               # 学术研究/答辩
    CREATIVE = "creative"               # 创意/营销
    GOVERNMENT = "government"           # 政府公文
```

### 2. 当前场景仅影响颜色 (design_system.py:412-448)
- consulting: 深蓝 #003366 + 金色
- annual_review: 深蓝 #1A365D + 红色
- company_intro: 黑色 #0A0A0A + 青色
- academic: 学术蓝 #1E3A8A + 琥珀金
- creative: 紫色 #6C5CE7 + 红色
- government: 中国红 #C41E3A + 金色

### 3. 演讲稿场景适配 (ai_designer.py:1055-1081)
当前仅通过简单关键词匹配：
- "汇报" / "报告" → 工作汇报风格
- "答辩" / "评审" → 项目答辩风格
- "述职" → 述职报告风格
- 其他 → 一般性汇报

**问题**: 匹配粗糙，未与 ScenarioType 关联

### 4. System Prompt 分析 (ai_designer.py:65-103)
当前 DESIGNER_SYSTEM_PROMPT 是通用的：
- Role: Swiss Style Designer + McKinsey Analyst
- 无场景差异化人格

---

## 💡 场景特征矩阵设计

### CONSULTING (咨询研究)
```
[TONE]: McKinsey-Formal, Data-Driven, Insight-First
[STRUCTURE]: Pyramid (SCQA), Top-Down, MECE
[VISUAL]: High-Density Charts, Bento Grid, Minimal Decoration
[DATA]: Charts > Text, Quantified Conclusions
[AUDIENCE]: C-Suite, Decision Makers
```

### ANNUAL_REVIEW (年终述职)
```
[TONE]: Achievement-Oriented, Reflective, Forward-Looking
[STRUCTURE]: Timeline + Milestone, Before-After, Goal-Progress-Next
[VISUAL]: Progress Bars, Achievement Cards, Comparison Tables
[DATA]: YoY Comparison, Target vs Actual, Growth Metrics
[AUDIENCE]: Leadership, HR, Peers
```

### COMPANY_INTRO (公司介绍)
```
[TONE]: Confident, Vision-Driven, Story-Telling
[STRUCTURE]: Hero-Problem-Solution, Why-What-How
[VISUAL]: Hero Images, Bold Typography, Brand-First
[DATA]: Market Size, Growth Trajectory, Social Proof
[AUDIENCE]: Investors, Partners, Clients
```

### ACADEMIC (学术答辩)
```
[TONE]: Rigorous, Evidence-Based, Methodical
[STRUCTURE]: Literature-Method-Result-Discussion, Hypothesis-Driven
[VISUAL]: Academic Figures, Citation-Ready, Clean Layout
[DATA]: Statistical Significance, Research Charts, References
[AUDIENCE]: Committee, Peers, Academia
```

### CREATIVE (创意营销)
```
[TONE]: Bold, Inspiring, Trend-Forward
[STRUCTURE]: Hook-Story-CTA, Emotional Arc
[VISUAL]: Full-Bleed Images, Asymmetric, Dynamic
[DATA]: Engagement Metrics, Viral Stats, User Stories
[AUDIENCE]: Marketers, Creative Teams, Brands
```

### GOVERNMENT (政府公文)
```
[TONE]: Authoritative, Formal, Policy-Oriented
[STRUCTURE]: Background-Policy-Implementation-Outlook
[VISUAL]: Hierarchical, Red-Gold Accents, Symmetry
[DATA]: Policy Metrics, Coverage Stats, Implementation Progress
[AUDIENCE]: Officials, Public, Media
```

---

## 🔧 实现策略

### 策略 A: 场景 Prompt 字典 (推荐)
在 `ai_designer.py` 中新增 `SCENARIO_PROMPTS` 字典，每个场景包含：
1. `outline_guide`: 大纲结构指导 (高密度压缩)
2. `content_style`: 内容页风格 (高密度压缩)
3. `speech_tone`: 演讲稿语调 (高密度压缩)

### 策略 B: 动态 System Prompt
根据场景切换 System Prompt 人格 → 复杂度高，暂不采用

---

## 📏 高密度压缩词示例

### 原始冗长版 (约 200 tokens)
```
这是一份年终述职报告，需要强调个人在过去一年中的工作成果和贡献。
请使用时间线结构，从年初到年末按顺序展示各阶段的工作内容。
每个成果要有具体的数据支撑，如完成了多少项目、提升了多少效率等。
同时需要对不足之处进行反思，并提出下一年的改进计划...
```

### 高密度压缩版 (约 40 tokens)
```
## 🎭 SCENARIO: Annual Review (述职)
[TONE]: Achievement+Reflection | [STRUCTURE]: Timeline+Milestones
[VISUAL]: Progress-Bars, YoY-Cards | [DATA]: Target-vs-Actual, Growth%
[FOCUS]: Contribution → Learning → Next-Year-Plan
```

**压缩比**: 5:1，模型执行力更强
