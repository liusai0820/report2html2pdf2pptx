"""
主题注册表 - 预设主题定义

包含以下主题类型:
1. consulting - 咨询研究/汇报类 (深蓝商务风)
2. annual_review - 年终述职/总结类 (稳重专业风)  
3. company_intro - 公司/项目介绍类 (现代科技风)
4. academic - 学术研究/论文答辩类 (简洁学术风)
5. creative - 创意/营销类 (活力创意风)
"""

from .theme_manager import (
    Theme, ThemeMetadata, ColorPalette, Typography, Layout, ChartConfig
)
from typing import Dict, List, Optional


# ============================================================
# 主题 1: 咨询研究/汇报类 (Consulting)
# ============================================================
CONSULTING_THEME = Theme(
    metadata=ThemeMetadata(
        id="consulting",
        name="咨询研究风格",
        description="适用于政府汇报、咨询报告、研究课题等正式场合，深蓝商务风格，庄重专业",
        category="consulting",
        tags=["政府", "咨询", "研究", "汇报", "正式"],
    ),
    colors=ColorPalette(
        primary="#003366",           # 深蓝 - 官方感
        primary_light="#0066CC",     # 亮蓝 - 强调
        primary_dark="#001a33",      # 深蓝暗色
        accent="#FFD700",            # 金色 - 点缀
        text_primary="#333333",      # 主文字
        text_secondary="#666666",    # 次要文字
        text_light="#999999",        # 浅色文字
        background="#FFFFFF",        # 白色背景
        background_alt="#F5F7FA",    # 浅灰背景
        border="#E0E0E0",            # 边框
    ),
    typography=Typography(
        font_family='"Microsoft YaHei", "微软雅黑", "Heiti SC", sans-serif',
        size_cover_title=56,
        size_page_title=36,
        size_section_title=48,
        size_heading=24,
        size_body=20,
        size_small=16,
    ),
    chart=ChartConfig(
        colors=["#005EB8", "#0F2B51", "#8893A1", "#00A86B", "#FF9500"],
    ),
    custom_css="""
/* 咨询风格特有样式 */
.section-slide {
    background: linear-gradient(135deg, #003366 0%, #0F2B51 100%);
}
.brand-line {
    background: #003366;
}
.bottom-box {
    border-left: 8px solid #003366;
}
"""
)


# ============================================================
# 主题 2: 年终述职/总结类 (Annual Review)
# ============================================================
ANNUAL_REVIEW_THEME = Theme(
    metadata=ThemeMetadata(
        id="annual_review",
        name="年终述职风格",
        description="适用于年终总结、工作汇报、述职报告等场合，稳重大气，突出成果",
        category="annual_review",
        tags=["年终", "述职", "总结", "汇报", "成果"],
    ),
    colors=ColorPalette(
        primary="#1A365D",           # 深海蓝 - 稳重
        primary_light="#2B6CB0",     # 中蓝 - 活力
        primary_dark="#0D1B2A",      # 深蓝黑
        accent="#ED8936",            # 橙色 - 成就感
        text_primary="#2D3748",      # 深灰文字
        text_secondary="#4A5568",    # 中灰文字
        text_light="#A0AEC0",        # 浅灰文字
        background="#FFFFFF",        # 白色背景
        background_alt="#EDF2F7",    # 浅蓝灰背景
        border="#E2E8F0",            # 边框
        success="#38A169",           # 绿色 - 增长
        warning="#DD6B20",           # 橙色 - 警示
    ),
    typography=Typography(
        font_family='"Microsoft YaHei", "微软雅黑", "PingFang SC", sans-serif',
        size_cover_title=52,
        size_page_title=34,
        size_section_title=44,
        size_heading=22,
        size_body=18,
        size_small=14,
    ),
    chart=ChartConfig(
        colors=["#2B6CB0", "#38A169", "#ED8936", "#E53E3E", "#805AD5"],
    ),
    custom_css="""
/* 年终述职特有样式 */
.section-slide {
    background: linear-gradient(135deg, #1A365D 0%, #2D3748 100%);
}
.data-card {
    border-top: 4px solid #ED8936;
}
.data-val {
    color: #2B6CB0;
}
/* 成果高亮 */
.achievement-highlight {
    background: linear-gradient(90deg, #ED8936 0%, #DD6B20 100%);
    color: white;
    padding: 8px 16px;
    border-radius: 4px;
    display: inline-block;
}
"""
)


# ============================================================
# 主题 3: 公司/项目介绍类 (Company Intro)
# ============================================================
COMPANY_INTRO_THEME = Theme(
    metadata=ThemeMetadata(
        id="company_intro",
        name="公司介绍风格",
        description="适用于公司介绍、项目路演、产品发布等场合，现代科技感，简洁有力",
        category="company_intro",
        tags=["公司", "项目", "路演", "产品", "科技"],
    ),
    colors=ColorPalette(
        primary="#0A0A0A",           # 纯黑 - 科技感
        primary_light="#3182CE",     # 科技蓝
        primary_dark="#000000",      # 纯黑
        accent="#00D4FF",            # 霓虹蓝 - 科技感
        text_primary="#1A1A1A",      # 深黑文字
        text_secondary="#4A4A4A",    # 中灰文字
        text_light="#8A8A8A",        # 浅灰文字
        background="#FFFFFF",        # 白色背景
        background_alt="#F7F7F7",    # 浅灰背景
        border="#E5E5E5",            # 边框
    ),
    typography=Typography(
        font_family='"SF Pro Display", "Microsoft YaHei", "PingFang SC", sans-serif',
        size_cover_title=60,         # 更大的封面标题
        size_page_title=38,
        size_section_title=52,
        size_heading=26,
        size_body=20,
        size_small=16,
    ),
    layout=Layout(
        padding_horizontal=80,       # 更大的边距
        padding_vertical=50,
        gap_large=80,
    ),
    chart=ChartConfig(
        colors=["#00D4FF", "#3182CE", "#0A0A0A", "#38A169", "#805AD5"],
    ),
    custom_css="""
/* 公司介绍特有样式 */
.section-slide {
    background: linear-gradient(135deg, #0A0A0A 0%, #1A1A2E 100%);
}
.section-line {
    background: linear-gradient(90deg, #00D4FF 0%, #3182CE 100%);
}
.brand-line {
    background: linear-gradient(90deg, #00D4FF 0%, #3182CE 100%);
}
/* 科技感数据卡片 */
.data-card {
    background: linear-gradient(135deg, #F7F7F7 0%, #FFFFFF 100%);
    border-top: 3px solid #00D4FF;
    box-shadow: 0 4px 20px rgba(0, 212, 255, 0.1);
}
.data-val {
    background: linear-gradient(90deg, #00D4FF 0%, #3182CE 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
"""
)


# ============================================================
# 主题 4: 学术研究/论文答辩类 (Academic)
# ============================================================
ACADEMIC_THEME = Theme(
    metadata=ThemeMetadata(
        id="academic",
        name="学术研究风格",
        description="适用于学术报告、论文答辩、研究分享等场合，简洁清晰，注重内容",
        category="academic",
        tags=["学术", "论文", "答辩", "研究", "教育"],
    ),
    colors=ColorPalette(
        primary="#2C3E50",           # 学院蓝 - 沉稳
        primary_light="#3498DB",     # 天蓝 - 清新
        primary_dark="#1A252F",      # 深蓝黑
        accent="#E74C3C",            # 红色 - 重点标注
        text_primary="#2C3E50",      # 深蓝灰文字
        text_secondary="#7F8C8D",    # 灰色文字
        text_light="#BDC3C7",        # 浅灰文字
        background="#FFFFFF",        # 白色背景
        background_alt="#ECF0F1",    # 浅灰背景
        border="#BDC3C7",            # 边框
    ),
    typography=Typography(
        font_family='"Source Han Sans SC", "Noto Sans SC", "Microsoft YaHei", sans-serif',
        size_cover_title=48,         # 相对小的标题
        size_page_title=32,
        size_section_title=40,
        size_heading=22,
        size_body=18,
        size_small=14,
        line_height_body=1.8,        # 更大的行高，便于阅读
    ),
    layout=Layout(
        padding_horizontal=50,
        padding_vertical=35,
        gap_large=50,
    ),
    chart=ChartConfig(
        colors=["#3498DB", "#2C3E50", "#E74C3C", "#27AE60", "#9B59B6"],
        font_size=12,
    ),
    custom_css="""
/* 学术风格特有样式 */
.section-slide {
    background: linear-gradient(135deg, #2C3E50 0%, #34495E 100%);
}
.section-line {
    background: #E74C3C;
}
/* 引用样式 */
.citation {
    font-size: 14px;
    color: #7F8C8D;
    font-style: italic;
    border-left: 3px solid #3498DB;
    padding-left: 15px;
    margin: 20px 0;
}
/* 公式/代码块 */
.formula-block {
    background: #ECF0F1;
    padding: 20px;
    border-radius: 4px;
    font-family: "Courier New", monospace;
    text-align: center;
}
"""
)


# ============================================================
# 主题 5: 创意/营销类 (Creative)
# ============================================================
CREATIVE_THEME = Theme(
    metadata=ThemeMetadata(
        id="creative",
        name="创意营销风格",
        description="适用于品牌推广、营销方案、创意提案等场合，活力四射，视觉冲击",
        category="creative",
        tags=["创意", "营销", "品牌", "推广", "设计"],
    ),
    colors=ColorPalette(
        primary="#6C5CE7",           # 紫色 - 创意
        primary_light="#A29BFE",     # 浅紫
        primary_dark="#5B4BC4",      # 深紫
        accent="#FD79A8",            # 粉色 - 活力
        text_primary="#2D3436",      # 深灰文字
        text_secondary="#636E72",    # 中灰文字
        text_light="#B2BEC3",        # 浅灰文字
        background="#FFFFFF",        # 白色背景
        background_alt="#F8F9FA",    # 浅灰背景
        border="#DFE6E9",            # 边框
        success="#00B894",           # 绿色
        warning="#FDCB6E",           # 黄色
    ),
    typography=Typography(
        font_family='"PingFang SC", "Microsoft YaHei", "Helvetica Neue", sans-serif',
        size_cover_title=64,         # 超大标题
        size_page_title=40,
        size_section_title=56,
        size_heading=28,
        size_body=20,
        size_small=16,
    ),
    layout=Layout(
        padding_horizontal=70,
        padding_vertical=45,
        gap_large=70,
        border_radius=8,             # 更大的圆角
    ),
    chart=ChartConfig(
        colors=["#6C5CE7", "#FD79A8", "#00B894", "#FDCB6E", "#74B9FF"],
    ),
    custom_css="""
/* 创意风格特有样式 */
.section-slide {
    background: linear-gradient(135deg, #6C5CE7 0%, #A29BFE 50%, #FD79A8 100%);
}
.section-line {
    background: linear-gradient(90deg, #FD79A8 0%, #FDCB6E 100%);
}
.brand-line {
    background: linear-gradient(90deg, #6C5CE7 0%, #FD79A8 100%);
    height: 6px;
}
/* 渐变数据卡片 */
.data-card {
    background: linear-gradient(135deg, #F8F9FA 0%, #FFFFFF 100%);
    border-top: none;
    border-radius: 12px;
    box-shadow: 0 8px 30px rgba(108, 92, 231, 0.15);
}
.data-val {
    background: linear-gradient(90deg, #6C5CE7 0%, #FD79A8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
/* 强调按钮 */
.cta-button {
    background: linear-gradient(90deg, #6C5CE7 0%, #FD79A8 100%);
    color: white;
    padding: 12px 30px;
    border-radius: 25px;
    font-weight: bold;
    display: inline-block;
}
"""
)


# ============================================================
# 主题 6: 政府公文类 (Government)
# ============================================================
GOVERNMENT_THEME = Theme(
    metadata=ThemeMetadata(
        id="government",
        name="政府公文风格",
        description="适用于政府报告、政策解读、党建汇报等场合，庄重严肃，符合公文规范",
        category="consulting",
        tags=["政府", "公文", "党建", "政策", "官方"],
    ),
    colors=ColorPalette(
        primary="#C41E3A",           # 中国红 - 庄重
        primary_light="#E53935",     # 亮红
        primary_dark="#8B0000",      # 深红
        accent="#FFD700",            # 金色 - 点缀
        text_primary="#1A1A1A",      # 纯黑文字
        text_secondary="#4A4A4A",    # 深灰文字
        text_light="#8A8A8A",        # 浅灰文字
        background="#FFFFFF",        # 白色背景
        background_alt="#FFF8F0",    # 米白背景
        border="#E0D5C5",            # 暖灰边框
    ),
    typography=Typography(
        font_family='"SimSun", "宋体", "Microsoft YaHei", serif',  # 宋体更正式
        font_family_heading='"Microsoft YaHei", "微软雅黑", "SimHei", sans-serif',
        size_cover_title=52,
        size_page_title=34,
        size_section_title=44,
        size_heading=22,
        size_body=18,
        size_small=14,
    ),
    chart=ChartConfig(
        colors=["#C41E3A", "#FFD700", "#1A1A1A", "#4A4A4A", "#8A8A8A"],
    ),
    custom_css="""
/* 政府公文特有样式 */
.section-slide {
    background: linear-gradient(135deg, #C41E3A 0%, #8B0000 100%);
}
.section-line {
    background: #FFD700;
}
.brand-line {
    background: #C41E3A;
}
/* 红头文件风格 */
.doc-type {
    color: #C41E3A;
    font-weight: bold;
    letter-spacing: 4px;
}
.main-title {
    border-bottom: 2px solid #C41E3A;
    padding-bottom: 20px;
}
"""
)


# ============================================================
# 主题注册表
# ============================================================
THEME_REGISTRY: Dict[str, Theme] = {
    "consulting": CONSULTING_THEME,
    "annual_review": ANNUAL_REVIEW_THEME,
    "company_intro": COMPANY_INTRO_THEME,
    "academic": ACADEMIC_THEME,
    "creative": CREATIVE_THEME,
    "government": GOVERNMENT_THEME,
}

# 默认主题
DEFAULT_THEME_ID = "consulting"


def get_theme(theme_id: str) -> Optional[Theme]:
    """获取主题"""
    return THEME_REGISTRY.get(theme_id)


def list_themes() -> List[Dict[str, str]]:
    """列出所有可用主题"""
    return [
        {
            "id": theme.metadata.id,
            "name": theme.metadata.name,
            "description": theme.metadata.description,
            "category": theme.metadata.category,
        }
        for theme in THEME_REGISTRY.values()
    ]


def get_themes_by_category(category: str) -> List[Theme]:
    """按分类获取主题"""
    return [
        theme for theme in THEME_REGISTRY.values()
        if theme.metadata.category == category
    ]


# 分类说明
THEME_CATEGORIES = {
    "consulting": {
        "name": "咨询研究类",
        "description": "适用于政府汇报、咨询报告、研究课题等正式场合",
        "themes": ["consulting", "government"]
    },
    "annual_review": {
        "name": "年终述职类", 
        "description": "适用于年终总结、工作汇报、述职报告等场合",
        "themes": ["annual_review"]
    },
    "company_intro": {
        "name": "公司介绍类",
        "description": "适用于公司介绍、项目路演、产品发布等场合",
        "themes": ["company_intro"]
    },
    "academic": {
        "name": "学术研究类",
        "description": "适用于学术报告、论文答辩、研究分享等场合",
        "themes": ["academic"]
    },
    "creative": {
        "name": "创意营销类",
        "description": "适用于品牌推广、营销方案、创意提案等场合",
        "themes": ["creative"]
    }
}
