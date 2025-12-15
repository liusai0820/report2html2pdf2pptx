"""
Prompt 生成器 - 根据主题动态生成 AI 提示词

功能:
1. 根据主题生成系统提示词
2. 根据主题生成页面生成提示词
3. 支持用户自定义配置注入
"""

from typing import Dict, Any, Optional
from .theme_manager import Theme


class PromptGenerator:
    """提示词生成器"""
    
    def __init__(self, theme: Theme, user_config: Optional[Dict[str, Any]] = None):
        self.theme = theme
        self.user_config = user_config or {}
    
    def generate_system_prompt(self) -> str:
        """生成系统提示词"""
        t = self.theme
        
        # 根据主题类别生成不同的角色定位
        role_descriptions = {
            "consulting": "你是一位顶级战略咨询公司的首席汇报材料专家，擅长制作政府汇报、咨询报告等正式文档。",
            "annual_review": "你是一位资深的企业管理顾问，擅长制作年终总结、述职报告等成果展示文档。",
            "company_intro": "你是一位专业的品牌策划师，擅长制作公司介绍、项目路演等商业展示文档。",
            "academic": "你是一位学术研究专家，擅长制作学术报告、论文答辩等学术展示文档。",
            "creative": "你是一位创意总监，擅长制作品牌推广、营销方案等创意展示文档。",
        }
        
        role = role_descriptions.get(t.metadata.category, role_descriptions["consulting"])
        
        # 获取用户自定义配置
        org_name = self.user_config.get("organization", "")
        project_name = self.user_config.get("project_name", "")
        keywords = self.user_config.get("keywords", [])
        
        return f"""# {t.metadata.name} 设计系统

{role}
你的任务是输出符合【{t.metadata.name}】风格的专业演示文稿。

## 0. 最高原则：内容忠实度 (Content Fidelity)

**你的所有输出必须严格基于提供的【原始内容】。**

1. **严禁编造数据**：绝对不允许为了排版好看而编造虚假的增长率、金额、人数等数据。
2. **严禁虚构案例**：不要编造不存在的企业名称或合作项目。
3. **信达雅**：你可以对文字进行润色、总结、提炼，但不能改变原意。
4. **处理缺失**：如果内容太少，请如实总结或调整版式，而不是编造废话填充。

## 1. 核心禁令 (Strict Rules)

1. **禁止英文装饰**：严禁出现 "Company Confidential", "Agenda" 等英文装饰词。
2. **禁止虚构内容**：封面标题必须严格等于用户提供的标题。
3. **禁止小字号**：正文最小字号不得小于 {t.typography.size_body}px。
4. **禁止 Emoji**：严禁使用 💡, 🚀 等图标。

## 2. 视觉规范

### 配色方案
- 主色调: {t.colors.primary}
- 强调色: {t.colors.primary_light}
- 点缀色: {t.colors.accent}
- 主文字: {t.colors.text_primary}
- 次要文字: {t.colors.text_secondary}
- 背景色: {t.colors.background}
- 备选背景: {t.colors.background_alt}

### 字体排版规范
- 字体: {t.typography.font_family}
- 封面大标题: {t.typography.size_cover_title}px
- 页面主标题: {t.typography.size_page_title}px
- 章节标题: {t.typography.size_section_title}px
- 一级观点: {t.typography.size_heading}px
- 正文/列表: {t.typography.size_body}px
- 图表/注释: {t.typography.size_small}px

{self._generate_user_context_section()}

## 3. 页面 HTML 结构模板

{self._generate_template_section()}

## 4. CSS 类名参考

使用以下预定义的 CSS 类名：
- `.slide-container` - 幻灯片容器
- `.cover-slide` - 封面页
- `.section-slide` - 章节过场页
- `.content-area` - 内容区域
- `.page-title` - 页面标题
- `.sub-head` - 子标题
- `.big-list` - 大号列表
- `.data-card` - 数据卡片
- `.data-val` - 数据值
- `.data-lbl` - 数据标签
- `.bottom-box` - 底部结论框
- `.clean-table` - 表格
- `.chart-container` - 图表容器

**绝对禁止在输出中包含 `<style>` 标签，所有样式由外部模板提供。**
"""

    def _generate_user_context_section(self) -> str:
        """生成用户上下文部分"""
        sections = []
        
        if self.user_config.get("organization"):
            sections.append(f"- 汇报单位: {self.user_config['organization']}")
        
        if self.user_config.get("project_name"):
            sections.append(f"- 项目名称: {self.user_config['project_name']}")
        
        if self.user_config.get("keywords"):
            keywords = ", ".join(self.user_config["keywords"])
            sections.append(f"- 主题关键词: {keywords}")
        
        if self.user_config.get("target_pages"):
            sections.append(f"- 目标页数: {self.user_config['target_pages']} 页")
        
        if sections:
            return "### 用户配置\n" + "\n".join(sections)
        return ""

    def _generate_template_section(self) -> str:
        """生成模板部分"""
        t = self.theme
        
        # 根据主题类别调整模板描述
        if t.metadata.category == "creative":
            cover_desc = "渐变背景，大号标题，视觉冲击"
            section_desc = "渐变背景，动感设计"
        elif t.metadata.category == "academic":
            cover_desc = "简洁清晰，学术规范"
            section_desc = "简约设计，突出章节"
        elif t.metadata.category == "company_intro":
            cover_desc = "科技感设计，现代简约"
            section_desc = "深色背景，科技感"
        else:
            cover_desc = "极简白底，大字号，庄重专业"
            section_desc = "深色背景，大号标题"
        
        return f"""
### 类型 A: 封面页 (Cover)
**特点**：{cover_desc}

```html
<div class="slide-container cover-slide">
    <div class="cover-top">
        <div class="brand-line"></div>
        <div class="doc-type">{{{{文档类型}}}}</div>
        <h1 class="main-title">{{{{必须严格使用用户提供的文档标题}}}}</h1>
        <h2 class="sub-title">{{{{文档副标题}}}}</h2>
    </div>
    <div class="cover-middle"></div>
    <div class="cover-bottom">
        <div class="footer-row">
            <div class="footer-item">汇报单位：{{{{单位名称}}}}</div>
        </div>
        <div class="footer-row">
            <div class="footer-item">日期：{{{{YYYY年MM月}}}}</div>
        </div>
    </div>
</div>
```

### 类型 B: 目录页 (Catalog)
**特点**：清晰的大号数字，层次分明

```html
<div class="slide-container">
    <main class="content-area">
        <div class="title-box">
            <h1 class="page-title">报告核心框架</h1>
        </div>
        <div class="catalog-list">
            <div class="catalog-item">
                <div class="catalog-idx">01</div>
                <div class="catalog-content">
                    <div class="catalog-name">{{{{章节标题}}}}</div>
                    <div class="catalog-desc">{{{{一句话核心观点}}}}</div>
                </div>
            </div>
        </div>
    </main>
</div>
```

### 类型 C: 章节过场页 (Section Divider)
**特点**：{section_desc}

```html
<div class="slide-container section-slide">
    <div class="section-bg-pattern"></div>
    <div class="section-content">
        <div class="section-number">{{{{章节序号}}}}</div>
        <div class="section-line"></div>
        <h1 class="section-title">{{{{章节标题}}}}</h1>
    </div>
</div>
```

### 类型 D: 正文页 (Content)
**特点**：大字号，左对齐，信息密集

```html
<div class="slide-container">
    <main class="content-area">
        <div class="title-box">
            <h1 class="page-title">{{{{行动式标题}}}}</h1>
        </div>
        <div class="layout-box two-col">
            <div class="col">
                <div class="text-block">
                    <h3 class="sub-head">关键发现</h3>
                    <ul class="big-list">
                        <li>要点一...</li>
                        <li>要点二...</li>
                    </ul>
                </div>
            </div>
            <div class="col">
                <div class="data-card">
                    <div class="data-val">45%</div>
                    <div class="data-lbl">同比增长率</div>
                </div>
            </div>
        </div>
        <div class="bottom-box">
            <div class="bottom-text">{{{{结论句子}}}}</div>
        </div>
    </main>
    <footer class="slide-footer">
        <span>数据来源：{{{{来源}}}}</span>
    </footer>
</div>
```
"""

    def generate_page_prompt(
        self,
        page_num: int,
        total_pages: int,
        page_data: Dict[str, Any],
        source_material: str = ""
    ) -> str:
        """生成页面生成提示词"""
        t = self.theme
        
        specified_type = page_data.get('type', 'CONTENT')
        current_title = page_data.get('title', '无标题')
        current_content = page_data.get('content', '')
        
        # 页面类型指令
        page_type_instruction = self._get_page_type_instruction(
            specified_type, page_num, total_pages, current_title
        )
        
        return f"""
任务：生成第 {page_num}/{total_pages} 页 HTML 代码。
{page_type_instruction}

【输入数据 (Source of Truth)】：
标题：{current_title}
内容详情：
{current_content}

【视觉规范】：
- 主色调: {t.colors.primary}
- 强调色: {t.colors.primary_light}
- 正文字号: {t.typography.size_body}px
- 标题字号: {t.typography.size_page_title}px

【高密度信息展示策略】：
1. **电报式写作**：使用短语而非长句
   - ❌ 错误：该园区的年产值增长了50%，达到了100亿元。
   - ✅ 正确：产值100亿元（+50%）

2. **数据保留原则**：每一个具体数字都是黄金信息，绝不许删除。

3. **排版规范**：
   - 正文使用 {t.typography.size_body}px 字号
   - 绝对禁止 CSS `<style>` 标签
   - 绝对禁止页眉 `<header>`

4. **专业图表**：
   - 遇到对比数据，优先使用 ECharts
   - 图表配色使用: {t.chart.colors[:3]}
   - 图表代码必须包含 `animation: false`

【严格执行令】：
1. **忠实还原**：PPT 正文的每一条观点、每一个数据，都必须能从"内容详情"中找到依据。
2. **字号与排版**：正文 > {t.typography.size_body}px，标题 > {t.typography.size_page_title}px。
3. **禁止页眉**：绝对禁止生成 `<header>` 元素。
4. **禁止生成 CSS**：绝对禁止在输出中包含 `<style>` 标签。

输出格式：直接输出 HTML 代码块。
"""

    def _get_page_type_instruction(
        self,
        page_type: str,
        page_num: int,
        total_pages: int,
        title: str
    ) -> str:
        """获取页面类型指令"""
        t = self.theme
        
        # 获取用户配置
        org_name = self.user_config.get("organization", "汇报单位")
        doc_type = self.user_config.get("doc_type", "专项咨询研究报告")
        
        if page_type == 'COVER' or page_num == 1:
            return f"""
这是【封面页】。
1. 必须严格使用模板 A (Cover)。
2. 主标题必须**原封不动**地使用："{title}"。
3. 绝对禁止自己编造标题。
4. doc-type（文档类型）使用：{doc_type}
5. 副标题使用：汇报材料
6. 汇报单位：{org_name}
7. 日期使用当前日期
8. 移除所有英文装饰。
"""
        elif page_type == 'AGENDA':
            return "这是【目录页】。使用模板 B，列出核心章节。"
        elif page_type == 'SECTION':
            return f"""
这是【章节过场页】。
1. 必须使用模板 C (Section Divider)。
2. 使用主题配色背景。
3. 标题："{title}"
4. 绝对禁止添加任何额外的描述文本。
5. 只显示章节标题，保持极简设计。
"""
        elif page_type == 'CLOSING' or page_num == total_pages:
            return "这是【封底页】。请使用极简设计，仅保留'谢 谢 观 看'及联系方式（中文）。"
        else:
            return "这是【正文页】。使用模板 D。"


def generate_system_prompt(theme: Theme, user_config: Optional[Dict[str, Any]] = None) -> str:
    """便捷函数：生成系统提示词"""
    generator = PromptGenerator(theme, user_config)
    return generator.generate_system_prompt()


def generate_page_prompt(
    theme: Theme,
    page_num: int,
    total_pages: int,
    page_data: Dict[str, Any],
    user_config: Optional[Dict[str, Any]] = None,
    source_material: str = ""
) -> str:
    """便捷函数：生成页面提示词"""
    generator = PromptGenerator(theme, user_config)
    return generator.generate_page_prompt(page_num, total_pages, page_data, source_material)
