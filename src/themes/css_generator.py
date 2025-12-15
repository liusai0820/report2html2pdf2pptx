"""
CSS 生成器 - 根据主题配置生成完整的 CSS 样式表

功能:
1. 生成 CSS 变量
2. 生成基础样式
3. 生成页面类型特定样式
4. 支持用户自定义覆盖
"""

from typing import Dict, Any, Optional
from .theme_manager import Theme


class CSSGenerator:
    """CSS 样式生成器"""
    
    def __init__(self, theme: Theme):
        self.theme = theme
    
    def generate_full_css(self) -> str:
        """生成完整的 CSS 样式表"""
        parts = [
            self._generate_css_variables(),
            self._generate_base_styles(),
            self._generate_cover_styles(),
            self._generate_section_styles(),
            self._generate_content_styles(),
            self._generate_catalog_styles(),
            self._generate_closing_styles(),
            self._generate_component_styles(),
            self._generate_chart_styles(),
            self._generate_print_styles(),
            self.theme.custom_css,
        ]
        return "\n".join(parts)
    
    def _generate_css_variables(self) -> str:
        """生成 CSS 变量"""
        return self.theme.generate_css_variables()
    
    def _generate_base_styles(self) -> str:
        """生成基础样式"""
        t = self.theme
        return f"""
/* ============================================
   基础样式 - {t.metadata.name}
   ============================================ */

* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}}

html, body {{
    font-family: var(--font-family);
    font-size: var(--size-body);
    line-height: var(--line-height-body);
    color: var(--text-primary);
    background: var(--background);
}}

.slide-container {{
    width: var(--slide-width);
    height: var(--slide-height);
    background: var(--background);
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    font-family: var(--font-family);
    page-break-after: always;
}}

/* 通用页脚 */
.slide-footer {{
    height: 50px;
    padding: 0 var(--padding-h);
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: var(--size-footer);
    color: var(--text-light);
    font-family: var(--font-family);
}}

/* 内容区域 */
.content-area {{
    flex: 1;
    padding: var(--padding-v) var(--padding-h);
    display: flex;
    flex-direction: column;
    font-family: var(--font-family);
}}

/* 标题区域 */
.title-box {{
    margin-bottom: var(--gap-medium);
}}

.page-title {{
    font-size: var(--size-page-title);
    color: var(--primary);
    line-height: var(--line-height-heading);
    font-weight: var(--weight-bold);
    font-family: var(--font-family-heading);
}}
"""

    def _generate_cover_styles(self) -> str:
        """生成封面样式"""
        return f"""
/* ============================================
   封面页样式
   ============================================ */

.cover-slide {{
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 60px 80px;
    position: relative;
}}

.cover-top {{
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
}}

.cover-middle {{
    flex: 1;
}}

.cover-bottom {{
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    gap: var(--gap-small);
}}

.brand-line {{
    width: 100px;
    height: 8px;
    background: var(--primary);
    margin-bottom: 40px;
    flex-shrink: 0;
}}

.doc-type {{
    font-size: var(--size-body);
    color: var(--text-secondary);
    margin-bottom: 30px;
    letter-spacing: 2px;
    font-family: var(--font-family);
    font-weight: var(--weight-normal);
}}

.main-title {{
    font-size: var(--size-cover-title);
    line-height: var(--line-height-heading);
    color: var(--text-primary);
    margin-bottom: 20px;
    font-weight: var(--weight-bold);
    font-family: var(--font-family-heading);
    word-wrap: break-word;
    overflow-wrap: break-word;
}}

.sub-title {{
    font-size: 28px;
    color: var(--text-secondary);
    font-weight: var(--weight-normal);
    font-family: var(--font-family);
}}

.footer-row {{
    display: flex;
    align-items: center;
}}

.footer-item {{
    font-size: 18px;
    color: var(--text-secondary);
    font-family: var(--font-family);
    line-height: 1.5;
}}
"""

    def _generate_section_styles(self) -> str:
        """生成章节过场页样式"""
        return f"""
/* ============================================
   章节过场页样式
   ============================================ */

.section-slide {{
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 80px;
    color: #fff;
    position: relative;
}}

.section-bg-pattern {{
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    opacity: 0.05;
    background-image: repeating-linear-gradient(
        45deg,
        transparent,
        transparent 35px,
        rgba(255,255,255,.1) 35px,
        rgba(255,255,255,.1) 70px
    );
}}

.section-content {{
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}}

.section-number {{
    font-size: 120px;
    font-weight: var(--weight-bold);
    color: rgba(255,255,255,0.15);
    line-height: 1;
    margin-bottom: 20px;
    font-family: var(--font-family-heading);
}}

.section-line {{
    width: 80px;
    height: 6px;
    background: var(--accent);
    margin-bottom: 30px;
}}

.section-title {{
    font-size: var(--size-section-title);
    font-weight: var(--weight-bold);
    margin-bottom: 20px;
    line-height: var(--line-height-heading);
    font-family: var(--font-family-heading);
}}

.section-desc {{
    font-size: var(--size-body);
    color: rgba(255,255,255,0.7);
    max-width: 800px;
    line-height: var(--line-height-body);
    font-family: var(--font-family);
}}
"""

    def _generate_content_styles(self) -> str:
        """生成正文页样式"""
        return f"""
/* ============================================
   正文页样式
   ============================================ */

/* 布局 */
.layout-box {{
    flex: 1;
    display: flex;
    gap: var(--gap-large);
}}

.two-col > .col {{
    flex: 1;
    display: flex;
    flex-direction: column;
}}

.three-col > .col {{
    flex: 1;
    display: flex;
    flex-direction: column;
}}

/* 子标题 */
.sub-head {{
    font-size: var(--size-heading);
    color: var(--primary);
    margin-bottom: 20px;
    border-left: 6px solid var(--primary-light);
    padding-left: 15px;
    line-height: 1;
    font-family: var(--font-family-heading);
    font-weight: var(--weight-bold);
}}

/* 列表 */
.big-list {{
    list-style: none;
}}

.big-list li {{
    font-size: var(--size-body);
    color: var(--text-primary);
    line-height: var(--line-height-body);
    margin-bottom: 20px;
    position: relative;
    padding-left: 30px;
    font-family: var(--font-family);
}}

.big-list li::before {{
    content: "";
    position: absolute;
    left: 0;
    top: 10px;
    width: 10px;
    height: 10px;
    background: var(--primary-light);
    border-radius: 2px;
}}

/* 数据卡片 */
.data-card {{
    background: var(--background-alt);
    padding: 30px;
    border-top: 4px solid var(--primary-light);
    border-radius: var(--border-radius);
}}

.data-val {{
    font-size: 56px;
    color: var(--primary);
    font-weight: var(--weight-bold);
    margin-bottom: 10px;
    font-family: var(--font-family-heading);
}}

.data-lbl {{
    font-size: var(--size-body);
    color: var(--text-secondary);
    font-family: var(--font-family);
}}

/* 底部结论框 */
.bottom-box {{
    margin-top: auto;
    background: var(--background-alt);
    padding: 30px;
    border-left: 8px solid var(--primary);
    border-radius: var(--border-radius);
}}

.bottom-text {{
    font-size: 22px;
    color: var(--primary);
    font-weight: var(--weight-bold);
    line-height: 1.5;
    font-family: var(--font-family);
}}

/* 文本块 */
.text-block {{
    margin-bottom: var(--gap-medium);
}}

/* 引用块 */
.quote-block {{
    border-left: 4px solid var(--primary-light);
    padding-left: 20px;
    font-style: italic;
    color: var(--text-secondary);
}}
"""

    def _generate_catalog_styles(self) -> str:
        """生成目录页样式"""
        return f"""
/* ============================================
   目录页样式
   ============================================ */

.catalog-list {{
    display: flex;
    flex-direction: column;
    gap: var(--gap-medium);
}}

.catalog-item {{
    display: flex;
    align-items: flex-start;
    gap: 30px;
    padding: 20px 0;
    border-bottom: 1px solid var(--border);
}}

.catalog-item:last-child {{
    border-bottom: none;
}}

.catalog-idx {{
    font-size: 48px;
    font-weight: var(--weight-bold);
    color: var(--primary-light);
    opacity: 0.3;
    line-height: 1;
    min-width: 80px;
    font-family: var(--font-family-heading);
}}

.catalog-content {{
    flex: 1;
}}

.catalog-name {{
    font-size: var(--size-heading);
    color: var(--primary);
    font-weight: var(--weight-bold);
    margin-bottom: 8px;
    font-family: var(--font-family-heading);
}}

.catalog-desc {{
    font-size: var(--size-body);
    color: var(--text-secondary);
    font-family: var(--font-family);
}}
"""

    def _generate_closing_styles(self) -> str:
        """生成封底页样式"""
        return f"""
/* ============================================
   封底页样式
   ============================================ */

.closing-slide {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 80px;
    background: var(--background);
}}

.closing-title {{
    font-size: 56px;
    color: var(--primary);
    font-weight: var(--weight-bold);
    margin-bottom: 40px;
    letter-spacing: 20px;
    font-family: var(--font-family-heading);
}}

.closing-contact {{
    font-size: var(--size-body);
    color: var(--text-secondary);
    line-height: 2;
    font-family: var(--font-family);
}}
"""

    def _generate_component_styles(self) -> str:
        """生成组件样式"""
        return f"""
/* ============================================
   通用组件样式
   ============================================ */

/* 表格 */
.clean-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 18px;
    font-family: var(--font-family);
}}

.clean-table th {{
    text-align: left;
    padding: 15px;
    background: var(--background-alt);
    color: var(--primary);
    border-bottom: 2px solid var(--primary);
    font-family: var(--font-family);
    font-weight: var(--weight-bold);
}}

.clean-table td {{
    padding: 15px;
    border-bottom: 1px solid var(--border);
    color: var(--text-primary);
    font-family: var(--font-family);
}}

.clean-table tr:hover td {{
    background: var(--background-alt);
}}

/* 指标堆叠 */
.metric-stack {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: var(--gap-medium);
}}

.metric-item {{
    text-align: center;
    padding: 20px;
    background: var(--background-alt);
    border-radius: var(--border-radius);
}}

.metric-value {{
    font-size: 36px;
    font-weight: var(--weight-bold);
    color: var(--primary);
    margin-bottom: 8px;
}}

.metric-label {{
    font-size: var(--size-small);
    color: var(--text-secondary);
}}

/* 高亮框 */
.highlight-box {{
    background: linear-gradient(135deg, var(--primary-light) 0%, var(--primary) 100%);
    color: white;
    padding: 20px 30px;
    border-radius: var(--border-radius);
    font-weight: var(--weight-bold);
}}

/* 标签 */
.tag {{
    display: inline-block;
    padding: 4px 12px;
    background: var(--background-alt);
    color: var(--primary);
    border-radius: 20px;
    font-size: var(--size-small);
    margin-right: 8px;
    margin-bottom: 8px;
}}

/* 进度条 */
.progress-bar {{
    height: 8px;
    background: var(--background-alt);
    border-radius: 4px;
    overflow: hidden;
}}

.progress-fill {{
    height: 100%;
    background: linear-gradient(90deg, var(--primary-light) 0%, var(--primary) 100%);
    border-radius: 4px;
}}

/* 时间线 */
.timeline {{
    position: relative;
    padding-left: 30px;
}}

.timeline::before {{
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 2px;
    background: var(--border);
}}

.timeline-item {{
    position: relative;
    margin-bottom: 30px;
}}

.timeline-item::before {{
    content: "";
    position: absolute;
    left: -34px;
    top: 5px;
    width: 10px;
    height: 10px;
    background: var(--primary-light);
    border-radius: 50%;
}}

.timeline-date {{
    font-size: var(--size-small);
    color: var(--text-light);
    margin-bottom: 5px;
}}

.timeline-content {{
    font-size: var(--size-body);
    color: var(--text-primary);
}}
"""

    def _generate_chart_styles(self) -> str:
        """生成图表样式"""
        return f"""
/* ============================================
   图表样式
   ============================================ */

.chart-container {{
    width: 100%;
    min-height: 400px;
    position: relative;
    background: #fff;
    border-radius: 8px;
    padding: 10px;
}}

.chart-container > div {{
    width: 100% !important;
    height: 100% !important;
}}

.chart-title {{
    font-size: var(--size-heading);
    color: var(--primary);
    text-align: center;
    margin-bottom: var(--gap-small);
    font-weight: var(--weight-bold);
}}

.chart-subtitle {{
    font-size: var(--size-small);
    color: var(--text-secondary);
    text-align: center;
    margin-bottom: var(--gap-medium);
}}
"""

    def _generate_print_styles(self) -> str:
        """生成打印样式"""
        return """
/* ============================================
   打印优化
   ============================================ */

@media print {
    .slide-container {
        break-inside: avoid;
        page-break-after: always;
    }
    
    .section-slide {
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    
    .data-card,
    .bottom-box,
    .highlight-box {
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
}

@page {
    size: 1280px 720px;
    margin: 0;
}
"""


def generate_theme_css(theme: Theme) -> str:
    """便捷函数：生成主题 CSS"""
    generator = CSSGenerator(theme)
    return generator.generate_full_css()


def generate_theme_css_with_overrides(
    theme: Theme,
    color_overrides: Optional[Dict[str, str]] = None,
    typography_overrides: Optional[Dict[str, Any]] = None
) -> str:
    """生成带覆盖配置的主题 CSS"""
    import copy
    
    # 深拷贝主题
    custom_theme = copy.deepcopy(theme)
    
    # 应用颜色覆盖
    if color_overrides:
        for key, value in color_overrides.items():
            if hasattr(custom_theme.colors, key):
                setattr(custom_theme.colors, key, value)
    
    # 应用字体覆盖
    if typography_overrides:
        for key, value in typography_overrides.items():
            if hasattr(custom_theme.typography, key):
                setattr(custom_theme.typography, key, value)
    
    generator = CSSGenerator(custom_theme)
    return generator.generate_full_css()
