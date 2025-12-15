"""
主题系统 - 支持多种演示文稿风格

主题类型:
- consulting: 咨询研究/汇报类 (深蓝商务风)
- annual_review: 年终述职/总结类 (稳重专业风)
- company_intro: 公司/项目介绍类 (现代科技风)
- academic: 学术研究/论文答辩类 (简洁学术风)
- creative: 创意/营销类 (活力创意风)
- government: 政府公文类 (庄重严肃风)
"""

from .theme_manager import ThemeManager, Theme, ColorPalette, Typography, Layout
from .theme_registry import (
    THEME_REGISTRY, 
    get_theme, 
    list_themes,
    get_themes_by_category,
    THEME_CATEGORIES,
    DEFAULT_THEME_ID
)
from .css_generator import CSSGenerator, generate_theme_css
from .prompt_generator import PromptGenerator, generate_system_prompt, generate_page_prompt
from .preview import generate_theme_preview, generate_all_theme_previews

__all__ = [
    # 核心类
    'ThemeManager',
    'Theme',
    'ColorPalette',
    'Typography',
    'Layout',
    
    # 注册表
    'THEME_REGISTRY',
    'THEME_CATEGORIES',
    'DEFAULT_THEME_ID',
    
    # 便捷函数
    'get_theme',
    'list_themes',
    'get_themes_by_category',
    
    # CSS 生成
    'CSSGenerator',
    'generate_theme_css',
    
    # Prompt 生成
    'PromptGenerator',
    'generate_system_prompt',
    'generate_page_prompt',
    
    # 预览
    'generate_theme_preview',
    'generate_all_theme_previews',
]
