"""
Prompt 引擎 - 智能生成高质量提示词

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
        org = self.user_config.get("organization", "汇报单位")
        doc_type = self.user_config.get("doc_type", "专项研究报告")
        date = self.user_config.get("date", "2024年") # 获取动态日期
        
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

## 核心任务：拒绝平庸，强制多样化，严格防溢出
你需要像一位高级视觉设计师一样，选择最直观的版式。同时，必须严格控制字数，**绝对不能让内容溢出屏幕**。

### 🚨 绝对强制规则 (违反将导致任务失败)
1. **表格还原**：Markdown 表格**必须**还原为 HTML 表格 ([Complex Table])，严禁转列表。
2. **拒绝重复**：不要连续两页使用相同布局。
3. **数据可视化**：有数字必须优先用 [JS Chart] 或 [Key Metrics]。
4. **字数铁律 (防溢出)**：
   - **页面标题**：必须精简到 **20字以内**，确保不换行。
   - **底部结论**：**严禁**写"结论："、"So What："等前缀！直接写那句结论。字数必须控制在 **35字以内** (确保1行，最多2行)。
   - **正文内容**：如果文字太多，请自动精简摘要，不要照搬原文。

## 当前主题配色 (ECharts专用)
JS代码中使用：`var themeColors = {chart_color_str};`

## 高级可视化菜单

### 1. [JS Chart] 动态图表 (ECharts)
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
                        <li>核心观点1...</li>
                        <li>核心观点2...</li>
                    </ul>
                </div>
            </div>
            <div class="col" style="flex: 1.5;">
                <div class="chart-container" style="width: 100%; height: 400px;">
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
                // 此处填入 ECharts option 配置 (参考之前的示例)
                // ...
                myChart.setOption(option);
            }})();
        </script>
        <div class="bottom-box"><div class="bottom-text">数据表明... (不要写前缀，35字内)</div></div>
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
HTML 结构：
```html
<div class="slide-container">
    <main class="content-area">
        <div class="title-box"><h1 class="page-title">{title}</h1></div>
        <div class="metric-stack">
            <div class="metric-item">
                <div class="metric-value">¥500M</div>
                <div class="metric-label">营收</div>
            </div>
            <!-- ... -->
        </div>
        <div class="text-block" style="margin-top: 30px;">
            <ul class="big-list">
                <li>数据分析...</li>
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
        """获取场景特定提示 - 强制植入可视化和防溢出要求"""
        
        common_rules = """
- **数据可视化**：凡是有数据的地方，必须用 [JS Chart] 或 [Key Metrics]！
- **版式多样性**：拒绝单调，不要连续使用相同布局。
- **防止溢出**：内容要精简，确保不超出页面范围。
"""

        tips = {
            "consulting": f"""
## 咨询报告特别提示
- 分析要有深度，但结论要直接
- 建议要具体可落地
{common_rules}
""",
            "annual_review": f"""
## 年终述职特别提示
- 成果要量化，用数据说话
- 突出个人/团队贡献
{common_rules}
""",
            "company_intro": f"""
## 公司介绍特别提示
- 突出核心优势和差异化
- 用成功案例证明实力
{common_rules}
""",
            "academic": f"""
## 学术报告特别提示
- 逻辑严密，论证充分
- 术语使用要准确
{common_rules}
""",
            "creative": f"""
## 创意提案特别提示
- 观点要新颖，有冲击力
- 视觉呈现要丰富
{common_rules}
""",
            "government": f"""
## 政府汇报特别提示
- 表述规范，政治站位高
- 措施具体，责任明确
{common_rules}
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
