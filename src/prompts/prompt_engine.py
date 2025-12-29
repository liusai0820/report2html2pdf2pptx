"""
Prompt 引擎 - 智能生成高质量提示词

@input:  scenario, user_config, theme_config, methodology
@output: PromptEngine 类, generate_*_prompt() 方法
@pos:    Prompt系统的核心，动态构建AI可理解的提示词

⚠️ 一旦我被更新，务必更新：
   1. 我的头部注释
   2. /src/prompts/_FOLDER.md

核心功能：
1. 根据场景生成系统提示词
2. 根据页面类型生成页面提示词
3. 融合方法论和最佳实践
4. 支持用户配置注入
"""

from typing import Dict, Any, Optional, List
from .methodology import METHODOLOGIES, REPORT_STRUCTURES, get_methodology_prompt
from .scenario_prompts import get_scenario_prompt, get_scenario_info


class PromptEngine:
    """
    专业 Prompt 引擎
    
    设计理念：
    1. 内容为王 - 结构清晰、逻辑严密、数据支撑
    2. 场景适配 - 不同场景有不同的表达方式
    3. 方法论驱动 - 融合顶级咨询公司的思维框架
    4. 可配置 - 支持用户自定义
    """
    
    def __init__(
        self,
        scenario: str = "consulting",
        user_config: Optional[Dict[str, Any]] = None,
        theme_config: Optional[Dict[str, Any]] = None
    ):
        self.scenario = scenario
        self.user_config = user_config or {}
        self.theme_config = theme_config or {}
        self.scenario_info = get_scenario_info(scenario)
    
    def generate_system_prompt(self) -> str:
        """生成完整的系统提示词"""
        parts = []
        
        # 1. 场景专属提示词
        parts.append(get_scenario_prompt(self.scenario))
        
        # 2. 核心方法论
        parts.append(self._generate_methodology_section())
        
        # 3. 内容质量规范
        parts.append(self._generate_quality_rules())
        
        # 4. 用户上下文
        if self.user_config:
            parts.append(self._generate_user_context())
        
        # 5. 视觉规范
        if self.theme_config:
            parts.append(self._generate_visual_specs())
        
        # 6. 输出规范
        parts.append(self._generate_output_rules())
        
        return "\n\n".join(parts)
    
    def _generate_methodology_section(self) -> str:
        """生成方法论部分"""
        return """
## 核心方法论

### 金字塔原理
- 结论先行：先说结论，再说论据
- 以上统下：上层是下层的总结
- 归类分组：同层观点属于同一范畴
- 逻辑递进：按逻辑顺序排列

### MECE 原则
- 相互独立（Mutually Exclusive）
- 完全穷尽（Collectively Exhaustive）

### So What 原则
每一页都要回答：这意味着什么？我们应该怎么做？

### 行动标题原则
标题不是主题，是结论。读完标题就知道这页要说什么。
"""

    def _generate_quality_rules(self) -> str:
        """生成内容质量规范"""
        return """
## 内容质量红线

### 绝对禁止
1. ❌ 编造数据：没有的数据不要写
2. ❌ 虚构案例：没有的案例不要编
3. ❌ 空洞表述：删除所有没有信息量的话
4. ❌ 逻辑跳跃：每个结论都要有依据
5. ❌ 主题标题：标题必须是结论

### 必须做到
1. ✅ 一页一观点：每页只传达一个核心信息
2. ✅ 数据说话：用数字代替形容词
3. ✅ 结论先行：先说结论，再说论据
4. ✅ So What：每页都要有启示或建议
5. ✅ 来源标注：数据必须标注来源

### 内容密度
- 正文不要太空，也不要太满
- 关键信息要突出
- 次要信息可以精简
- 留白也是设计
"""

    def _generate_user_context(self) -> str:
        """生成用户上下文"""
        parts = ["## 项目上下文"]
        
        if self.user_config.get("organization"):
            parts.append(f"- 汇报单位：{self.user_config['organization']}")
        
        if self.user_config.get("project_name"):
            parts.append(f"- 项目名称：{self.user_config['project_name']}")
        
        if self.user_config.get("doc_type"):
            parts.append(f"- 文档类型：{self.user_config['doc_type']}")
        
        if self.user_config.get("keywords"):
            keywords = self.user_config["keywords"]
            if isinstance(keywords, list):
                keywords = "、".join(keywords)
            parts.append(f"- 主题关键词：{keywords}")
        
        if self.user_config.get("target_audience"):
            parts.append(f"- 目标受众：{self.user_config['target_audience']}")
        
        if self.user_config.get("target_pages"):
            parts.append(f"- 目标页数：{self.user_config['target_pages']} 页")
        
        depth_map = {
            "brief": "简洁版（突出重点，精简内容）",
            "normal": "标准版（平衡深度和广度）",
            "detailed": "详细版（深入分析，充分论证）"
        }
        if self.user_config.get("content_depth"):
            depth = self.user_config["content_depth"]
            parts.append(f"- 内容深度：{depth_map.get(depth, depth)}")
        
        return "\n".join(parts)
    
    def _generate_visual_specs(self) -> str:
        """生成视觉规范"""
        parts = ["## 视觉规范"]
        
        if self.theme_config.get("colors"):
            colors = self.theme_config["colors"]
            parts.append(f"- 主色调：{colors.get('primary', '#003366')}")
            parts.append(f"- 强调色：{colors.get('accent', '#FFD700')}")
        
        if self.theme_config.get("typography"):
            typo = self.theme_config["typography"]
            parts.append(f"- 正文字号：{typo.get('size_body', 20)}px")
            parts.append(f"- 标题字号：{typo.get('size_page_title', 36)}px")
        
        return "\n".join(parts)
    
    def _generate_output_rules(self) -> str:
        """生成输出规范"""
        return """
## 输出规范

### HTML 结构
- 使用预定义的 CSS 类名
- 不要生成 <style> 标签
- 不要生成 <header> 标签
- 结构清晰，语义化

### 预定义类名
- `.slide-container` - 幻灯片容器
- `.cover-slide` - 封面页
- `.section-slide` - 章节页
- `.content-area` - 内容区域
- `.page-title` - 页面标题
- `.sub-head` - 子标题
- `.big-list` - 列表
- `.data-card` - 数据卡片
- `.bottom-box` - 底部结论框
- `.clean-table` - 表格
- `.chart-container` - 图表容器

### 图表规范
- 使用 ECharts
- 设置 animation: false
- 配色使用主题色
- 字号不小于 12px
"""

    def generate_outline_prompt(self, content: str, target_pages: int = 25) -> str:
        """生成大纲规划提示词"""
        structure = REPORT_STRUCTURES.get(self.scenario, REPORT_STRUCTURES["consulting"])
        
        return f"""
# 大纲规划任务

你是一位顶级咨询公司的项目经理，需要根据以下文档内容，规划一份专业的演示文稿大纲。

## 规划原则

### 1. 结构化思维
{structure}

### 2. 内容拆分原则
- 每页只讲一个核心观点
- 数据密集的内容单独成页
- 复杂分析要拆分成多页
- 每个大章节前有章节封面

### 3. 页数控制
- 目标页数：{target_pages} 页左右
- 不要为了凑页数而注水
- 也不要为了精简而丢失重要内容

### 4. 逻辑递进
- 章节之间要有逻辑关系
- 页面之间要有过渡
- 整体要讲一个完整的故事

### 5. 🚨 严禁事项 (重要！)
- **严禁生成任何类似封面的引言页**：不要在大纲中包含"概述"、"摘要"、"导语"、"报告背景"等包含汇报人、汇报单位、日期的页面。封面信息（标题、汇报人、机构、日期）由系统自动生成，你生成的大纲应该直接从核心内容开始。
- **严禁复述大标题**：第一个 SECTION 章节应该是具体的研究/业务主题（如"研究背景"、"市场分析"），而不是重复报告大标题。
- **严禁出现"第一部分 引言"这种页面**：直接进入正题。

## 输入文档

{content[:10000]}

## 输出格式

每行一条，格式为：`类型|标题|内容要点`

类型说明：
- SECTION：章节封面页（深色背景，只有章节标题）
- CONTENT：正文页（包含具体内容）

标题要求：
- 必须是结论，不是主题
- 要有信息量
- 读完标题就知道这页要说什么

内容要点：
- 列出这页要包含的关键信息
- 包括具体数据、案例、观点
- 越详细越好，AI 生成时会用到

## 示例

SECTION|第一部分 市场分析|
CONTENT|市场规模 5 年 CAGR 达 23%，正处于爆发期|2023年市场规模500亿，预计2028年达1500亿；主要驱动因素：政策支持、技术成熟、需求释放
CONTENT|头部三家企业占据 70% 份额，竞争格局已定|A公司35%、B公司20%、C公司15%；中小企业生存空间被压缩
SECTION|第二部分 问题诊断|
CONTENT|核心问题：产品同质化严重，价格战不可持续|毛利率从40%下降到25%；研发投入不足，缺乏差异化

请开始规划大纲：
"""

    def generate_page_prompt(
        self,
        page_num: int,
        total_pages: int,
        page_data: Dict[str, Any],
        source_material: str = ""
    ) -> str:
        """生成页面内容提示词"""
        page_type = page_data.get("type", "CONTENT")
        title = page_data.get("title", "")
        content = page_data.get("content", "")
        
        # 根据页面类型生成不同的提示词
        if page_type == "COVER":
            return self._generate_cover_prompt(title, content)
        elif page_type == "AGENDA":
            return self._generate_agenda_prompt(title, content)
        elif page_type == "SECTION":
            return self._generate_section_prompt(title, content)
        elif page_type == "CLOSING":
            return self._generate_closing_prompt(title, content)
        else:
            return self._generate_content_prompt(
                page_num, total_pages, title, content, source_material
            )
    
    def _generate_cover_prompt(self, title: str, content: str) -> str:
        """生成封面页提示词"""
        from datetime import datetime
        org = self.user_config.get("organization", "汇报单位")
        doc_type = self.user_config.get("doc_type", "专项研究报告")
        # 动态获取当前日期作为默认值
        default_date = datetime.now().strftime("%Y年%m月")
        date = self.user_config.get("date", default_date)
        
        return f"""
# 封面页生成

## 要求
1. 使用 `.cover-slide` 类
2. 标题必须原封不动使用："{title}"
3. 绝对禁止修改或编造标题

## 内容
- 文档类型：{doc_type}
- 主标题：{title}
- 副标题：汇报材料
- 汇报单位：{org}
- 日期：{date}

## HTML 结构
```html
<div class="slide-container cover-slide">
    <div class="cover-top">
        <div class="brand-line"></div>
        <div class="doc-type">{doc_type}</div>
        <h1 class="main-title">{title}</h1>
        <h2 class="sub-title">汇报材料</h2>
    </div>
    <div class="cover-middle"></div>
    <div class="cover-bottom">
        <div class="footer-row">
            <div class="footer-item">汇报单位：{org}</div>
        </div>
        <div class="footer-row">
            <div class="footer-item">日期：{date}</div>
        </div>
    </div>
</div>
```

直接输出 HTML 代码：
"""

    def _generate_agenda_prompt(self, title: str, content: str) -> str:
        """生成目录页提示词"""
        return f"""
# 目录页生成

## 任务目标
将以下章节大纲内容，转换为 HTML 目录列表。

## 章节内容（数据源）
{content}

## 生成要求
1. **必须填充内容**：你必须从上面的"章节内容"中提取每一章的标题和核心观点，填入下方的 HTML 模板中。**严禁输出空的列表！**
2. **格式规范**：使用 `.catalog-list` 和 `.catalog-item` 类。
3. **序号对应**：确保序号（01, 02...）与章节内容对应。

## HTML 结构模板
```html
<div class="slide-container">
    <main class="content-area">
        <div class="title-box">
            <h1 class="page-title">目录</h1>
        </div>
        
        <!-- 目录列表容器 -->
        <div style="margin-top: 40px;">
            <div class="catalog-list">
                <!-- 请根据实际章节数量重复生成以下 item -->
                <div class="catalog-item">
                    <div class="catalog-idx">01</div> <!-- 序号 -->
                    <div class="catalog-content">
                        <div class="catalog-name">章节标题</div> <!-- 填入实际标题 -->
                        <div class="catalog-desc">章节核心观点描述...</div> <!-- 填入实际观点 -->
                    </div>
                </div>
            </div>
        </div>
    </main>
</div>
```

直接输出填充好内容的 HTML 代码：
"""

    def _generate_section_prompt(self, title: str, content: str) -> str:
        """生成章节页提示词"""
        return f"""
# 章节过场页生成

## 要求
1. 使用 `.section-slide` 类
2. 深色背景，大号标题
3. 只显示章节标题，保持极简
4. 绝对禁止添加任何额外内容

## 内容
- 章节标题：{title}

## HTML 结构
```html
<div class="slide-container section-slide">
    <div class="section-bg-pattern"></div>
    <div class="section-content">
        <div class="section-number">01</div>
        <div class="section-line"></div>
        <h1 class="section-title">{title}</h1>
    </div>
</div>
```

直接输出 HTML 代码：
"""

    def _generate_closing_prompt(self, title: str, content: str) -> str:
        """生成封底页提示词"""
        return f"""
# 封底页生成

## 要求
1. 极简设计
2. 只保留"谢谢观看"和联系方式
3. 中文表达

## HTML 结构
```html
<div class="slide-container closing-slide">
    <div class="closing-title">谢 谢 观 看</div>
    <div class="closing-contact">
        <p>如有疑问，请联系项目组</p>
    </div>
</div>
```

直接输出 HTML 代码：
"""

    def _generate_content_prompt(
        self,
        page_num: int,
        total_pages: int,
        title: str,
        content: str,
        source_material: str = ""
    ) -> str:
        """生成正文页提示词 - 增强版式与高级图表"""
        
        # 获取当前主题颜色，用于图表配色
        colors = self.theme_config.get("colors", {})
        primary = colors.get("primary", "#003366")
        accent = colors.get("accent", "#FFD700")
        # 构建图表配色数组
        chart_colors = [
            primary, 
            accent, 
            colors.get("primary_light", "#0066CC"),
            colors.get("success", "#00A86B"), 
            colors.get("warning", "#FF9500")
        ]
        chart_color_str = str(chart_colors)
        
        # 根据场景调整提示词
        scenario_tips = self._get_scenario_specific_tips()
        
        return f"""
# 正文页生成 (第 {page_num}/{total_pages} 页)

## 页面信息
- 标题：{title}
- 内容要点：{content}

## ⚠️ 物理尺寸约束 (最重要！)
**幻灯片尺寸固定为 1280×720 像素，内容区高度约 550px（扣除标题和边距）**。
你必须像设计师一样，在有限空间内合理布局，**任何超出都是失败**。

## 🚨 核心规则：防溢出第一

### 元素数量硬性限制
| 元素类型 | 最大数量 | 说明 |
|----------|----------|------|
| 数据卡片 (.data-card) | **2个/列** | 左侧最多堆叠2个，不能3个 |
| 列表项 (big-list li) | **3-4条** | 每个列表最多4条，通常3条最佳 |
| 时间线节点 | **4个** | 水平排列，不要纵向 |
| 图表高度 | **350px** | 不得超过，给底部留空 |

### 字数铁律
- **页面标题**：≤20字，确保单行
- **子标题**：≤15字
- **列表项**：每条 ≤40字（含标点）
- **底部结论**：≤35字，直接写结论，无前缀

### 布局策略
1. **优先横向**：多个元素优先横向排列（two-col/three-col），而非纵向堆叠
2. **左轻右重**：左侧放数据/要点（占比小），右侧放图表/详情（占比大）
3. **内容精简**：宁可少一个卡片，也不要溢出
4. **预留空间**：始终为 bottom-box 预留至少 80px 高度

### 生成前自检
在输出HTML前，请自问：
- [ ] 左侧是否超过2个数据卡片？→ 如果是，删减为2个
- [ ] 列表项是否超过4条？→ 如果是，合并或删减
- [ ] 图表高度是否超过350px？→ 如果是，改为350px
- [ ] 整体高度是否可能超出550px？→ 如果是，精简内容

## 当前主题配色 (ECharts专用)
JS代码中使用：`var themeColors = {chart_color_str};`

## 高级可视化菜单

### 1. [JS Chart] 动态图表 (ECharts)
**注意**：图表高度固定350px，左侧列表最多3条！
HTML 结构：
```html
<div class="slide-container">
    <main class="content-area">
        <div class="title-box"><h1 class="page-title">{title}</h1></div>
        <div class="layout-box two-col">
            <div class="col" style="flex: 1;">
                <div class="text-block">
                    <h3 class="sub-head">数据洞察</h3>
                    <ul class="big-list">
                        <li>核心观点1（最多40字）</li>
                        <li>核心观点2（最多40字）</li>
                        <li>核心观点3（最多40字）</li>
                        <!-- 最多3条！ -->
                    </ul>
                </div>
            </div>
            <div class="col" style="flex: 1.5;">
                <div class="chart-container" style="width: 100%; height: 350px;">
                    <div id="chart_{page_num}" style="width: 100%; height: 100%;"></div>
                </div>
            </div>
        </div>
        <script>
            (function(){{
                var chartDom = document.getElementById('chart_{page_num}');
                var myChart = echarts.init(chartDom);
                var themeColors = {chart_color_str};
                var option;
                // ECharts option 配置
                myChart.setOption(option);
            }})();
        </script>
        <div class="bottom-box"><div class="bottom-text">数据表明...（35字内，无前缀）</div></div>
    </main>
</div>
```

### 2. [Timeline] 发展历程/流程
HTML 结构：
```html
<div class="slide-container">
    <main class="content-area">
        <div class="title-box"><h1 class="page-title">{title}</h1></div>
        <div class="timeline-box">
            <div class="timeline-item">
                <div class="timeline-year">2023</div>
                <div class="timeline-dot"></div>
                <div class="timeline-content">
                    <div style="font-weight:bold;margin-bottom:5px;">节点名称</div>
                    <div class="timeline-text">简述...</div>
                </div>
            </div>
            <!-- ... -->
        </div>
        <div class="bottom-box"><div class="bottom-text">关键里程碑达成... (不要写前缀)</div></div>
    </main>
</div>
```

### 3. [Comparison] 左右对比
HTML 结构：
```html
<div class="slide-container">
    <main class="content-area">
        <div class="title-box"><h1 class="page-title">{title}</h1></div>
        <div class="layout-box two-col compare">
            <div class="col compare-left">
                <div class="icon-box" style="background:#e53935"><svg>...</svg></div>
                <h3 class="sub-head negative">痛点 / 现状</h3>
                <ul class="big-list">
                    <li>点1...</li>
                </ul>
            </div>
            <div class="col compare-right">
                <div class="icon-box" style="background:#43a047"><svg>...</svg></div>
                <h3 class="sub-head positive">对策 / 未来</h3>
                <ul class="big-list">
                    <li>点1...</li>
                </ul>
            </div>
        </div>
    </main>
</div>
```

### 4. [Complex Table] 复杂表格
HTML 结构：
```html
<div class="slide-container">
    <main class="content-area">
        <div class="title-box"><h1 class="page-title">{title}</h1></div>
        <div style="overflow-x: auto;">
            <table class="clean-table" style="width: 100%;">
                <thead>
                    <tr style="background-color: rgba(0,0,0,0.03);">
                        <th style="width:20%">类别</th>
                        <th style="width:40%">详情</th>
                        <th style="width:40%">备注</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="font-weight:bold;">项目A</td>
                        <td>详细内容...</td>
                        <td>说明...</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div class="bottom-box"><div class="bottom-text">表格数据分析结论... (不要写前缀)</div></div>
    </main>
</div>
```

### 5. [Three Columns] 三栏陈列
HTML 结构：
```html
<div class="slide-container">
    <main class="content-area">
        <div class="title-box"><h1 class="page-title">{title}</h1></div>
        <div class="layout-box three-col">
            <div class="col">
                <div class="data-card" style="height:100%">
                    <h3 class="sub-head">01 观点</h3>
                    <p>内容...</p>
                </div>
            </div>
            <!-- ... -->
        </div>
        <div class="bottom-box"><div class="bottom-text">三点核心总结... (不要写前缀)</div></div>
    </main>
</div>
```

### 6. [Key Metrics] 关键指标
最适合：展示 3-5 个核心数据点。

**重要规则**：
- `metric-value` 只放数字或百分比（如 `250名`、`23%`）
- `metric-label` 只放 4-6 字的短标签（如"青年干部样本"、"研发投入"）
- 如果有长描述（超过 10 个字），必须**另起一个 `.text-block`**，绝不能塞进 `metric-label` 里（否则会导致文字逐字换行变成竖排）

HTML 结构：
```html
<div class="slide-container">
    <main class="content-area">
        <div class="title-box"><h1 class="page-title">{title}</h1></div>
        <div class="metric-stack">
            <div class="metric-item">
                <div class="metric-value">250+</div>
                <div class="metric-label">青年干部样本</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">157家</div>
                <div class="metric-label">企业调研</div>
            </div>
            <div class="metric-item">
                <div class="metric-value">100亿+</div>
                <div class="metric-label">实战项目规模</div>
            </div>
            <!-- 最多放 4-5 个 -->
        </div>
        <!-- 如果有详细说明，放在这里 -->
        <div class="text-block" style="margin-top: 30px;">
            <ul class="big-list">
                <li>详细说明1：深国创中心青年干部硕士及以上占比超过80%...</li>
                <li>详细说明2：...</li>
            </ul>
        </div>
    </main>
</div>
```

## 生成要求
1. **智能选择**：根据"{content}"的内容特征，从上述菜单中选择**最恰当**的一个版式。
2. **完整代码**：输出包含 `<script>` 的完整 HTML 片段。
3. **防溢出**：时刻检查内容量，如果内容太多，请主动删减次要信息。

{scenario_tips}

## 原始素材
{source_material[:2000] if source_material else "无额外素材"}

直接输出 HTML 代码（不包含 markdown 标记）：
"""

    def _get_scenario_specific_tips(self) -> str:
        """获取场景特定提示 - 增强版：深度定制每个场景的版式和风格"""
        
        tips = {
            "consulting": """
## 🎯 咨询报告专属设计指南

### 版式选择优先级
1. **[JS Chart]** - 必须占比 40%+，数据分析是咨询报告的灵魂
   - 市场规模用面积图/柱状图
   - 增长趋势用折线图
   - 市场份额用饼图/环形图
   - 竞争对比用雷达图/柱状对比

2. **[Comparison]** - 占比 20%，用于问题诊断和方案对比
   - 现状 vs 目标
   - 痛点 vs 解决方案
   - Before vs After

3. **[Complex Table]** - 复杂数据展示
   - 竞品分析矩阵
   - SWOT 分析表格
   - 实施计划表

### 视觉风格要求
- **配色**：深蓝主色，金色强调，避免花哨
- **版式**：左文右图，信息密度高但留白充足
- **图标**：使用专业的商务图标，禁止卡通
- **字体**：严谨正式，标题加粗，正文清晰

### 内容表达规范
- **标题**：必须是结论性的，如"市场规模5年CAGR达23%，正处于爆发期"
- **数据**：每页至少1个关键数据，用大号字体突出
- **来源**：所有数据必须标注来源
- **结论**：底部结论框必须有So What

### 禁止事项 ❌
- 禁止使用卡通插画
- 禁止使用过于鲜艳的颜色
- 禁止空洞的形容词
- 禁止没有数据支撑的结论
""",
            
            "annual_review": """
## 🏆 年终述职专属设计指南

### 版式选择优先级
1. **[Key Metrics]** - 必须占比 35%+，成就要用数字说话
   - 每个成果页必须有1-2个醒目数据
   - 数字要大！要醒目！
   - 增长百分比、完成数量、排名等

2. **[Comparison]** - 占比 25%，突出对比和进步
   - 去年 vs 今年
   - 目标 vs 实际
   - 行业平均 vs 个人表现

3. **[Timeline]** - 展示项目历程和里程碑
   - 重点项目的关键节点
   - 全年工作时间线

### 视觉风格要求
- **配色**：积极向上的色调，可以更加活泼
- **版式**：成就感要强，数据要突出
- **动效**：可以使用进度条、仪表盘等
- **图标**：可使用奖杯、勋章等成就类图标

### 内容表达规范
- **开场**：一句话概括全年，要有冲击力
- **成果**：用"问题→行动→结果"结构讲故事
- **数据**：增长类数据用百分比，规模类用绝对值
- **贡献**：突出个人/团队的关键作用

### 必须包含 ✅
- 至少3页使用 [Key Metrics] 大数据展示
- 至少1页目标完成对比 ([Comparison])
- 明确的个人成长和能力提升展示
""",

            "company_intro": """
## 🚀 公司介绍专属设计指南

### 版式选择优先级
1. **[Key Metrics]** - 占比 30%，关键数字建立信任
   - 公司规模（团队人数、办公面积）
   - 业务数据（客户数、项目数、营收）
   - 行业地位（排名、市场份额）

2. **[Three Columns]** - 占比 25%，展示产品/优势
   - 产品线介绍
   - 核心优势
   - 服务类型

3. **[Timeline]** - 展示发展历程
   - 公司里程碑
   - 融资历程
   - 技术突破

### 视觉风格要求
- **配色**：使用品牌主色，现代科技感
- **版式**：视觉冲击力要强，图片占比高
- **客户**：Logo墙要显眼，证明实力
- **排版**：大标题、大图片、少文字

### 内容表达规范
- **定位**：一句话说清"我们是谁、做什么、有什么不同"
- **优势**：不说"我们最好"，而是用案例证明
- **案例**：客户痛点→解决方案→量化成果
- **CTA**：最后一页要有明确的行动号召

### 必须包含 ✅
- 公司核心数据一览（[Key Metrics]）
- 发展历程时间线
- 至少2个成功案例
- 核心团队介绍
- 明确的联系方式和合作邀请
""",

            "academic": """
## 📚 学术报告专属设计指南

### 版式选择优先级
1. **[Complex Table]** - 占比 30%+，学术规范的核心
   - 变量定义表
   - 描述性统计
   - 回归分析结果
   - 假设检验结果

2. **[JS Chart]** - 占比 30%，研究发现可视化
   - 样本分布（直方图/箱线图）
   - 时间序列（折线图）
   - 变量关系（散点图）
   - 分组对比（柱状图）

3. **文字列表** - 文献综述和讨论部分
   - 理论框架
   - 研究假设
   - 贡献与局限

### 视觉风格要求
- **配色**：学术蓝为主，克制低调
- **版式**：内容优先，装饰从简
- **字体**：正式学术字体，公式清晰
- **引用**：所有引用格式规范

### 内容表达规范
- **问题**：研究问题清晰陈述，假设明确
- **方法**：研究设计和分析方法详细说明
- **结果**：先描述后分析，遵循学术规范
- **结论**：理论贡献和实践启示分开阐述

### 学术规范要求
- 图表标题规范（图1、表2...）
- 注释和来源标注完整
- 术语使用准确一致
- 逻辑严密，论证充分

### 禁止事项 ❌
- 禁止过度装饰
- 禁止使用非学术表达
- 禁止数据模糊或缺少来源
- 禁止结论超出研究范围
""",

            "creative": """
## 🎨 创意提案专属设计指南

### 版式选择优先级
1. **视觉效果图** - 占比 40%+，创意要靠图说话
   - 效果图/mockup
   - 视觉参考
   - 传播物料示例
   - 活动场景渲染

2. **[Timeline]** - 占比 20%，执行时间线
   - 传播节奏
   - 活动流程
   - 用户旅程

3. **[Three Columns]** - 创意要素并列展示
   - 传播矩阵
   - 触点规划
   - 用户分群

### 视觉风格要求
- **配色**：大胆撞色，符合创意调性
- **版式**：打破常规，可以不对称
- **留白**：敢于大面积留白，突出创意
- **图片**：高质量视觉，是核心要素

### 内容表达规范
- **洞察**：消费者洞察要犀利、有共鸣
- **Big Idea**：一句话创意要响亮、记得住
- **执行**：要具体可落地，不能空谈
- **效果**：有对标案例支撑预估

### 创意呈现技巧
- 用"如果...那么..."句式讲故事
- 用情感连接建立共鸣
- 用反差对比制造记忆点
- 用视觉冲击抓住注意力

### 必须包含 ✅
- 消费者洞察/用户画像
- 清晰的 Big Idea
- 至少3个执行场景/物料示例
- 传播效果预估
""",

            "government": """
## 🏛️ 政府公文专属设计指南

### 版式选择优先级
1. **[Complex Table]** - 占比 35%+，公文规范的核心
   - 工作任务分解表
   - 责任分工表
   - 进度计划表
   - 考核指标表

2. **[Key Metrics]** - 占比 25%，成效数据展示
   - 完成率、覆盖率
   - 同比增长
   - 排名进步

3. **[Timeline]** - 工作进度和里程碑
   - 工作推进时间线
   - 政策落实节点
   - 重点任务进度

### 视觉风格要求
- **配色**：党政红为主，庄重稳重
- **版式**：规范整齐，格式统一
- **字体**：正式公文字体，等级分明
- **留白**：适度留白，不可过于紧凑

### 内容表达规范
- **语言**：使用规范的公文用语
- **表述**：准确、精炼、无歧义
- **数据**：务必准确，标注来源
- **措施**：具体可操作，责任明确

### 公文规范要求
- 政治表述准确（习近平新时代中国特色社会主义思想等）
- 政策依据明确
- 措施具体，避免空话套话
- 责任人、时间节点明确
- 考核机制可执行

### 禁止事项 ❌
- 禁止使用口语化表达
- 禁止编造数据
- 禁止政策表述不规范
- 禁止责任主体不明确
- 禁止只有问题没有措施
"""
        }
        return tips.get(self.scenario, tips["consulting"])



def create_prompt_engine(
    scenario: str = "consulting",
    user_config: Optional[Dict[str, Any]] = None,
    theme_config: Optional[Dict[str, Any]] = None
) -> PromptEngine:
    """创建 Prompt 引擎的便捷函数"""
    return PromptEngine(scenario, user_config, theme_config)
