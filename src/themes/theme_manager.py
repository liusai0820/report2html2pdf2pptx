"""
主题管理器 - 核心主题系统

支持:
1. 预设主题加载
2. 用户自定义配置覆盖
3. CSS 变量动态注入
4. 主题继承和扩展
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List, Any
from pathlib import Path
import json
import copy


@dataclass
class ColorPalette:
    """配色方案"""
    primary: str = "#003366"          # 主色调
    primary_light: str = "#0066CC"    # 主色调亮色
    primary_dark: str = "#001a33"     # 主色调暗色
    accent: str = "#FFD700"           # 强调色
    text_primary: str = "#333333"     # 主文字色
    text_secondary: str = "#666666"   # 次要文字色
    text_light: str = "#999999"       # 浅色文字
    background: str = "#FFFFFF"       # 背景色
    background_alt: str = "#F5F7FA"   # 备选背景色
    border: str = "#E0E0E0"           # 边框色
    success: str = "#00A86B"          # 成功色
    warning: str = "#FF9500"          # 警告色
    error: str = "#FF3B30"            # 错误色
    
    def to_css_vars(self) -> str:
        """转换为 CSS 变量"""
        return f"""
    --primary: {self.primary};
    --primary-light: {self.primary_light};
    --primary-dark: {self.primary_dark};
    --accent: {self.accent};
    --text-primary: {self.text_primary};
    --text-secondary: {self.text_secondary};
    --text-light: {self.text_light};
    --background: {self.background};
    --background-alt: {self.background_alt};
    --border: {self.border};
    --success: {self.success};
    --warning: {self.warning};
    --error: {self.error};
    
    /* 兼容旧变量名 */
    --deep-blue: {self.primary};
    --bright-blue: {self.primary_light};
    --text-main: {self.text_primary};
    --text-sub: {self.text_secondary};
    --bg-gray: {self.background_alt};
    --line-gray: {self.border};
"""


@dataclass
class Typography:
    """字体排版配置"""
    font_family: str = '"Microsoft YaHei", "微软雅黑", "Heiti SC", sans-serif'
    font_family_heading: str = '"Microsoft YaHei", "微软雅黑", "Heiti SC", sans-serif'
    font_family_mono: str = '"Monaco", "Courier New", monospace'
    
    # 字号配置 (px)
    size_cover_title: int = 56       # 封面大标题
    size_page_title: int = 36        # 页面主标题
    size_section_title: int = 48     # 章节标题
    size_heading: int = 24           # 一级观点
    size_body: int = 20              # 正文
    size_small: int = 16             # 图表/注释
    size_footer: int = 14            # 页脚
    
    # 行高
    line_height_heading: float = 1.3
    line_height_body: float = 1.6
    
    # 字重
    weight_normal: int = 400
    weight_bold: int = 700
    
    def to_css_vars(self) -> str:
        """转换为 CSS 变量"""
        return f"""
    --font-family: {self.font_family};
    --font-family-heading: {self.font_family_heading};
    --font-family-mono: {self.font_family_mono};
    
    --size-cover-title: {self.size_cover_title}px;
    --size-page-title: {self.size_page_title}px;
    --size-section-title: {self.size_section_title}px;
    --size-heading: {self.size_heading}px;
    --size-body: {self.size_body}px;
    --size-small: {self.size_small}px;
    --size-footer: {self.size_footer}px;
    
    --line-height-heading: {self.line_height_heading};
    --line-height-body: {self.line_height_body};
    
    --weight-normal: {self.weight_normal};
    --weight-bold: {self.weight_bold};
"""


@dataclass
class Layout:
    """布局配置"""
    slide_width: int = 1280           # 幻灯片宽度
    slide_height: int = 720           # 幻灯片高度
    padding_horizontal: int = 60      # 水平内边距
    padding_vertical: int = 40        # 垂直内边距
    gap_large: int = 60               # 大间距
    gap_medium: int = 30              # 中间距
    gap_small: int = 15               # 小间距
    border_radius: int = 4            # 圆角
    
    def to_css_vars(self) -> str:
        """转换为 CSS 变量"""
        return f"""
    --slide-width: {self.slide_width}px;
    --slide-height: {self.slide_height}px;
    --padding-h: {self.padding_horizontal}px;
    --padding-v: {self.padding_vertical}px;
    --gap-large: {self.gap_large}px;
    --gap-medium: {self.gap_medium}px;
    --gap-small: {self.gap_small}px;
    --border-radius: {self.border_radius}px;
"""


@dataclass
class ChartConfig:
    """图表配置"""
    colors: List[str] = field(default_factory=lambda: [
        "#005EB8", "#0F2B51", "#8893A1", "#00A86B", "#FF9500"
    ])
    font_size: int = 14
    animation: bool = False  # PDF 导出时关闭动画
    
    def to_echarts_config(self) -> Dict[str, Any]:
        """转换为 ECharts 配置"""
        return {
            "color": self.colors,
            "animation": self.animation,
            "textStyle": {
                "fontSize": self.font_size
            }
        }


@dataclass 
class ThemeMetadata:
    """主题元数据"""
    id: str                           # 主题 ID
    name: str                         # 显示名称
    description: str                  # 描述
    category: str                     # 分类: consulting, annual_review, company_intro, academic, creative
    tags: List[str] = field(default_factory=list)  # 标签
    author: str = "System"            # 作者
    version: str = "1.0.0"            # 版本
    preview_image: Optional[str] = None  # 预览图


@dataclass
class Theme:
    """完整主题定义"""
    metadata: ThemeMetadata
    colors: ColorPalette = field(default_factory=ColorPalette)
    typography: Typography = field(default_factory=Typography)
    layout: Layout = field(default_factory=Layout)
    chart: ChartConfig = field(default_factory=ChartConfig)
    
    # 自定义 CSS (可选)
    custom_css: str = ""
    
    # 页面特定样式覆盖
    cover_style: Dict[str, Any] = field(default_factory=dict)
    section_style: Dict[str, Any] = field(default_factory=dict)
    content_style: Dict[str, Any] = field(default_factory=dict)
    closing_style: Dict[str, Any] = field(default_factory=dict)
    
    def generate_css_variables(self) -> str:
        """生成完整的 CSS 变量定义"""
        return f""":root {{
{self.colors.to_css_vars()}
{self.typography.to_css_vars()}
{self.layout.to_css_vars()}
}}
"""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "metadata": {
                "id": self.metadata.id,
                "name": self.metadata.name,
                "description": self.metadata.description,
                "category": self.metadata.category,
                "tags": self.metadata.tags,
                "author": self.metadata.author,
                "version": self.metadata.version,
            },
            "colors": self.colors.__dict__,
            "typography": self.typography.__dict__,
            "layout": self.layout.__dict__,
            "chart": {
                "colors": self.chart.colors,
                "font_size": self.chart.font_size,
                "animation": self.chart.animation
            },
            "custom_css": self.custom_css
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Theme':
        """从字典创建主题"""
        metadata = ThemeMetadata(
            id=data["metadata"]["id"],
            name=data["metadata"]["name"],
            description=data["metadata"]["description"],
            category=data["metadata"]["category"],
            tags=data["metadata"].get("tags", []),
            author=data["metadata"].get("author", "System"),
            version=data["metadata"].get("version", "1.0.0"),
        )
        
        colors = ColorPalette(**data.get("colors", {}))
        typography = Typography(**data.get("typography", {}))
        layout = Layout(**data.get("layout", {}))
        chart = ChartConfig(**data.get("chart", {}))
        
        return cls(
            metadata=metadata,
            colors=colors,
            typography=typography,
            layout=layout,
            chart=chart,
            custom_css=data.get("custom_css", "")
        )


class ThemeManager:
    """主题管理器"""
    
    def __init__(self, themes_dir: Optional[Path] = None):
        self.themes_dir = themes_dir or Path(__file__).parent / "presets"
        self._themes: Dict[str, Theme] = {}
        self._load_builtin_themes()
    
    def _load_builtin_themes(self):
        """加载内置主题"""
        from .theme_registry import THEME_REGISTRY
        self._themes = copy.deepcopy(THEME_REGISTRY)
    
    def get_theme(self, theme_id: str) -> Optional[Theme]:
        """获取主题"""
        return self._themes.get(theme_id)
    
    def list_themes(self) -> List[Dict[str, Any]]:
        """列出所有主题"""
        return [
            {
                "id": theme.metadata.id,
                "name": theme.metadata.name,
                "description": theme.metadata.description,
                "category": theme.metadata.category,
                "tags": theme.metadata.tags
            }
            for theme in self._themes.values()
        ]
    
    def list_by_category(self, category: str) -> List[Theme]:
        """按分类列出主题"""
        return [
            theme for theme in self._themes.values()
            if theme.metadata.category == category
        ]
    
    def create_custom_theme(
        self,
        base_theme_id: str,
        overrides: Dict[str, Any],
        new_id: Optional[str] = None
    ) -> Theme:
        """基于现有主题创建自定义主题"""
        base_theme = self.get_theme(base_theme_id)
        if not base_theme:
            raise ValueError(f"Base theme not found: {base_theme_id}")
        
        # 深拷贝基础主题
        new_theme = copy.deepcopy(base_theme)
        
        # 应用覆盖配置
        if "colors" in overrides:
            for key, value in overrides["colors"].items():
                if hasattr(new_theme.colors, key):
                    setattr(new_theme.colors, key, value)
        
        if "typography" in overrides:
            for key, value in overrides["typography"].items():
                if hasattr(new_theme.typography, key):
                    setattr(new_theme.typography, key, value)
        
        if "layout" in overrides:
            for key, value in overrides["layout"].items():
                if hasattr(new_theme.layout, key):
                    setattr(new_theme.layout, key, value)
        
        if "chart" in overrides:
            if "colors" in overrides["chart"]:
                new_theme.chart.colors = overrides["chart"]["colors"]
            if "font_size" in overrides["chart"]:
                new_theme.chart.font_size = overrides["chart"]["font_size"]
        
        if "custom_css" in overrides:
            new_theme.custom_css += "\n" + overrides["custom_css"]
        
        # 更新元数据
        if new_id:
            new_theme.metadata.id = new_id
            new_theme.metadata.name = overrides.get("name", f"Custom - {base_theme.metadata.name}")
        
        return new_theme
    
    def apply_user_config(self, theme: Theme, user_config: Dict[str, Any]) -> Theme:
        """应用用户配置到主题"""
        return self.create_custom_theme(
            theme.metadata.id,
            user_config,
            new_id=f"{theme.metadata.id}_custom"
        )
    
    def save_theme(self, theme: Theme, filepath: Path):
        """保存主题到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(theme.to_dict(), f, ensure_ascii=False, indent=2)
    
    def load_theme(self, filepath: Path) -> Theme:
        """从文件加载主题"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return Theme.from_dict(data)
    
    def register_theme(self, theme: Theme):
        """注册新主题"""
        self._themes[theme.metadata.id] = theme
