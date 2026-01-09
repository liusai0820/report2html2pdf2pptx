# 方案建议：Prompt 降噪与样式防御 (Prompt Compression & Defensive CSS)

## 1. 问题分析
- **图片/图表溢出**：当前 Prompt 虽然强调了"严禁溢出"，但缺乏具体的 CSS 强制手段。AI 往往生成固定高度的容器，导致内容挤出。
- **Prompt 过长 (指令稀释)**：当前的 System Prompt 约 170 行，包含了大量重复的负面约束（"禁止做这个"），导致 AI 注意力分散，容易忽略核心的布局指令。

## 2. 核心策略：高密度信息压缩 (Information Compression)
利用 LLM 的知识库，用专业术语替代冗长的描述。

| 原有描述 | 压缩后的高密度指令 | 效果 |
| :--- | :--- | :--- |
| "信息充实、视觉清晰、层次分明、统一样式..." (10+行) | **Design Philosophy: Swiss International Style** | 调动 AI 内部对瑞士平面设计风格（网格、非对称、排版优先）的理解 |
| "总分总逻辑、核心观点、层层递进..." (10+行) | **Structure: Pyramid Principle (SCQA)** | 调动 AI 对麦肯锡金字塔原理的理解 |
| "左右两栏布局、三卡片网格、列表+说明..." (10+行) | **Layout: Bento Grid / Modular Grid** | 调动 AI 对现代 UI 网格布局的理解 |
| "严禁使用红色和绿色作为对比色..." (5+行) | **Color Palette: Professional Business (No Traffic Lights)** | 简明扼要 |

## 3. 核心策略：防御性 CSS (Defensive CSS)
不再依靠 AI "自觉"遵守高度限制，而是要求它使用一套强制的 CSS 规则。

**新增指令：**
> **🛡️ IMMUTABLE CSS RULES (Must Apply):**
> 1. `* { box-sizing: border-box; min-width: 0; min-height: 0; }` (防止 Flex 子元素溢出)
> 2. Images: `img { max-width: 100%; max-height: 100%; object-fit: contain; }` (图片自适应容器)
> 3. Charts: `div[id^="chart"] { width: 100% !important; height: 100% !important; }` (图表跟随容器)
> 4. Containers: `overflow: hidden;` (强制截断溢出内容)

## 4. 修改预览 (System Prompt)

**修改前 (170行)**：
(大量的 "禁止..." "必须..." 细节描述)

**修改后 (~60行)**：

```python
DESIGNER_SYSTEM_PROMPT = """
# Role: Senior Information Designer & Art Director
# Style: Swiss International Style (Grid-based, Typography-centric, Asymmetric)

## 🎯 DESIGN PRINCIPLES (High Density)
1. **Pyramid Principle**: ONE key message per slide. Title = Conclusion.
2. **Swiss Style Layout**: Use mathematical Grids (Bento Box). Align everything.
3. **Data Visualization**: Prefer ECharts over text. "A picture is worth 1000 words."
4. **Typography**: High contrast sizes (Scale: 1.618).

## 🛡️ CANVAS PHYSICS (Immutable Laws)
- **Viewport**: 1280x720 fixed.
- **Safe Zone**: Padding 60px. **Bottom 80px is LAVA (Footer Only).**
- **Defensive CSS**:
  - Flexbox/Grid for ALL layouts.
  - `overflow: hidden` on ALL content cards.
  - Images: `object-fit: contain`, `max-height: 100%`.
  - NO fixed heights for text (use `flex: 1`).

## 🚫 STYLISTIC BANS
- No Gradients, Shadows, or 3D effects (Flat Design only).
- No Emoji. No Markdown. No "Traffic Light" colors.
"""
```

## 5. 预期收益
1. **减少溢出**：通过 CSS `object-fit` 和 `min-height: 0` 物理层面防止图片撑破布局。
2. **提升审美**：通过 "Swiss Style" 关键词，引导 AI 生成更现代、更高级的排版。
3. **响应更快**：Prompt 缩短约 60%，Token 消耗减少，推理速度略微提升。

请确认是否按此方向修改 `ai_designer.py`？
