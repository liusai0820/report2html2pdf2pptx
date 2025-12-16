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

/* 全局列表样式重置 - 防止浏览器默认符号与自定义符号重复 */
ul, ol {{
    list-style: none;
    margin: 0;
    padding: 0;
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

/* 内容区域 - 防溢出设计 */
.content-area {{
    flex: 1;
    padding: var(--padding-v) var(--padding-h);
    display: flex;
    flex-direction: column;
    font-family: var(--font-family);
    overflow: hidden; /* 防溢出最后防线 */
    max-height: calc(var(--slide-height) - 50px); /* 扣除页脚高度 */
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
        """根据主题分类生成封面样式"""
        cat = self.theme.metadata.category
        # 特殊处理 annual_review，因为它之前混在 consulting 里
        if self.theme.metadata.id == 'annual_review':
            return self._generate_cover_styles_annual()
            
        if cat == 'creative':
            return self._generate_cover_styles_creative()
        elif cat == 'academic':
            return self._generate_cover_styles_academic()
        elif cat == 'government':
            return self._generate_cover_styles_government()
        elif cat == 'company_intro':
            return self._generate_cover_styles_tech()
        else:
            return self._generate_cover_styles_default()

    def _generate_cover_styles_default(self) -> str:
        """默认/咨询风格封面 (极简商务之巅 - 回归本质)"""
        return f"""
/* ============================================
   封面页样式 (Consulting - Ultimate Minimalist)
   ============================================ */

.cover-slide {{
    display: flex;
    flex-direction: column;
    padding: 80px 100px;
    position: relative;
    background: #ffffff; /* 纯白背景，模拟纸张 */
    color: #1a1a1a;
}}

/* 只有一条极简的品牌色装饰线，位于左上角 */
.cover-slide::before {{
    content: "";
    position: absolute;
    top: 80px; left: 100px;
    width: 80px; height: 8px;
    background: var(--primary);
}}

/* 顶部区域：文档类型 */
.cover-top {{
    margin-top: 40px; /* 在装饰线下方 */
    margin-bottom: 60px;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}}

.brand-line {{ display: none; }}

.doc-type {{
    font-size: 18px;
    color: var(--text-secondary);
    font-weight: 500;
    letter-spacing: 1px;
    margin-bottom: 0;
}}

/* 隐藏其他花哨装饰 */
.cover-top::after {{ display: none; }}

/* 核心标题区 - 视觉重心 */
.main-title {{
    font-size: 64px; /* 巨大 */
    line-height: 1.2;
    color: #000000;
    font-weight: 700; /* 粗体，有力 */
    font-family: var(--font-family-heading);
    margin-bottom: 40px;
    max-width: 900px;
    letter-spacing: -1px;
}}

.sub-title {{
    font-size: 28px;
    color: #555555;
    font-weight: 400;
    line-height: 1.5;
    max-width: 800px;
}}

.cover-middle {{ display: none; }}

.cover-bottom {{
    margin-top: auto;
    width: 100%;
    border-top: 1px solid #eeeeee; /* 极细的分割线 */
    padding-top: 20px;
}}

.footer-row {{
    display: flex;
    flex-direction: column;
    gap: 8px;
}}

.footer-item {{
    font-size: 14px;
    color: #888888;
    font-family: var(--font-family);
}}
"""

    def _generate_cover_styles_annual(self) -> str:
        """年终述职风格 (清爽亮色 + 年份大字)"""
        # 动态获取当前年份
        from datetime import datetime
        current_year = datetime.now().strftime("%Y")
        
        return f"""
/* ============================================
   封面页样式 (Annual Review - Bright & Clean)
   ============================================ */
.cover-slide {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 80px 100px;
    position: relative;
    /* 清爽的蓝白渐变背景 */
    background: linear-gradient(120deg, #ffffff 0%, #f0f7ff 100%);
    color: #1e293b;
    overflow: hidden;
}}

/* 左侧装饰线 */
.cover-slide::before {{
    content: "";
    position: absolute;
    top: 0; bottom: 0; left: 0;
    width: 15px;
    background: var(--primary);
}}

/* 动态年份水印 */
.cover-slide::after {{
    content: "{current_year}";
    position: absolute;
    right: 20px;
    bottom: -60px;
    font-size: 280px;
    font-weight: 900;
    color: var(--primary);
    opacity: 0.06;
    z-index: 0;
    font-family: var(--font-family-heading);
    letter-spacing: -10px;
}}

.cover-top {{
    position: relative;
    z-index: 2;
    margin-bottom: 40px;
}}

.doc-type {{
    display: inline-block;
    font-size: 16px;
    color: white;
    background: var(--primary); /* 醒目的标签 */
    padding: 6px 16px;
    letter-spacing: 2px;
    font-weight: bold;
    text-transform: uppercase;
    margin-bottom: 30px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}}

.brand-line {{ display: none; }}

.main-title {{
    position: relative;
    z-index: 2;
    font-size: 72px;
    line-height: 1.1;
    font-weight: 800;
    margin-bottom: 20px;
    color: #0f172a;
    letter-spacing: -1px;
}}

.sub-title {{
    position: relative;
    z-index: 2;
    font-size: 32px;
    color: #64748b;
    font-weight: 300;
}}

.cover-bottom {{
    position: relative;
    z-index: 2;
    margin-top: 80px;
    display: flex;
    gap: 40px;
    align-items: center;
}}

.footer-item {{
    font-size: 16px;
    color: #475569;
    font-weight: 500;
    background: white;
    padding: 10px 20px;
    border: 1px solid #e2e8f0;
    border-radius: 30px;
}}
"""

    def _generate_cover_styles_creative(self) -> str:
        """创意/营销风格封面 - 缤纷渐变版"""
        return f"""
/* ============================================
   封面页样式 (Creative - Vibrant)
   ============================================ */

.cover-slide {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 80px;
    position: relative;
    overflow: hidden;
    /* 缤纷渐变背景 */
    background: linear-gradient(135deg, #6C5CE7 0%, #A29BFE 50%, #FD79A8 100%);
    color: white;
}}

/* 装饰背景：白色半透明圆 */
.cover-slide::before {{
    content: "";
    position: absolute;
    top: -100px; right: -100px;
    width: 600px; height: 600px;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    border-radius: 50%;
    z-index: 0;
}}

.cover-slide::after {{
    content: "";
    position: absolute;
    bottom: -50px; left: -50px;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
    border-radius: 50%;
    z-index: 0;
}}

.cover-top {{
    position: relative;
    z-index: 10;
}}

.cover-top .doc-type, 
.cover-top .brand-line {{
    display: none;
}}

.main-title {{
    font-size: 80px;
    line-height: 1;
    color: white; /* 纯白 */
    margin-bottom: 20px;
    font-weight: 900;
    text-transform: uppercase;
    text-shadow: 0 4px 20px rgba(0,0,0,0.2);
}}

.sub-title {{
    font-size: 32px;
    color: var(--primary); /* 反色：用深色字配浅色块 */
    font-weight: bold;
    background: white; /* 白底 */
    display: inline-block;
    padding: 8px 24px;
    transform: rotate(-1deg);
    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    border-radius: 4px;
}}

.cover-bottom {{
    position: relative;
    z-index: 10;
    margin-top: 60px;
}}

.footer-item {{
    font-size: 16px;
    color: rgba(255,255,255,0.8);
    font-weight: 600;
}}
"""

    def _generate_cover_styles_academic(self) -> str:
        """学术/论文风格封面"""
        return f"""
/* ============================================
   封面页样式 (Academic)
   ============================================ */
.cover-slide {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 60px;
    position: relative;
    background: white;
    text-align: center;
}}

.cover-slide::after {{
    content: "";
    position: absolute;
    top: 20px; left: 20px; right: 20px; bottom: 20px;
    border: 4px double var(--primary);
    pointer-events: none;
}}

.cover-top {{ margin-bottom: 40px; }}

.doc-type {{
    font-size: 20px;
    color: var(--text-secondary);
    font-weight: normal;
    font-family: serif;
    letter-spacing: 4px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 10px;
    display: inline-block;
}}

.main-title {{
    font-size: 48px;
    line-height: 1.4;
    color: var(--primary-dark);
    margin-bottom: 30px;
    font-weight: 700;
    font-family: serif;
    max-width: 80%;
    margin-left: auto;
    margin-right: auto;
}}

.sub-title {{
    font-size: 24px;
    color: var(--text-secondary);
    font-weight: normal;
    font-family: serif;
}}

.cover-bottom {{
    margin-top: 60px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}}

.footer-item {{
    font-size: 18px;
    color: var(--text-primary);
    font-family: serif;
}}
"""

    def _generate_cover_styles_government(self) -> str:
        """政府/公文风格"""
        return f"""
/* ============================================
   封面页样式 (Government)
   ============================================ */
.cover-slide {{
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 100px;
    position: relative;
    background: #fff;
    text-align: center;
}}

.cover-slide::before {{
    content: "";
    position: absolute;
    top: 80px; left: 0; right: 0;
    height: 3px;
    background: #DD2C00;
    margin: 0 60px;
}}

.cover-slide::after {{
    content: "";
    position: absolute;
    bottom: 60px; left: 0; right: 0;
    height: 1px;
    background: #DD2C00;
    margin: 0 60px;
    opacity: 0.5;
}}

.cover-top {{
    margin-top: 60px;
    width: 100%;
    border-bottom: 1px solid #DD2C00;
    padding-bottom: 40px;
    margin-bottom: 60px;
}}

.brand-line {{ display: none; }}

.doc-type {{
    font-size: 36px;
    color: #DD2C00;
    font-family: serif;
    font-weight: 900;
    letter-spacing: 8px;
}}

.main-title {{
    font-size: 52px;
    line-height: 1.4;
    color: #000;
    font-family: sans-serif;
    margin-bottom: 40px;
}}

.sub-title {{
    font-size: 26px;
    color: #333;
    font-family: serif;
}}

.cover-bottom {{
    margin-top: auto;
    width: 100%;
    text-align: right;
    padding-right: 20px;
}}

.footer-item {{
    font-size: 20px;
    color: #000;
    font-family: serif;
    margin-bottom: 12px;
}}
"""

    def _generate_cover_styles_tech(self) -> str:
        """科技/公司介绍风格 - 浅色科技风"""
        return f"""
/* ============================================
   封面页样式 (Tech/Company - Light Mode)
   ============================================ */

.cover-slide {{
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 80px;
    position: relative;
    background: #f8fafc; /* 科技灰白 */
    color: #0f172a; /* 深蓝字 */
}}

/* 浅色网格背景 */
.cover-slide::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: 
        linear-gradient(rgba(148, 163, 184, 0.1) 1px, transparent 1px),
        linear-gradient(90deg, rgba(148, 163, 184, 0.1) 1px, transparent 1px);
    background-size: 30px 30px;
}}

.cover-top {{ margin-bottom: 20px; position: relative; z-index: 1; }}

.doc-type {{
    display: inline-block;
    padding: 6px 12px;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 4px;
    font-size: 14px;
    color: var(--primary);
    letter-spacing: 1px;
    width: fit-content;
    font-family: var(--font-family-mono);
}}

.main-title {{
    position: relative;
    z-index: 1;
    font-size: 64px;
    line-height: 1.1;
    margin-top: 20px;
    margin-bottom: 30px;
    font-weight: bold;
    font-family: var(--font-family-heading);
    /* 渐变但保持高可读性 */
    background: linear-gradient(135deg, #0f172a 0%, #334155 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}}

.sub-title {{
    position: relative;
    z-index: 1;
    font-size: 24px;
    color: #64748b;
    font-weight: 300;
}}

.cover-bottom {{
    margin-top: 80px;
    border-top: 2px solid #e2e8f0;
    padding-top: 20px;
    position: relative;
    z-index: 1;
}}

.footer-item {{
    font-size: 14px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
}}
"""

    def _generate_section_styles(self) -> str:
        """根据主题分类生成章节页样式"""
        cat = self.theme.metadata.category
        # 特殊处理年终总结
        if self.theme.metadata.id == 'annual_review':
            return self._generate_section_styles_annual()
        if cat == 'creative':
            return self._generate_section_styles_creative()
        elif cat == 'academic':
            return self._generate_section_styles_academic()
        elif cat == 'government':
            return self._generate_section_styles_government()
        elif cat == 'company_intro':
            return self._generate_section_styles_tech()
        else:
            return self._generate_section_styles_default()

    def _generate_section_styles_default(self) -> str:
        """默认/咨询风格章节页 - 极简白色版，与封面风格一致"""
        return f"""
/* ============================================
   章节过场页样式 (Default - Minimalist)
   ============================================ */

.section-slide {{
    background: #ffffff;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 80px;
    color: var(--text-primary);
    position: relative;
    overflow: hidden;
}}

/* 左侧品牌色块装饰 */
.section-slide::before {{
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 8px;
    background: var(--primary);
}}

.section-bg-pattern {{
    display: none; /* 极简风格不需要背景图案 */
}}

.section-content {{
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    max-width: 800px;
}}

.section-number {{
    font-size: 100px;
    font-weight: var(--weight-bold);
    color: var(--primary-light);
    opacity: 0.3;
    line-height: 0.9;
    margin-bottom: 10px;
    font-family: var(--font-family-heading);
}}

.section-line {{
    width: 60px;
    height: 4px;
    background: var(--primary);
    margin-bottom: 30px;
}}

.section-title {{
    font-size: var(--size-section-title);
    font-weight: var(--weight-bold);
    color: var(--text-primary);
    margin-bottom: 20px;
    line-height: var(--line-height-heading);
    font-family: var(--font-family-heading);
}}

.section-desc {{
    font-size: var(--size-body);
    color: var(--text-secondary);
    line-height: var(--line-height-body);
    font-family: var(--font-family);
}}
"""

    def _generate_section_styles_annual(self) -> str:
        """年终述职风格章节页 - 与封面协调的深蓝渐变"""
        return f"""
/* ============================================
   章节过场页样式 (Annual Review)
   ============================================ */

.section-slide {{
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 80px;
    color: #ffffff;
    position: relative;
    overflow: hidden;
}}

.section-bg-pattern {{
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    opacity: 0.05;
    background-image: radial-gradient(#fff 1px, transparent 1px);
    background-size: 30px 30px;
}}

.section-content {{
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}}

.section-number {{
    font-size: 120px;
    font-weight: var(--weight-bold);
    color: rgba(255,255,255,0.2);
    line-height: 0.8;
    margin-bottom: 20px;
    font-family: var(--font-family-heading);
}}

.section-line {{
    width: 80px;
    height: 4px;
    background: var(--accent);
    margin: 0 auto 30px auto;
}}

.section-title {{
    font-size: var(--size-section-title);
    font-weight: var(--weight-bold);
    color: #ffffff;
    margin-bottom: 20px;
    line-height: var(--line-height-heading);
    font-family: var(--font-family-heading);
}}

.section-desc {{
    font-size: var(--size-body);
    color: rgba(255,255,255,0.8);
    line-height: var(--line-height-body);
    font-family: var(--font-family);
}}
"""

    def _generate_section_styles_creative(self) -> str:
        """创意风格章节页 - 缤纷渐变版"""
        return f"""
/* ============================================
   章节过场页样式 (Creative - Vibrant)
   ============================================ */

.section-slide {{
    /* 统一使用缤纷渐变背景 */
    background: linear-gradient(135deg, #6C5CE7 0%, #A29BFE 50%, #FD79A8 100%);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 60px;
    position: relative;
    overflow: hidden;
    text-align: center;
    color: white;
}}

/* 背景装饰：白色光晕圆 */
.section-slide::before {{
    content: "";
    position: absolute;
    top: -100px; left: -50px;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
    border-radius: 50%;
    z-index: 0;
}}

.section-slide::after {{
    content: "";
    position: absolute;
    bottom: -50px; right: -50px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
    border-radius: 50%;
    z-index: 0;
}}

/* 章节序号 */
.section-number {{
    font-size: 180px;
    line-height: 1;
    font-weight: 900;
    color: rgba(255,255,255,0.15); /* 白色透明 */
    font-family: var(--font-family-heading);
    margin-bottom: -40px;
    position: relative;
    z-index: 0;
}}

.section-content {{
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    max-width: 800px;
}}

/* 标题 - 纯白大字，带投影 */
.section-title {{
    font-size: 64px;
    font-weight: 900;
    color: #ffffff;
    margin-bottom: 30px;
    line-height: 1.1;
    text-transform: uppercase;
    text-shadow: 0 4px 20px rgba(0,0,0,0.2); /* 提升文字辨识度 */
    background: none; /* 移除任何可能造成黑条的背景 */
    display: block;
}}

.section-desc {{
    font-size: 24px;
    color: rgba(255,255,255,0.9);
    font-weight: 500;
    margin-top: 10px;
    max-width: 600px;
}}

.section-line {{ display: none; }}
"""

    def _generate_section_styles_tech(self) -> str:
        """科技风格章节页 - 网格与未来感"""
        return f"""
/* ============================================
   章节过场页样式 (Tech)
   ============================================ */

.section-slide {{
    background: #0f172a;
    display: flex;
    flex-direction: row;
    align-items: center;
    padding: 100px;
    position: relative;
    overflow: hidden;
    color: white;
}}

/* 科技网格背景 */
.section-slide::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: 
        linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
    background-size: 50px 50px;
}}

.section-number {{
    font-size: 80px;
    font-family: var(--font-family-mono);
    color: var(--primary-light);
    border: 1px solid var(--primary-light);
    padding: 10px 30px;
    margin-right: 60px;
    background: rgba(0,0,0,0.3);
    border-radius: 4px;
}}

.section-content {{
    flex: 1;
    position: relative;
    z-index: 1;
}}

.section-title {{
    font-size: 48px;
    font-weight: bold;
    color: white;
    margin-bottom: 20px;
    letter-spacing: 1px;
}}

.section-line {{
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, var(--accent) 0%, transparent 100%);
    margin-bottom: 20px;
}}

.section-desc {{
    font-size: 18px;
    color: #94a3b8;
    font-family: var(--font-family-mono);
}}
"""

    def _generate_section_styles_government(self) -> str:
        """政府风格章节页 - 纯红极简"""
        return f"""
/* ============================================
   章节过场页样式 (Government)
   ============================================ */

.section-slide {{
    background: #DD2C00; /* 全红背景 */
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 100px;
    color: white;
    text-align: center;
}}

.section-border {{
    position: absolute;
    top: 20px; left: 20px; right: 20px; bottom: 20px;
    border: 2px solid rgba(255,255,255,0.3);
    pointer-events: none;
}}

.section-number {{
    font-size: 60px;
    font-family: "PingFang SC", serif;
    color: rgba(255,255,255,0.9);
    margin-bottom: 30px;
    border-bottom: 1px solid rgba(255,255,255,0.5);
    padding-bottom: 10px;
    display: inline-block;
}}

.section-title {{
    font-size: 56px;
    font-family: "SimHei", sans-serif;
    margin-bottom: 30px;
    font-weight: normal;
    letter-spacing: 2px;
}}

.section-desc {{
    font-size: 24px;
    font-family: "KaiTi", serif;
    opacity: 0.9;
}}

.section-line {{ display: none; }}
"""

    def _generate_section_styles_academic(self) -> str:
        """学术风格章节页 - 极简白底黑字"""
        return f"""
/* ============================================
   章节过场页样式 (Academic)
   ============================================ */

.section-slide {{
    background: white;
    display: flex;
    flex-direction: row;
    align-items: center;
    padding: 80px 120px;
    color: var(--text-primary);
    position: relative;
}}

/* 左侧色条装饰 */
.section-slide::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; bottom: 0; width: 40px;
    background: var(--primary);
}}

.section-number {{
    font-size: 100px;
    font-weight: bold;
    color: var(--primary-light);
    opacity: 0.2;
    margin-right: 40px;
    font-family: serif;
}}

.section-content {{
    flex: 1;
    border-left: 1px solid var(--border);
    padding-left: 40px;
}}

.section-title {{
    font-size: 42px;
    margin-bottom: 15px;
    font-family: serif;
    color: var(--primary-dark);
}}

.section-desc {{
    font-size: 20px;
    color: var(--text-secondary);
    font-style: italic;
}}

.section-line {{ display: none; }}
"""

    def _generate_content_styles(self) -> str:
        """生成正文页样式"""
        return f"""
/* ============================================
   正文页样式
   ============================================ */

/* 布局容器 - 防溢出 */
.layout-box {{
    flex: 1;
    display: flex;
    gap: var(--gap-large);
    overflow: hidden; /* 裁剪溢出内容 */
    min-height: 0; /* 允许flex收缩 */
}}

.two-col > .col {{
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0; /* 允许收缩 */
    overflow: hidden;
}}

.three-col > .col {{
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0;
    overflow: hidden;
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
    padding: 20px 25px;
    border-top: 4px solid var(--primary-light);
    border-radius: var(--border-radius);
    flex-shrink: 0;
}}

.data-val {{
    font-size: 48px;
    color: var(--primary);
    font-weight: var(--weight-bold);
    margin-bottom: 8px;
    font-family: var(--font-family-heading);
    line-height: 1;
}}

.data-lbl {{
    font-size: var(--size-small);
    color: var(--text-secondary);
    font-family: var(--font-family);
}}

/* 底部结论框 */
.bottom-box {{
    margin-top: auto;
    background: var(--background-alt);
    padding: 20px 25px;
    border-left: 8px solid var(--primary);
    border-radius: var(--border-radius);
    flex-shrink: 0;
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
    max-height: 350px; /* 限制最大高度，防溢出 */
    min-height: 200px;
    position: relative;
    background: #fff;
    border-radius: 8px;
    padding: 10px;
    flex-shrink: 0;
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
