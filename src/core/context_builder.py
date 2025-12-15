"""
上下文构建器 - 将所有信息整合为 AI 可理解的上下文

核心理念：
1. 不做决策，只做信息整合
2. 所有信息都是上下文的一部分
3. AI 根据完整上下文自主决策

这是 AI 原生设计的关键：
- 传统方式：代码决定用哪个模板、哪种风格、哪些规则
- AI 原生：把所有信息给 AI，让 AI 自己决定
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from pathlib import Path
import json

from themes.theme_manager import Theme


@dataclass
class PresentationContext:
    """
    演示文稿完整上下文
    
    这个类包含生成一份演示文稿所需的所有信息。
    不是配置，而是上下文 —— AI 会根据这些信息自主决策。
    """
    
    # ========== 主题对象 ==========
    theme: Optional[Theme] = None           # 加载后的主题对象
    
    # ========== 源文档 ==========
    document_content: str = ""              # 原始文档内容
    document_type: str = ""                 # 文档类型 (docx, md, json)
    document_name: str = ""                 # 文档名称
    
    # ========== 场景信息 ==========
    scenario: str = "consulting"            # 场景类型
    scenario_description: str = ""          # 场景描述（让 AI 理解）
    
    # ========== 受众信息 ==========
    audience: str = ""                      # 目标受众
    audience_expectations: str = ""         # 受众期望
    presentation_occasion: str = ""         # 汇报场合
    
    # ========== 内容要求 ==========
    core_message: str = ""                  # 核心信息/主旨
    key_points: List[str] = field(default_factory=list)  # 必须包含的要点
    constraints: List[str] = field(default_factory=list) # 约束条件
    
    # ========== 组织信息 ==========
    organization: str = ""                  # 汇报单位
    project_name: str = ""                  # 项目名称
    author: str = ""                        # 作者
    date: str = ""                          # 日期
    
    # ========== 风格偏好 ==========
    tone: str = ""                          # 语调 (专业/轻松/学术/创意)
    visual_style: str = ""                  # 视觉风格描述
    color_preference: str = ""              # 颜色偏好
    
    # ========== 结构要求 ==========
    target_pages: int = 25                  # 目标页数
    content_depth: str = "normal"           # 内容深度
    must_include_sections: List[str] = field(default_factory=list)  # 必须包含的章节
    
    # ========== 质量标准 ==========
    quality_requirements: List[str] = field(default_factory=list)  # 质量要求
    
    # ========== 参考资料 ==========
    reference_materials: List[str] = field(default_factory=list)  # 参考资料
    examples: List[str] = field(default_factory=list)  # 示例
    
    def to_prompt_context(self) -> str:
        """
        将上下文转换为 AI 可理解的自然语言描述
        
        这是关键：不是给 AI 一堆参数，而是给 AI 一段完整的背景描述
        """
        parts = []
        
        # 任务背景
        parts.append("# 任务背景\n")
        parts.append(f"你需要帮助制作一份演示文稿。\n")
        
        if self.scenario_description:
            parts.append(f"场景：{self.scenario_description}\n")
        
        if self.audience:
            parts.append(f"受众：{self.audience}\n")
        
        if self.audience_expectations:
            parts.append(f"受众期望：{self.audience_expectations}\n")
        
        if self.presentation_occasion:
            parts.append(f"汇报场合：{self.presentation_occasion}\n")
        
        # 核心信息
        if self.core_message:
            parts.append(f"\n# 核心信息\n{self.core_message}\n")
        
        # 组织信息
        if self.organization or self.project_name:
            parts.append("\n# 项目信息\n")
            if self.organization:
                parts.append(f"- 汇报单位：{self.organization}\n")
            if self.project_name:
                parts.append(f"- 项目名称：{self.project_name}\n")
            if self.date:
                parts.append(f"- 日期：{self.date}\n")
        
        # 内容要求
        if self.key_points:
            parts.append("\n# 必须包含的要点\n")
            for point in self.key_points:
                parts.append(f"- {point}\n")
        
        # 风格要求
        if self.tone or self.visual_style:
            parts.append("\n# 风格要求\n")
            if self.tone:
                parts.append(f"- 语调：{self.tone}\n")
            if self.visual_style:
                parts.append(f"- 视觉风格：{self.visual_style}\n")
            if self.color_preference:
                parts.append(f"- 颜色偏好：{self.color_preference}\n")
        
        # 结构要求
        parts.append(f"\n# 结构要求\n")
        parts.append(f"- 目标页数：约 {self.target_pages} 页\n")
        parts.append(f"- 内容深度：{self._depth_description()}\n")
        
        if self.must_include_sections:
            parts.append("- 必须包含的章节：\n")
            for section in self.must_include_sections:
                parts.append(f"  - {section}\n")
        
        # 约束条件
        if self.constraints:
            parts.append("\n# 约束条件\n")
            for constraint in self.constraints:
                parts.append(f"- {constraint}\n")
        
        # 质量要求
        if self.quality_requirements:
            parts.append("\n# 质量要求\n")
            for req in self.quality_requirements:
                parts.append(f"- {req}\n")
        
        # 源文档
        if self.document_content:
            parts.append(f"\n# 源文档内容\n")
            parts.append(f"以下是需要转换为演示文稿的原始内容：\n\n")
            parts.append(self.document_content[:15000])  # 限制长度
            if len(self.document_content) > 15000:
                parts.append("\n\n[文档内容过长，已截断...]")
        
        return "".join(parts)
    
    def _depth_description(self) -> str:
        """内容深度描述"""
        descriptions = {
            "brief": "简洁版 - 突出重点，精简内容，适合快速汇报",
            "normal": "标准版 - 平衡深度和广度，适合正式汇报",
            "detailed": "详细版 - 深入分析，充分论证，适合深度研讨"
        }
        return descriptions.get(self.content_depth, self.content_depth)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "document_content": self.document_content,
            "document_type": self.document_type,
            "document_name": self.document_name,
            "scenario": self.scenario,
            "scenario_description": self.scenario_description,
            "audience": self.audience,
            "audience_expectations": self.audience_expectations,
            "presentation_occasion": self.presentation_occasion,
            "core_message": self.core_message,
            "key_points": self.key_points,
            "constraints": self.constraints,
            "organization": self.organization,
            "project_name": self.project_name,
            "author": self.author,
            "date": self.date,
            "tone": self.tone,
            "visual_style": self.visual_style,
            "color_preference": self.color_preference,
            "target_pages": self.target_pages,
            "content_depth": self.content_depth,
            "must_include_sections": self.must_include_sections,
            "quality_requirements": self.quality_requirements,
        }


class ContextBuilder:
    """
    上下文构建器
    
    负责从各种来源收集信息，构建完整的 PresentationContext
    """
    
    def __init__(self):
        self.context = PresentationContext()
    
    def from_document(self, file_path: str) -> 'ContextBuilder':
        """从文档加载内容"""
        from document_parser import DocumentParser
        
        path = Path(file_path)
        self.context.document_name = path.stem
        self.context.document_type = path.suffix.lstrip('.')
        
        doc_data = DocumentParser.load_document(file_path)
        
        if 'full_content' in doc_data:
            self.context.document_content = doc_data['full_content']
        elif 'pages' in doc_data:
            # 将结构化内容转换为文本
            content_parts = []
            for page in doc_data['pages']:
                content_parts.append(f"## {page.get('title', '')}")
                content_parts.append(page.get('content', ''))
            self.context.document_content = "\n\n".join(content_parts)
        
        if 'title' in doc_data and doc_data['title']:
            self.context.project_name = doc_data['title']
        else:
            # 如果文档中没有提取到标题，使用文件名作为默认标题
            self.context.project_name = self.context.document_name
        
        return self
    
    def with_scenario(self, scenario: str) -> 'ContextBuilder':
        """设置场景"""
        self.context.scenario = scenario
        
        # 场景描述 - 让 AI 理解这是什么场景
        scenario_descriptions = {
            "consulting": """
这是一份咨询研究报告，需要呈现给政府领导或企业高管。
受众特点：时间有限，需要快速抓住重点，关注数据和可执行建议。
风格要求：专业、严谨、数据驱动、结论先行。
典型结构：执行摘要 → 背景分析 → 问题诊断 → 解决方案 → 实施计划。
""",
            "annual_review": """
这是一份年终述职/工作总结报告，需要向上级领导汇报。
受众特点：关注成果和价值，评估能力和潜力。
风格要求：自信但不自大，用数据说话，突出个人贡献。
典型结构：年度总结 → 目标回顾 → 成果展示 → 经验教训 → 明年规划。
""",
            "company_intro": """
这是一份公司/项目介绍，需要向潜在客户、投资人或合作伙伴展示。
受众特点：需要快速了解你是谁，关注能带来什么价值。
风格要求：专业自信，突出差异化，强调客户价值。
典型结构：一句话定位 → 公司概览 → 核心业务 → 优势案例 → 合作机会。
""",
            "academic": """
这是一份学术研究报告或论文答辩，需要向学术同行或评审专家展示。
受众特点：关注研究的严谨性，评估学术贡献。
风格要求：严谨准确，客观中立，术语规范。
典型结构：研究背景 → 文献综述 → 研究方法 → 研究发现 → 讨论结论。
""",
            "creative": """
这是一份创意提案或营销方案，需要打动客户或消费者。
受众特点：需要被打动，关注创意和效果。
风格要求：有感染力，有画面感，有记忆点。
典型结构：引爆点 → 洞察 → 创意概念 → 执行方案 → 效果预估。
""",
            "government": """
这是一份政府公文或政策汇报，需要向政府领导或上级部门汇报。
受众特点：关注政策合规性，重视数据准确性。
风格要求：规范严谨，政治正确，措施具体。
典型结构：背景意义 → 现状分析 → 问题诊断 → 对策建议 → 保障措施。
"""
        }
        
        self.context.scenario_description = scenario_descriptions.get(
            scenario, scenario_descriptions["consulting"]
        )
        
        # 加载主题
        try:
            from themes.theme_manager import ThemeManager
            theme_manager = ThemeManager()
            theme = theme_manager.get_theme(scenario)
            if theme:
                self.context.theme = theme
        except Exception as e:
            # 在 CLI 工具中，打印警告而不是中断
            print(f"Warning: Could not load theme for scenario '{scenario}'. Error: {e}")

        return self
    
    def with_audience(self, audience: str, expectations: str = "") -> 'ContextBuilder':
        """设置受众信息"""
        self.context.audience = audience
        self.context.audience_expectations = expectations
        return self
    
    def with_organization(self, org: str, project: str = "", date: str = "") -> 'ContextBuilder':
        """设置组织信息"""
        self.context.organization = org
        if project:
            self.context.project_name = project
        if date:
            self.context.date = date
        return self
    
    def with_style(self, tone: str = "", visual: str = "", color: str = "") -> 'ContextBuilder':
        """设置风格偏好"""
        if tone:
            self.context.tone = tone
        if visual:
            self.context.visual_style = visual
        if color:
            self.context.color_preference = color
        return self
    
    def with_structure(self, pages: int = 25, depth: str = "normal") -> 'ContextBuilder':
        """设置结构要求"""
        self.context.target_pages = pages
        self.context.content_depth = depth
        return self
    
    def with_constraints(self, constraints: List[str]) -> 'ContextBuilder':
        """设置约束条件"""
        self.context.constraints = constraints
        return self
    
    def with_quality_requirements(self, requirements: List[str]) -> 'ContextBuilder':
        """设置质量要求"""
        self.context.quality_requirements = requirements
        return self
    
    def add_default_quality_requirements(self) -> 'ContextBuilder':
        """添加默认质量要求"""
        self.context.quality_requirements = [
            "标题必须是结论，不是主题（如'市场规模达500亿'而非'市场分析'）",
            "每页只传达一个核心观点",
            "所有数据必须来自源文档，禁止编造",
            "每页都要有 So What（这意味着什么/我们应该怎么做）",
            "使用数据和事实支撑观点，避免空洞表述",
            "语言简洁有力，删除所有废话",
        ]
        return self
    
    def add_default_constraints(self) -> 'ContextBuilder':
        """添加默认约束"""
        self.context.constraints = [
            "禁止编造数据或案例",
            "禁止使用 Emoji",
            "禁止使用英文装饰词（如 Company Confidential）",
            "正文字号不小于 18px",
        ]
        return self
    
    def build(self) -> PresentationContext:
        """构建最终上下文"""
        # 添加默认值
        if not self.context.quality_requirements:
            self.add_default_quality_requirements()
        
        if not self.context.constraints:
            self.add_default_constraints()
        
        if not self.context.date:
            from datetime import datetime
            self.context.date = datetime.now().strftime("%Y年%m月")
        
        return self.context


def build_context_from_config(
    document_path: str,
    scenario: str = "consulting",
    user_config: Optional[Dict[str, Any]] = None
) -> PresentationContext:
    """
    便捷函数：从配置构建上下文
    """
    config = user_config or {}
    
    builder = ContextBuilder()
    builder.from_document(document_path)
    builder.with_scenario(scenario)
    
    if config.get("organization"):
        builder.with_organization(
            config["organization"],
            config.get("project_name", ""),
            config.get("date", "")
        )
    
    if config.get("target_pages"):
        builder.with_structure(
            config["target_pages"],
            config.get("content_depth", "normal")
        )
    
    if config.get("tone") or config.get("visual_style"):
        builder.with_style(
            config.get("tone", ""),
            config.get("visual_style", ""),
            config.get("color_preference", "")
        )
    
    return builder.build()
