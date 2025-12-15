"""
用户配置模型 - 管理用户的个性化配置

功能:
1. 定义用户配置结构
2. 配置验证
3. 配置持久化
4. 与主题系统集成
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from pathlib import Path
import json


@dataclass
class UserConfig:
    """用户配置"""
    
    # 基本信息
    organization: str = ""              # 汇报单位
    project_name: str = ""              # 项目名称
    project_title: str = ""             # 项目标题
    doc_type: str = ""                  # 文档类型
    
    # 主题配置
    theme_id: str = "consulting"        # 主题 ID
    
    # 颜色覆盖 (可选)
    color_primary: Optional[str] = None
    color_accent: Optional[str] = None
    color_background: Optional[str] = None
    
    # 内容配置
    target_pages: int = 25              # 目标页数
    content_depth: str = "normal"       # 内容深度: brief, normal, detailed
    keywords: List[str] = field(default_factory=list)  # 主题关键词
    
    # 页面配置
    include_cover: bool = True          # 生成封面
    include_agenda: bool = True         # 生成目录
    include_closing: bool = True        # 生成封底
    include_background: bool = True     # 在内容中体现主题背景
    
    # 输出配置
    output_pdf: bool = True             # 输出 PDF
    output_pptx: bool = True            # 输出 PPTX
    output_html: bool = True            # 输出 HTML
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserConfig':
        """从字典创建"""
        # 过滤掉不存在的字段
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
    def get_theme_overrides(self) -> Dict[str, Any]:
        """获取主题覆盖配置"""
        overrides = {}
        
        # 颜色覆盖
        colors = {}
        if self.color_primary:
            colors["primary"] = self.color_primary
        if self.color_accent:
            colors["accent"] = self.color_accent
        if self.color_background:
            colors["background"] = self.color_background
        
        if colors:
            overrides["colors"] = colors
        
        return overrides
    
    def get_prompt_context(self) -> Dict[str, Any]:
        """获取提示词上下文"""
        return {
            "organization": self.organization,
            "project_name": self.project_name,
            "project_title": self.project_title,
            "doc_type": self.doc_type,
            "keywords": self.keywords,
            "target_pages": self.target_pages,
            "content_depth": self.content_depth,
            "include_background": self.include_background,
        }
    
    def validate(self) -> List[str]:
        """验证配置，返回错误列表"""
        errors = []
        
        if self.target_pages < 5:
            errors.append("目标页数不能少于 5 页")
        if self.target_pages > 100:
            errors.append("目标页数不能超过 100 页")
        
        if self.content_depth not in ["brief", "normal", "detailed"]:
            errors.append("内容深度必须是 brief, normal, detailed 之一")
        
        # 验证颜色格式
        import re
        color_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')
        
        if self.color_primary and not color_pattern.match(self.color_primary):
            errors.append("主色调格式错误，应为 #RRGGBB")
        if self.color_accent and not color_pattern.match(self.color_accent):
            errors.append("强调色格式错误，应为 #RRGGBB")
        if self.color_background and not color_pattern.match(self.color_background):
            errors.append("背景色格式错误，应为 #RRGGBB")
        
        return errors


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".ai-pptx"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "user_config.json"
    
    def save_config(self, config: UserConfig, name: str = "default"):
        """保存配置"""
        configs = self._load_all_configs()
        configs[name] = config.to_dict()
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(configs, f, ensure_ascii=False, indent=2)
    
    def load_config(self, name: str = "default") -> Optional[UserConfig]:
        """加载配置"""
        configs = self._load_all_configs()
        if name in configs:
            return UserConfig.from_dict(configs[name])
        return None
    
    def list_configs(self) -> List[str]:
        """列出所有保存的配置"""
        configs = self._load_all_configs()
        return list(configs.keys())
    
    def delete_config(self, name: str) -> bool:
        """删除配置"""
        configs = self._load_all_configs()
        if name in configs:
            del configs[name]
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(configs, f, ensure_ascii=False, indent=2)
            return True
        return False
    
    def _load_all_configs(self) -> Dict[str, Any]:
        """加载所有配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}


# 预设配置模板
PRESET_CONFIGS = {
    "hetao": UserConfig(
        organization="深圳国家高技术产业创新中心",
        project_name="河套深港科技创新合作区",
        doc_type="河套深港科技创新合作区深圳园区创新体系建设综合咨询研究课题",
        theme_id="consulting",
        keywords=["河套合作区", "深港合作", "科技创新"],
        target_pages=30,
        content_depth="detailed",
    ),
    "annual_report": UserConfig(
        organization="",
        project_name="年度工作总结",
        doc_type="年度工作汇报",
        theme_id="annual_review",
        keywords=["年终总结", "工作成果", "未来规划"],
        target_pages=20,
        content_depth="normal",
    ),
    "company_pitch": UserConfig(
        organization="",
        project_name="公司介绍",
        doc_type="公司简介",
        theme_id="company_intro",
        keywords=["公司介绍", "产品服务", "团队优势"],
        target_pages=15,
        content_depth="brief",
    ),
    "academic": UserConfig(
        organization="",
        project_name="研究报告",
        doc_type="学术研究报告",
        theme_id="academic",
        keywords=["研究背景", "方法论", "研究结论"],
        target_pages=25,
        content_depth="detailed",
    ),
    "marketing": UserConfig(
        organization="",
        project_name="营销方案",
        doc_type="营销策划方案",
        theme_id="creative",
        keywords=["品牌推广", "营销策略", "创意方案"],
        target_pages=20,
        content_depth="normal",
    ),
}


def get_preset_config(preset_name: str) -> Optional[UserConfig]:
    """获取预设配置"""
    return PRESET_CONFIGS.get(preset_name)


def list_preset_configs() -> List[Dict[str, str]]:
    """列出所有预设配置"""
    return [
        {
            "id": name,
            "name": config.project_name,
            "theme": config.theme_id,
            "description": config.doc_type,
        }
        for name, config in PRESET_CONFIGS.items()
    ]
