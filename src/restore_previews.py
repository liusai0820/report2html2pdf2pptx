
import os
import sys
from pathlib import Path

# Setup path
src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

from themes.css_generator import CSSGenerator
from themes.theme_manager import ThemeManager

# Init Manager
theme_manager = ThemeManager()

# Scenarios definitions (key: scenario_id, value: best_match_theme_id)
# 根据 server.py 的 SCENARIOS 定义映射最合适的主题
SCENARIO_MAP = {
    "consulting": "consulting_default",     # 咨询
    "annual_review": "annual_review",       # 年终
    "company_intro": "tech_simple",         # 科技/公司 (tech_simple or business_blue)
    "academic": "academic_paper",           # 学术 (假设有 academic_paper)
    "creative": "creative_vibrant",         # 创意
    "government": "government_red",         # 政府
}

# Fallback mapping if exact ID not found
CATEGORY_MAP = {
    "consulting": "consulting",
    "annual_review": "annual_review", 
    "company_intro": "company_intro",
    "academic": "academic",
    "creative": "creative",
    "government": "government"
}

def generate_preview_html():
    output_dir = src_path / "previews"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating previews to {output_dir}...")

    # 我们需要 server.py 里的原始 SCENARIO 列表信息来获取 Name
    SERVER_SCENARIOS = [
        {"id": "consulting", "name": "咨询研究/汇报"},
        {"id": "annual_review", "name": "年终述职/总结"},
        {"id": "company_intro", "name": "公司/项目介绍"},
        {"id": "academic", "name": "学术研究/答辩"},
        {"id": "creative", "name": "创意/营销"},
        {"id": "government", "name": "政府公文"},
    ]

    for scenario_info in SERVER_SCENARIOS:
        scenario_id = scenario_info['id']
        scenario_name = scenario_info['name']
        print(f"Processing {scenario_id}...")
        
        # 1. Get Best Theme
        theme_id = SCENARIO_MAP.get(scenario_id)
        theme = theme_manager.get_theme(theme_id)
        
        # Fallback to category search if not found
        if not theme:
            cat = CATEGORY_MAP.get(scenario_id, "consulting")
            themes = theme_manager.list_by_category(cat)
            if themes:
                theme = themes[0]
            else:
                # Ultimate fallback
                theme = theme_manager.get_theme("consulting_default")
                
        if not theme:
            print(f"❌ No theme found for {scenario_id}, skipping")
            continue
            
        print(f"   Using theme: {theme.metadata.name}")

        # 2. Generate CSS
        css_gen = CSSGenerator(theme)
        css = css_gen.generate_full_css()
        
        # 3. Create HTML Content
        # 注意: CSS 和 JS 中的 { } 必须转义为 {{ }}
        # 只有 python 变量才用 {var}
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{scenario_name} - Preview</title>
    <style>
        {css}
        
        /* Fix for preview sizing */
        body {{
            transform-origin: top left;
            overflow: hidden;
            background: #e0e0e0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }}
        .slide-container {{
            width: 1280px;
            height: 720px;
            overflow: hidden;
            position: relative;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            /* Scale down to fit if needed, but usually iframe handles this */
        }}
    </style>
    <!-- Preview Metadata for Frontend Extraction -->
    <div class="preview-header" style="display:none;">
        <p>标签: {scenario_name}</p>
        <div class="color-swatch" style="background-color: {theme.colors.primary}">{theme.colors.primary}</div>
        <div class="description">{theme.metadata.description}</div>
    </div>
</head>
<body>

    <!-- Cover Page -->
    <div class="slide-container cover-slide">
        <!-- Cover content structure matching CSS generator expectations -->
        <div class="cover-top">
            <div class="doc-type">演示文档</div>
            <div class="brand-line"></div>
        </div>
        
        <div class="main-title">{scenario_name}</div>
        <div class="sub-title">AI 智能生成的演示文稿预览 - 风格: {theme.metadata.name}</div>
        
        <div class="cover-bottom">
            <div class="footer-row">
                <div class="footer-item">汇报人：SlideCraft AI</div>
                <div class="footer-item">日期：2024年12月</div>
            </div>
        </div>
    </div>

</body>
</html>
"""
        
        # 3. Save
        path = output_dir / f"{scenario_id}.html"
        path.write_text(html, encoding="utf-8")
        print(f"✓ Saved {path}")

if __name__ == "__main__":
    generate_preview_html()
