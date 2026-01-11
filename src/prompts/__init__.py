"""
专业 Prompt 系统

基于顶级咨询公司方法论设计，融合：
- 麦肯锡金字塔原理
- BCG 结构化思维
- 贝恩 RAPID 决策框架
- 演示文稿设计最佳实践

核心理念：
1. 内容为王 - 结构清晰、逻辑严密、数据支撑
2. 一页一观点 - 每页只传达一个核心信息
3. 行动导向 - 标题即结论，内容即证据
4. 视觉服务内容 - 设计服务于信息传达
"""

from .prompt_engine import PromptEngine, create_prompt_engine
from .scenario_prompts import (
    SCENARIO_PROMPTS, 
    get_scenario_prompt, 
    get_scenario_info
)
from .methodology import (
    METHODOLOGIES, 
    REPORT_STRUCTURES,
    get_methodology_prompt
)
from .quality_checker import (
    QualityChecker,
    QualityIssue,
    check_content_quality,
    check_outline_quality
)

__all__ = [
    # Prompt 引擎
    'PromptEngine',
    'create_prompt_engine',
    
    # 场景 Prompt
    'SCENARIO_PROMPTS',
    'get_scenario_prompt',
    'get_scenario_info',
    
    # 方法论
    'METHODOLOGIES',
    'REPORT_STRUCTURES',
    'get_methodology_prompt',
    
    # 质量检查
    'QualityChecker',
    'QualityIssue',
    'check_content_quality',
    'check_outline_quality',
]
