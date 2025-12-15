"""
核心模块 - AI 原生的统一架构

设计理念：
1. 单一真相源 - 所有配置汇聚到一个地方
2. 组合优于继承 - 通过组合不同能力构建系统
3. AI 驱动 - 让 AI 做决策，而不是硬编码规则
4. 上下文感知 - 所有信息都作为上下文传递给 AI

架构：
┌─────────────────────────────────────────────────────┐
│                    用户输入                          │
│  (文档 + 场景 + 主题 + 配置)                         │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│              ContextBuilder (上下文构建器)           │
│  - 收集所有信息                                      │
│  - 构建完整上下文                                    │
│  - 不做决策，只做信息整合                            │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│              AIOrchestrator (AI 编排器)              │
│  - 将上下文传递给 AI                                 │
│  - AI 自主决定如何生成                               │
│  - 最小化硬编码规则                                  │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│              OutputRenderer (输出渲染器)             │
│  - 将 AI 输出转换为最终格式                          │
│  - HTML / PDF / PPTX                                │
└─────────────────────────────────────────────────────┘
"""

from .context_builder import ContextBuilder, PresentationContext, build_context_from_config
from .ai_orchestrator import AIOrchestrator
from .output_renderer import OutputRenderer
from .generator import PresentationGenerator, generate_presentation

__all__ = [
    # 上下文
    'ContextBuilder',
    'PresentationContext',
    'build_context_from_config',
    
    # AI 编排
    'AIOrchestrator',
    
    # 输出渲染
    'OutputRenderer',
    
    # 统一生成器
    'PresentationGenerator',
    'generate_presentation',
]
