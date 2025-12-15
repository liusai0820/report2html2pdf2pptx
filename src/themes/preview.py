"""
主题预览生成器 - 生成主题预览 HTML

功能:
1. 生成主题预览页面
2. 展示所有页面类型
3. 支持颜色对比
"""

from pathlib import Path
from typing import Optional
from .theme_manager import Theme
from .css_generator import generate_theme_css


def generate_theme_preview(theme: Theme, output_path: Optional[str] = None) -> str:
    """生成主题预览 HTML"""
    
    css = generate_theme_css(theme)
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>主题预览 - {theme.metadata.name}</title>
    <style>
{css}

/* 预览页面样式 */
body {{
    background: #f0f0f0;
    padding: 40px;
}}

.preview-container {{
    max-width: 1400px;
    margin: 0 auto;
}}

.preview-header {{
    text-align: center;
    margin-bottom: 40px;
    padding: 30px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}}

.preview-header h1 {{
    font-size: 32px;
    color: var(--primary);
    margin-bottom: 10px;
}}

.preview-header p {{
    color: var(--text-secondary);
    font-size: 16px;
}}

.color-palette {{
    display: flex;
    gap: 10px;
    justify-content: center;
    margin-top: 20px;
    flex-wrap: wrap;
}}

.color-swatch {{
    width: 60px;
    height: 60px;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    padding-bottom: 5px;
    font-size: 10px;
    color: white;
    text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}}

.slide-preview {{
    margin-bottom: 40px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    border-radius: 8px;
    overflow: hidden;
}}

.slide-label {{
    background: var(--primary);
    color: white;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: bold;
}}
    </style>
</head>
<body>
    <div class="preview-container">
        <!-- 预览头部 -->
        <div class="preview-header">
            <h1>{theme.metadata.name}</h1>
            <p>{theme.metadata.description}</p>
            <p><strong>分类:</strong> {theme.metadata.category} | <strong>标签:</strong> {', '.join(theme.metadata.tags)}</p>
            
            <!-- 配色展示 -->
            <div class="color-palette">
                <div class="color-swatch" style="background: {theme.colors.primary};">Primary</div>
                <div class="color-swatch" style="background: {theme.colors.primary_light};">Light</div>
                <div class="color-swatch" style="background: {theme.colors.accent};">Accent</div>
                <div class="color-swatch" style="background: {theme.colors.text_primary};">Text</div>
                <div class="color-swatch" style="background: {theme.colors.background_alt}; color: #333;">BG Alt</div>
            </div>
        </div>
        
        <!-- 封面页预览 -->
        <div class="slide-preview">
            <div class="slide-label">封面页 (Cover)</div>
            <div class="slide-container cover-slide">
                <div class="cover-top">
                    <div class="brand-line"></div>
                    <div class="doc-type">专项咨询研究报告</div>
                    <h1 class="main-title">演示文稿标题示例</h1>
                    <h2 class="sub-title">汇报材料</h2>
                </div>
                <div class="cover-middle"></div>
                <div class="cover-bottom">
                    <div class="footer-row">
                        <div class="footer-item">汇报单位：示例单位名称</div>
                    </div>
                    <div class="footer-row">
                        <div class="footer-item">日期：2024年12月</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 章节页预览 -->
        <div class="slide-preview">
            <div class="slide-label">章节过场页 (Section)</div>
            <div class="slide-container section-slide">
                <div class="section-bg-pattern"></div>
                <div class="section-content">
                    <div class="section-number">01</div>
                    <div class="section-line"></div>
                    <h1 class="section-title">第一部分 研究背景</h1>
                    <div class="section-desc">本章节将介绍项目的研究背景和核心问题</div>
                </div>
            </div>
        </div>
        
        <!-- 正文页预览 -->
        <div class="slide-preview">
            <div class="slide-label">正文页 (Content)</div>
            <div class="slide-container">
                <main class="content-area">
                    <div class="title-box">
                        <h1 class="page-title">核心发现与数据分析</h1>
                    </div>
                    <div class="layout-box two-col">
                        <div class="col">
                            <div class="text-block">
                                <h3 class="sub-head">关键发现</h3>
                                <ul class="big-list">
                                    <li>第一个关键发现，包含重要的数据支撑和分析结论</li>
                                    <li>第二个关键发现，展示了显著的增长趋势</li>
                                    <li>第三个关键发现，提供了战略性建议</li>
                                </ul>
                            </div>
                        </div>
                        <div class="col">
                            <div class="data-card">
                                <div class="data-val">45%</div>
                                <div class="data-lbl">同比增长率</div>
                            </div>
                            <div class="data-card" style="margin-top: 20px;">
                                <div class="data-val">128亿</div>
                                <div class="data-lbl">年度营收</div>
                            </div>
                        </div>
                    </div>
                    <div class="bottom-box">
                        <div class="bottom-text">综合分析表明，该领域具有显著的发展潜力和投资价值</div>
                    </div>
                </main>
                <footer class="slide-footer">
                    <span>数据来源：课题组整理</span>
                </footer>
            </div>
        </div>
        
        <!-- 目录页预览 -->
        <div class="slide-preview">
            <div class="slide-label">目录页 (Catalog)</div>
            <div class="slide-container">
                <main class="content-area">
                    <div class="title-box">
                        <h1 class="page-title">报告核心框架</h1>
                    </div>
                    <div class="catalog-list">
                        <div class="catalog-item">
                            <div class="catalog-idx">01</div>
                            <div class="catalog-content">
                                <div class="catalog-name">研究背景与目标</div>
                                <div class="catalog-desc">分析当前市场环境和研究目标</div>
                            </div>
                        </div>
                        <div class="catalog-item">
                            <div class="catalog-idx">02</div>
                            <div class="catalog-content">
                                <div class="catalog-name">核心发现与分析</div>
                                <div class="catalog-desc">展示关键数据和深度分析结果</div>
                            </div>
                        </div>
                        <div class="catalog-item">
                            <div class="catalog-idx">03</div>
                            <div class="catalog-content">
                                <div class="catalog-name">战略建议与展望</div>
                                <div class="catalog-desc">提供可行的战略建议和未来展望</div>
                            </div>
                        </div>
                    </div>
                </main>
            </div>
        </div>
        
        <!-- 封底页预览 -->
        <div class="slide-preview">
            <div class="slide-label">封底页 (Closing)</div>
            <div class="slide-container closing-slide">
                <div class="closing-title">谢 谢 观 看</div>
                <div class="closing-contact">
                    <p>如有疑问，请联系项目组</p>
                    <p>联系邮箱：example@company.com</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    if output_path:
        Path(output_path).write_text(html, encoding='utf-8')
    
    return html


def generate_all_theme_previews(output_dir: str = "theme_previews"):
    """生成所有主题的预览"""
    from .theme_registry import THEME_REGISTRY
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 生成索引页
    index_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>主题预览索引</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 40px; background: #f5f5f5; }
        h1 { text-align: center; color: #333; }
        .theme-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto; }
        .theme-card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .theme-card h2 { margin: 0 0 10px 0; font-size: 18px; }
        .theme-card p { color: #666; font-size: 14px; margin: 0 0 15px 0; }
        .theme-card a { display: inline-block; padding: 8px 16px; background: #0066cc; color: white; text-decoration: none; border-radius: 4px; }
        .theme-card a:hover { background: #0052a3; }
        .color-bar { display: flex; height: 8px; border-radius: 4px; overflow: hidden; margin-bottom: 15px; }
        .color-bar span { flex: 1; }
    </style>
</head>
<body>
    <h1>🎨 主题预览索引</h1>
    <div class="theme-grid">
"""
    
    for theme_id, theme in THEME_REGISTRY.items():
        # 生成单个主题预览
        preview_file = f"{theme_id}.html"
        generate_theme_preview(theme, str(output_path / preview_file))
        
        # 添加到索引
        index_html += f"""
        <div class="theme-card">
            <div class="color-bar">
                <span style="background: {theme.colors.primary};"></span>
                <span style="background: {theme.colors.primary_light};"></span>
                <span style="background: {theme.colors.accent};"></span>
            </div>
            <h2>{theme.metadata.name}</h2>
            <p>{theme.metadata.description}</p>
            <a href="{preview_file}">查看预览</a>
        </div>
"""
    
    index_html += """
    </div>
</body>
</html>
"""
    
    (output_path / "index.html").write_text(index_html, encoding='utf-8')
    
    return str(output_path / "index.html")
