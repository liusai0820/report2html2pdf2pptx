"""
AI Presentation Generator v2 - AI 原生设计架构

核心理念：
1. Design System Token - 只约束设计系统，不约束布局
2. 端到端 AI 设计 - 让 AI 自主决定每页的视觉呈现  
3. 内联样式 - AI 生成完整的 HTML + 内联 CSS
4. 验证器 - 后置校验防溢出，而非前置约束扼杀创意

架构概览：
┌──────────────────────────────────────────────────────┐
│                    PresentationEngine                 │
│  (统一入口，协调所有模块)                              │
├──────────────────────────────────────────────────────┤
│                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ DesignSystem│  │  AIDesigner │  │  Validator  │   │
│  │  (Token)    │  │  (核心引擎)  │  │  (校验器)   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ DocParser   │  │ Renderer    │  │ Exporter    │   │
│  │ (文档解析)   │  │ (渲染器)    │  │ (导出器)    │   │
│  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                                       │
└──────────────────────────────────────────────────────┘
"""

from .design_system import DesignSystem, DesignTokens
from .ai_designer import AIDesigner
from .validator import SlideValidator
from .engine import PresentationEngine

__all__ = [
    'DesignSystem',
    'DesignTokens', 
    'AIDesigner',
    'SlideValidator',
    'PresentationEngine',
]
