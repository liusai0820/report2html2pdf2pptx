"""
Design System - 设计系统 Token

@input:  场景类型, 用户自定义颜色, 字体风格
@output: DesignSystem, DesignTokens, ColorPalette, Typography
@pos:    V2引擎的视觉约束层，定义所有可用的设计变量

⚠️ 一旦我被更新，务必更新：
   1. 我的头部注释
   2. /src/v2/_FOLDER.md

这是唯一的"约束层"，只定义：
1. 颜色 Palette
2. 字体/字号范围
3. 间距系统
4. 画布尺寸

不定义：
- 具体布局模板
- 组件结构
- 内容规则

AI 可以在这些约束内自由创作。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class ScenarioType(Enum):
    """场景类型"""
    CONSULTING = "consulting"           # 咨询研究/汇报
    ANNUAL_REVIEW = "annual_review"     # 年终述职/总结
    COMPANY_INTRO = "company_intro"     # 公司/项目介绍
    ACADEMIC = "academic"               # 学术研究/答辩
    CREATIVE = "creative"               # 创意/营销
    GOVERNMENT = "government"           # 政府公文


@dataclass
class ColorPalette:
    """配色方案 - AI 必须使用这些颜色"""
    
    # 主色系
    primary: str = "#1e40af"            # 主色调（深蓝）
    primary_light: str = "#3b82f6"      # 主色亮色
    primary_dark: str = "#1e3a8a"       # 主色暗色
    
    # 强调色
    accent: str = "#f59e0b"             # 强调色（琥珀）
    accent_light: str = "#fbbf24"       # 强调色亮色
    
    # 语义色
    success: str = "#10b981"            # 成功/增长
    warning: str = "#f59e0b"            # 警告/注意
    danger: str = "#ef4444"             # 危险/下降
    info: str = "#3b82f6"               # 信息
    
    # 中性色
    text_primary: str = "#1f2937"       # 主文字
    text_secondary: str = "#6b7280"     # 次要文字
    text_light: str = "#9ca3af"         # 浅色文字
    text_inverse: str = "#ffffff"       # 反色文字（用于深色背景）
    
    # 背景色
    background: str = "#ffffff"         # 主背景
    background_alt: str = "#f9fafb"     # 备选背景
    background_dark: str = "#111827"    # 深色背景
    
    # 边框/分割线
    border: str = "#e5e7eb"             # 边框
    divider: str = "#f3f4f6"            # 分割线
    
    def to_css_vars(self) -> str:
        """转换为 CSS 变量"""
        return f"""
:root {{
    --color-primary: {self.primary};
    --color-primary-light: {self.primary_light};
    --color-primary-dark: {self.primary_dark};
    --color-accent: {self.accent};
    --color-accent-light: {self.accent_light};
    --color-success: {self.success};
    --color-warning: {self.warning};
    --color-danger: {self.danger};
    --color-info: {self.info};
    --color-text-primary: {self.text_primary};
    --color-text-secondary: {self.text_secondary};
    --color-text-light: {self.text_light};
    --color-text-inverse: {self.text_inverse};
    --color-background: {self.background};
    --color-background-alt: {self.background_alt};
    --color-background-dark: {self.background_dark};
    --color-border: {self.border};
    --color-divider: {self.divider};
}}
"""
    
    def to_dict(self) -> Dict[str, str]:
        """转换为字典（用于传递给 AI）"""
        return {
            "primary": self.primary,
            "primary_light": self.primary_light,
            "primary_dark": self.primary_dark,
            "accent": self.accent,
            "accent_light": self.accent_light,
            "success": self.success,
            "warning": self.warning,
            "danger": self.danger,
            "info": self.info,
            "text_primary": self.text_primary,
            "text_secondary": self.text_secondary,
            "text_light": self.text_light,
            "text_inverse": self.text_inverse,
            "background": self.background,
            "background_alt": self.background_alt,
            "background_dark": self.background_dark,
            "border": self.border,
            "divider": self.divider,
        }


@dataclass
class Typography:
    """字体排版 - AI 必须遵守的字体规范"""
    
    # 字体风格: 'modern' (黑体) 或 'classic' (楷体)
    font_style: str = "modern"
    
    # 字体族预设 - 使用 Web 字体确保 PDF 可编辑
    FONT_PRESETS = {
        "modern": {
            # 现代风格 - 黑体系 (使用 Noto Sans SC Web 字体)
            "base": "'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif",
            "heading": "'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif",
            "display_name": "现代简约（黑体）"
        },
        "classic": {
            # 典雅风格 - 楷体系 (使用 LXGW WenKai 和 Ma Shan Zheng Web 字体)
            # 这两个是 Google Fonts 官方支持的中文楷体，可以正确嵌入 PDF
            "base": "'LXGW WenKai', 'Ma Shan Zheng', 'STKaiti', 'KaiTi', serif",
            "heading": "'LXGW WenKai', 'Ma Shan Zheng', 'STKaiti', 'KaiTi', serif",
            "display_name": "典雅庄重（楷体）"
        }
    }
    
    # 字体族 - 由 font_style 动态决定
    font_family_base: str = ""
    font_family_heading: str = ""
    font_family_mono: str = "'JetBrains Mono', 'Fira Code', monospace"
    
    # 字号范围（px）- AI 可以在范围内选择
    size_hero: int = 72         # 封面大标题（60-80）
    size_title: int = 48        # 章节标题（40-56）
    size_heading_1: int = 36    # 页面标题（32-40）
    size_heading_2: int = 28    # 二级标题（24-32）
    size_heading_3: int = 22    # 三级标题（20-26）
    size_body: int = 18         # 正文（16-20）
    size_small: int = 14        # 小字/注释（12-16）
    size_tiny: int = 12         # 最小字（10-14）
    
    # 字重
    weight_light: int = 300
    weight_normal: int = 400
    weight_medium: int = 500
    weight_semibold: int = 600
    weight_bold: int = 700
    weight_black: int = 900
    
    # 行高
    line_height_tight: float = 1.2      # 标题
    line_height_normal: float = 1.5     # 正文
    line_height_relaxed: float = 1.75   # 宽松
    
    # 字间距
    letter_spacing_tight: str = "-0.02em"
    letter_spacing_normal: str = "0"
    letter_spacing_wide: str = "0.05em"
    
    def __post_init__(self):
        """初始化后根据 font_style 设置字体族"""
        preset = self.FONT_PRESETS.get(self.font_style, self.FONT_PRESETS["modern"])
        if not self.font_family_base:
            self.font_family_base = preset["base"]
        if not self.font_family_heading:
            self.font_family_heading = preset["heading"]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "font_style": self.font_style,
            "font_family_base": self.font_family_base,
            "font_family_heading": self.font_family_heading,
            "font_family_mono": self.font_family_mono,
            "sizes": {
                "hero": self.size_hero,
                "title": self.size_title,
                "heading_1": self.size_heading_1,
                "heading_2": self.size_heading_2,
                "heading_3": self.size_heading_3,
                "body": self.size_body,
                "small": self.size_small,
                "tiny": self.size_tiny,
            },
            "weights": {
                "light": self.weight_light,
                "normal": self.weight_normal,
                "medium": self.weight_medium,
                "semibold": self.weight_semibold,
                "bold": self.weight_bold,
                "black": self.weight_black,
            },
            "line_heights": {
                "tight": self.line_height_tight,
                "normal": self.line_height_normal,
                "relaxed": self.line_height_relaxed,
            }
        }


@dataclass
class Spacing:
    """间距系统"""
    
    # 基础间距单位（px）
    unit: int = 4
    
    # 预设间距
    xs: int = 4      # 1 unit
    sm: int = 8      # 2 units
    md: int = 16     # 4 units
    lg: int = 24     # 6 units
    xl: int = 32     # 8 units
    xxl: int = 48    # 12 units
    xxxl: int = 64   # 16 units
    
    # 页面边距
    page_margin_x: int = 60     # 水平边距
    page_margin_y: int = 40     # 垂直边距
    
    def to_dict(self) -> Dict[str, int]:
        return {
            "unit": self.unit,
            "xs": self.xs,
            "sm": self.sm,
            "md": self.md,
            "lg": self.lg,
            "xl": self.xl,
            "xxl": self.xxl,
            "xxxl": self.xxxl,
            "page_margin_x": self.page_margin_x,
            "page_margin_y": self.page_margin_y,
        }


@dataclass
class Canvas:
    """画布尺寸"""
    
    width: int = 1280       # 16:9 宽度
    height: int = 720       # 16:9 高度
    
    # 安全区域（距离边缘的最小距离）
    safe_margin: int = 40
    
    # 内容区域（扣除边距后）
    @property
    def content_width(self) -> int:
        return self.width - 2 * self.safe_margin
    
    @property
    def content_height(self) -> int:
        return self.height - 2 * self.safe_margin
    
    def to_dict(self) -> Dict[str, int]:
        return {
            "width": self.width,
            "height": self.height,
            "safe_margin": self.safe_margin,
            "content_width": self.content_width,
            "content_height": self.content_height,
        }


@dataclass
class Effects:
    """视觉效果"""
    
    # 圆角
    radius_none: int = 0
    radius_sm: int = 4
    radius_md: int = 8
    radius_lg: int = 12
    radius_xl: int = 16
    radius_full: str = "9999px"
    
    # 阴影
    shadow_sm: str = "0 1px 2px rgba(0,0,0,0.05)"
    shadow_md: str = "0 4px 6px rgba(0,0,0,0.07)"
    shadow_lg: str = "0 10px 15px rgba(0,0,0,0.1)"
    shadow_xl: str = "0 20px 25px rgba(0,0,0,0.15)"
    
    # 渐变方向建议
    gradient_directions: List[str] = field(default_factory=lambda: [
        "to right",
        "to bottom right",
        "135deg",
        "180deg",
    ])
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "radius": {
                "none": self.radius_none,
                "sm": self.radius_sm,
                "md": self.radius_md,
                "lg": self.radius_lg,
                "xl": self.radius_xl,
                "full": self.radius_full,
            },
            "shadow": {
                "sm": self.shadow_sm,
                "md": self.shadow_md,
                "lg": self.shadow_lg,
                "xl": self.shadow_xl,
            }
        }


@dataclass
class DesignTokens:
    """设计 Token 集合"""
    
    colors: ColorPalette = field(default_factory=ColorPalette)
    typography: Typography = field(default_factory=Typography)
    spacing: Spacing = field(default_factory=Spacing)
    canvas: Canvas = field(default_factory=Canvas)
    effects: Effects = field(default_factory=Effects)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为完整字典"""
        return {
            "colors": self.colors.to_dict(),
            "typography": self.typography.to_dict(),
            "spacing": self.spacing.to_dict(),
            "canvas": self.canvas.to_dict(),
            "effects": self.effects.to_dict(),
        }
    
    def to_ai_prompt(self) -> str:
        """生成 AI 可理解的设计系统描述"""
        return f"""
## 🎨 设计系统约束

### 画布
- 尺寸: {self.canvas.width} × {self.canvas.height} 像素
- 安全边距: {self.canvas.safe_margin}px（内容不能超出此范围）
- 可用内容区: {self.canvas.content_width} × {self.canvas.content_height} 像素

### 配色方案（必须使用这些颜色）
- 主色: {self.colors.primary}
- 主色亮: {self.colors.primary_light}
- 主色暗: {self.colors.primary_dark}
- 强调色: {self.colors.accent}
- 成功色: {self.colors.success}
- 警告色: {self.colors.warning}
- 危险色: {self.colors.danger}
- 主文字: {self.colors.text_primary}
- 次要文字: {self.colors.text_secondary}
- 浅色文字: {self.colors.text_light}
- 白色文字: {self.colors.text_inverse}
- 背景色: {self.colors.background}
- 备选背景: {self.colors.background_alt}
- 深色背景: {self.colors.background_dark}

### 字体
- 基础字体: {self.typography.font_family_base}
- 标题字体: {self.typography.font_family_heading}
- 等宽字体: {self.typography.font_family_mono}

### 字号范围（可在范围内灵活选择）
- 封面大标题: 60-80px（推荐 {self.typography.size_hero}px）
- 章节标题: 40-56px（推荐 {self.typography.size_title}px）
- 页面标题: 32-40px（推荐 {self.typography.size_heading_1}px）
- 二级标题: 24-32px（推荐 {self.typography.size_heading_2}px）
- 三级标题: 20-26px（推荐 {self.typography.size_heading_3}px）
- 正文: 16-20px（推荐 {self.typography.size_body}px）
- 小字: 12-16px（推荐 {self.typography.size_small}px）

### 间距
- 页面边距: {self.spacing.page_margin_x}px（水平），{self.spacing.page_margin_y}px（垂直）
- 元素间距建议: {self.spacing.sm}px / {self.spacing.md}px / {self.spacing.lg}px / {self.spacing.xl}px

### 视觉效果
- 圆角: {self.effects.radius_sm}px / {self.effects.radius_md}px / {self.effects.radius_lg}px
- 阴影: 使用 box-shadow 增加层次感
"""


class DesignSystem:
    """
    设计系统主类
    
    职责：
    1. 管理设计 Token
    2. 根据场景调整配色
    3. 支持用户自定义覆盖
    """
    
    # 场景预设配色（与 output/theme_previews/*.html 保持一致）
    SCENARIO_PRESETS: Dict[ScenarioType, Dict[str, str]] = {
        ScenarioType.CONSULTING: {
            "primary": "#003366",        # 深蓝商务（与 consulting.html 一致）
            "primary_light": "#0066CC",
            "primary_dark": "#001a33",
            "accent": "#FFD700",          # 金色强调
        },
        ScenarioType.ANNUAL_REVIEW: {
            "primary": "#1A365D",         # 深蓝述职（与 annual_review.html 一致）
            "primary_light": "#2B6CB0",
            "primary_dark": "#0D1B2A",
            "accent": "#E53E3E",           # 红色强调
        },
        ScenarioType.COMPANY_INTRO: {
            "primary": "#0A0A0A",          # 黑色商务（与 company_intro.html 一致）
            "primary_light": "#3182CE",
            "primary_dark": "#000000",
            "accent": "#00D4FF",           # 青色强调
        },
        ScenarioType.ACADEMIC: {
            "primary": "#2C3E50",          # 深灰学术（与 academic.html 一致）
            "primary_light": "#3498DB",
            "primary_dark": "#1A252F",
            "accent": "#27AE60",           # 绿色强调
        },
        ScenarioType.CREATIVE: {
            "primary": "#6C5CE7",          # 紫色创意（与 creative.html 一致）
            "primary_light": "#A29BFE",
            "primary_dark": "#5B4BC4",
            "accent": "#FF6B6B",           # 红色强调
        },
        ScenarioType.GOVERNMENT: {
            "primary": "#C41E3A",          # 中国红（与 government.html 一致）
            "primary_light": "#E53935",
            "primary_dark": "#8B0000",
            "accent": "#FFD700",           # 金色强调
        },
    }
    
    def __init__(
        self,
        scenario: ScenarioType = ScenarioType.CONSULTING,
        custom_colors: Optional[Dict[str, str]] = None,
        font_style: str = "modern",  # 'modern' (黑体) 或 'classic' (楷体)
    ):
        self.scenario = scenario
        self.font_style = font_style
        self.tokens = self._create_tokens(scenario, custom_colors, font_style)
    
    def _create_tokens(
        self,
        scenario: ScenarioType,
        custom_colors: Optional[Dict[str, str]] = None,
        font_style: str = "modern"
    ) -> DesignTokens:
        """创建设计 Token"""
         
        # 获取场景预设
        preset = self.SCENARIO_PRESETS.get(scenario, self.SCENARIO_PRESETS[ScenarioType.CONSULTING])
        
        # 创建配色
        colors = ColorPalette(
            primary=preset["primary"],
            primary_light=preset["primary_light"],
            primary_dark=preset["primary_dark"],
            accent=preset["accent"],
        )
        
        # 应用用户自定义
        if custom_colors:
            for key, value in custom_colors.items():
                if hasattr(colors, key):
                    setattr(colors, key, value)
        
        # 创建字体排版配置
        typography = Typography(font_style=font_style)
        
        return DesignTokens(colors=colors, typography=typography)
    
    def get_tokens(self) -> DesignTokens:
        """获取设计 Token"""
        return self.tokens
    
    def get_ai_prompt(self) -> str:
        """获取 AI 可理解的设计系统描述"""
        return self.tokens.to_ai_prompt()
    
    def update_colors(self, **kwargs):
        """更新颜色"""
        for key, value in kwargs.items():
            if hasattr(self.tokens.colors, key):
                setattr(self.tokens.colors, key, value)
    
    @classmethod
    def from_scenario(
        cls, 
        scenario_str: str, 
        custom_primary: Optional[str] = None,
        font_style: str = "modern"
    ) -> 'DesignSystem':
        """从场景字符串创建"""
        try:
            scenario = ScenarioType(scenario_str)
        except ValueError:
            scenario = ScenarioType.CONSULTING
        
        custom_colors = None
        if custom_primary:
            # 根据主色自动生成亮色和暗色
            custom_colors = {
                "primary": custom_primary,
                "primary_light": cls._lighten_color(custom_primary, 0.2),
                "primary_dark": cls._darken_color(custom_primary, 0.2),
            }
        
        return cls(scenario=scenario, custom_colors=custom_colors, font_style=font_style)
    
    @staticmethod
    def _lighten_color(hex_color: str, amount: float) -> str:
        """使颜色变亮"""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = min(255, int(r + (255 - r) * amount))
        g = min(255, int(g + (255 - g) * amount))
        b = min(255, int(b + (255 - b) * amount))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @staticmethod
    def _darken_color(hex_color: str, amount: float) -> str:
        """使颜色变暗"""
        hex_color = hex_color.lstrip('#')
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = max(0, int(r * (1 - amount)))
        g = max(0, int(g * (1 - amount)))
        b = max(0, int(b * (1 - amount)))
        return f"#{r:02x}{g:02x}{b:02x}"
