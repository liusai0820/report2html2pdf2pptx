"""
Prompt 模块

@pos: 原子化的 Prompt 系统，按功能分离到独立文件

导出：
- SCENARIO_PROMPTS: 场景专属 Prompt 配置
- SCENARIO_ALIASES: 场景别名映射
- get_scenario_prompts: 获取场景专有 Prompt
- build_speech_prompt: 构建演讲稿 Prompt
- get_detail_config: 获取详略配置
"""

from .scenario_prompts import (
    SCENARIO_PROMPTS,
    SCENARIO_ALIASES,
    get_scenario_prompts
)

from .speech_prompt import (
    build_speech_prompt,
    get_detail_config
)

__all__ = [
    "SCENARIO_PROMPTS",
    "SCENARIO_ALIASES",
    "get_scenario_prompts",
    "build_speech_prompt",
    "get_detail_config",
]
