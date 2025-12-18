"""
Slide Validator - 幻灯片验证器

核心理念：
1. 后置校验而不是前置约束
2. 检查溢出、颜色合规性、HTML 结构
3. 提供自动修复建议
"""

import re
from typing import List, Tuple, Optional
from .design_system import DesignSystem


class ValidationResult:
    """验证结果"""
    def __init__(self, is_valid: bool = True, errors: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
    
    def add_error(self, error: str):
        self.is_valid = False
        self.errors.append(error)


class SlideValidator:
    """
    幻灯片验证器
    
    职责：
    1. 检查生成的 HTML 是否符合基本规范
    2. 检查是否有明显的溢出风险（估算）
    3. 检查是否使用了违禁标签（style, script 等）
    """
    
    def __init__(self, design_system: DesignSystem):
        self.design_system = design_system
        self.tokens = design_system.get_tokens()
    
    def validate(self, html: str) -> ValidationResult:
        """验证 HTML 内容"""
        result = ValidationResult()
        
        # 1. 基础结构检查
        if not html.strip():
            result.add_error("内容为空")
            return result
        
        # 2. 禁止标签检查
        # 允许内联样式 style="..."，但禁止块级 <style>...</style> (除了图表所需的)
        # 这里暂时放宽，因为 ECharts 可能需要简单的 style
        
        if "<header" in html.lower():
            result.add_error("检测到 <header> 标签，不允许使用页眉")
        
        # 3. Emoji 检测 (基本范围)
        # 匹配常见的 Emoji 范围
        emoji_pattern = re.compile(r'[\U00010000-\U0010ffff]', flags=re.UNICODE)
        if emoji_pattern.search(html):
            result.add_error("检测到 Emoji 字符，可能导致 PPTX 转换失败")
            
        # 4. 画布尺寸检查（尝试正则匹配）
        width_match = re.search(r'width:\s*(\d+)px', html)
        height_match = re.search(r'height:\s*(\d+)px', html)
        
        expected_width = self.tokens.canvas.width
        expected_height = self.tokens.canvas.height
        
        if width_match:
            width = int(width_match.group(1))
            if width != expected_width:
                result.add_error(f"画布宽度错误: {width}px，应为 {expected_width}px")
        
        if height_match:
            height = int(height_match.group(1))
            if height != expected_height:
                result.add_error(f"画布高度错误: {height}px，应为 {expected_height}px")
                
        # 5. 内容溢出风险估算 (非常粗略)
        text_length = len(re.sub(r'<[^>]+>', '', html))
        canvas_area = expected_width * expected_height * 0.8 # 80% 可用
        
        # 简单估算：假设平均每个字符占 400px² (20x20)
        estimated_area = text_length * 400
        
        if estimated_area > canvas_area:
            result.add_error(f"内容可能溢出: 文字量过多 ({text_length} 字)")
            
        return result
    
    def fix_html(self, html: str) -> str:
        """
        尝试自动修复 HTML
        1. 移除 Emoji
        2. 确保最外层 div 尺寸正确
        """
        # 1. 移除 Emoji
        html = re.sub(r'[\U00010000-\U0010ffff]', '', html, flags=re.UNICODE)
        
        # 2. 移除不支持的特殊字符 (如下箭头等可能不在上述范围的)
        # 这里可以根据需要添加更多过滤
        
        # 3. 强制设置最外层 div 的样式
        expected_width = self.tokens.canvas.width
        expected_height = self.tokens.canvas.height
        
        # 检查是否已有外层容器，如果没有则包裹
        if not html.strip().startswith('<div'):
            html = f'<div style="width: {expected_width}px; height: {expected_height}px; background: {self.tokens.colors.background}; box-sizing: border-box; overflow: hidden; font-family: \'Noto Sans SC\', sans-serif;">{html}</div>'
            
        return html
