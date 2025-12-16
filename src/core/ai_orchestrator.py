"""
AI 编排器 - AI 原生的核心引擎

核心理念：
1. 最小化硬编码 - 让 AI 自己决定
2. 上下文驱动 - 所有信息作为上下文传递
3. 单一职责 - 只负责与 AI 交互
"""

import asyncio
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from rich.console import Console

from config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    DEFAULT_MODEL,
    TIMEOUT_SECONDS,
    MAX_RETRIES,
    RETRY_DELAY,
    TEMPERATURE,
)
from .context_builder import PresentationContext
from prompts.prompt_engine import create_prompt_engine

console = Console()


# 核心系统提示词 - 这是唯一的"硬编码"，但它是元级别的指导
MASTER_SYSTEM_PROMPT = """
你是一位世界级的演示文稿设计专家，融合了麦肯锡的结构化思维、IDEO的设计思维、TED的演讲艺术。

## 你的核心能力

1. **金字塔思维**：结论先行，以上统下，归类分组，逻辑递进
2. **洞察提炼**：从海量信息中提炼关键洞察
3. **故事构建**：用 SCQA 框架构建有说服力的叙事
4. **视觉表达**：让复杂信息简单易懂

## 你的工作原则

### 内容原则
1. **一页一观点**：每页只传达一个核心信息
2. **标题即结论**：标题不是主题，是这页的核心观点
3. **数据说话**：用数字代替形容词，用事实代替观点
4. **So What**：每页都要回答"这意味着什么"

### 质量红线
1. **禁止编造**：没有的数据不写，没有的案例不编
2. **禁止废话**：删除所有没有信息量的表述
3. **禁止跳跃**：每个结论都要有依据
4. **禁止出现"So What"字样**：底部结论框直接写结论性语句，不要写"So What"这种提示词

### 输出规范
1. 使用预定义的 CSS 类名
2. 不生成 <style> 标签
3. 不生成 <header> 标签
4. 结构清晰，语义化

## 预定义 CSS 类名

- `.slide-container` - 幻灯片容器
- `.cover-slide` - 封面页
- `.section-slide` - 章节过场页
- `.content-area` - 内容区域
- `.page-title` - 页面标题（36px，结论式）
- `.sub-head` - 子标题（24px）
- `.big-list` - 大号列表（20px）
- `.data-card` - 数据卡片
- `.data-val` - 数据值（大号数字）
- `.data-lbl` - 数据标签
- `.bottom-box` - 底部结论框（So What）
- `.clean-table` - 表格
- `.chart-container` - 图表容器

## 你的任务

根据用户提供的上下文，生成高质量的演示文稿内容。
你会收到完整的背景信息，请根据这些信息自主决定最佳的呈现方式。
"""


class AIOrchestrator:
    """
    AI 编排器
    
    职责：
    1. 接收上下文
    2. 与 AI 交互
    3. 返回结果
    
    不做：
    1. 不做业务逻辑判断
    2. 不做模板选择
    3. 不做硬编码规则
    """
    
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.client = AsyncOpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
        )
    
    async def generate_outline(self, context: PresentationContext) -> List[Dict[str, Any]]:
        """
        生成大纲
        
        让 AI 根据完整上下文自主决定：
        - 分几个章节
        - 每章几页
        - 每页讲什么
        """
        # 使用 PromptEngine 生成大纲提示词
        # 提取主题配置
        theme_config = {}
        if context.theme:
            theme_config = context.theme.to_dict()
            
        engine = create_prompt_engine(
            scenario=context.scenario,
            theme_config=theme_config
        )
        
        # 使用 generate_system_prompt 作为系统提示词的一部分（或者整合）
        # 这里为了保持架构简单，我们直接用 generate_outline_prompt
        prompt = engine.generate_outline_prompt(
            content=context.to_prompt_context(),
            target_pages=context.target_pages
        )
        
        response = await self._generate(prompt)
        return self._parse_outline(response)
    
    async def generate_page(
        self,
        context: PresentationContext,
        page_info: Dict[str, Any],
        page_num: int,
        total_pages: int
    ) -> str:
        """
        生成单页内容
        
        让 AI 根据上下文和页面信息自主决定：
        - 用什么布局
        - 放什么内容
        - 怎么呈现
        """
        # 准备配置
        from datetime import datetime
        current_date = datetime.now().strftime("%Y年%m月")  # 如 "2025年12月"
        
        user_config = {
            "organization": context.organization,
            "project_name": context.project_name,
            "target_pages": context.target_pages,
            "content_depth": context.content_depth,
            "date": current_date  # 动态日期
        }
        
        theme_config = {}
        if context.theme:
            theme_config = context.theme.to_dict()
            
        # 创建 Prompt 引擎
        engine = create_prompt_engine(
            scenario=context.scenario,
            user_config=user_config,
            theme_config=theme_config
        )
        
        # 生成提示词
        # 注意：这里我们不再需要手动判断 page_type，PromptEngine 会处理
        prompt = engine.generate_page_prompt(
            page_num=page_num,
            total_pages=total_pages,
            page_data=page_info,
            source_material=context.document_content[:2000] # 提供一部分原始内容作为参考
        )
        
        html = await self._generate(prompt)
        return self._clean_html(html)
    
    async def _generate(self, prompt: str, retry_count: int = 0) -> str:
        """调用 AI 生成"""
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": MASTER_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=TEMPERATURE,
                ),
                timeout=TIMEOUT_SECONDS
            )
            
            # 检查响应是否有效
            if not response or not response.choices:
                raise ValueError("API 返回空响应")
            
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("API 返回内容为空")
            
            return content.strip()
        
        except asyncio.TimeoutError:
            if retry_count < MAX_RETRIES:
                wait_time = RETRY_DELAY * (retry_count + 1)
                console.print(f"[yellow]⚠ 超时，{wait_time}秒后重试...[/yellow]")
                await asyncio.sleep(wait_time)
                return await self._generate(prompt, retry_count + 1)
            raise
        
        except Exception as e:
            error_msg = str(e)
            if retry_count < MAX_RETRIES:
                wait_time = RETRY_DELAY * (retry_count + 1)
                console.print(f"[yellow]⚠ 失败: {error_msg[:100]}，{wait_time}秒后重试...[/yellow]")
                await asyncio.sleep(wait_time)
                return await self._generate(prompt, retry_count + 1)
            console.print(f"[red]✗ 最终失败: {error_msg}[/red]")
            raise
    
    def _parse_outline(self, text: str) -> List[Dict[str, Any]]:
        """解析大纲"""
        pages = []
        # 系统自动生成的类型，AI 不应该生成
        auto_types = {'COVER', 'AGENDA', 'CLOSING'}
        
        for line in text.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split('|')
            if len(parts) >= 2:
                page_type = parts[0].strip().upper()
                
                # 过滤掉 AI 可能错误生成的封面/目录/封底
                if page_type in auto_types:
                    continue
                
                # 只接受 SECTION 和 CONTENT 类型
                if page_type not in {'SECTION', 'CONTENT'}:
                    page_type = 'CONTENT'
                
                pages.append({
                    'type': page_type,
                    'title': parts[1].strip(),
                    'content': parts[2].strip() if len(parts) > 2 else ''
                })
        return pages
    
    def _clean_html(self, html: str) -> str:
        """清理 HTML 并修复标点符号"""
        import re
        html = html.strip()
        
        # 移除 markdown 代码块标记
        if html.startswith('```html'):
            html = html[7:]
        elif html.startswith('```'):
            html = html[3:]
        if html.endswith('```'):
            html = html[:-3]
        
        # 移除 AI 可能输出的多余内容（在 HTML 之前的解释文字）
        # 找到第一个 <div 或 <main 标签的位置
        first_tag_match = re.search(r'<(div|main|section)\s', html, re.IGNORECASE)
        if first_tag_match and first_tag_match.start() > 0:
            # 移除 HTML 标签之前的所有内容
            html = html[first_tag_match.start():]
        
        # 移除 HTML 之后的多余内容（在最后一个 </div> 之后）
        last_div_match = list(re.finditer(r'</div>\s*$', html, re.IGNORECASE))
        if last_div_match:
            html = html[:last_div_match[-1].end()]
        
        # 移除 style 和 header 标签
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<header[^>]*>.*?</header>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # 修复中文标点符号（在中文内容中）
        html = self._fix_chinese_punctuation(html)
        
        return html.strip()
    
    def _fix_chinese_punctuation(self, html: str) -> str:
        """修复中文标点符号
        
        将中文内容中的英文标点符号替换为中文标点符号
        注意：不影响 HTML 标签和属性中的引号
        """
        import re
        
        # 分离 HTML 标签和文本内容
        parts = []
        last_end = 0
        
        # 匹配所有 HTML 标签
        for match in re.finditer(r'<[^>]+>', html):
            # 添加标签前的文本（需要处理标点）
            if match.start() > last_end:
                text = html[last_end:match.start()]
                text = self._convert_punctuation_in_text(text)
                parts.append(text)
            
            # 添加标签本身（不处理）
            parts.append(match.group())
            last_end = match.end()
        
        # 添加最后一段文本
        if last_end < len(html):
            text = html[last_end:]
            text = self._convert_punctuation_in_text(text)
            parts.append(text)
        
        return ''.join(parts)
    
    def _convert_punctuation_in_text(self, text: str) -> str:
        """转换文本中的标点符号（仅处理包含中文的文本）"""
        import re
        
        # 如果文本中没有中文字符，不处理
        if not re.search(r'[\u4e00-\u9fff]', text):
            return text
        
        # 转换标点符号
        # 1. 英文引号 -> 中文引号（成对转换）
        # 使用状态机来正确配对引号
        result = []
        in_quote = False
        i = 0
        while i < len(text):
            if text[i] == '"':
                if not in_quote:
                    result.append('"')
                    in_quote = True
                else:
                    result.append('"')
                    in_quote = False
            else:
                result.append(text[i])
            i += 1
        
        text = ''.join(result)
        
        # 2. 其他标点符号（只在中文上下文中转换）
        # 逗号：在中文字符或百分号附近的逗号
        text = re.sub(r'([\u4e00-\u9fff%]),', r'\1，', text)
        text = re.sub(r',([\u4e00-\u9fff])', r'，\1', text)
        
        # 句号：在中文字符后的句号
        text = re.sub(r'([\u4e00-\u9fff])\.(?!\d)', r'\1。', text)
        
        # 冒号：在中文字符附近的冒号
        text = re.sub(r'([\u4e00-\u9fff]):', r'\1：', text)
        text = re.sub(r':([\u4e00-\u9fff])', r'：\1', text)
        
        # 分号：在中文字符附近的分号
        text = re.sub(r'([\u4e00-\u9fff]);', r'\1；', text)
        text = re.sub(r';([\u4e00-\u9fff])', r'；\1', text)
        
        # 问号和感叹号
        text = re.sub(r'([\u4e00-\u9fff])\?', r'\1？', text)
        text = re.sub(r'([\u4e00-\u9fff])!', r'\1！', text)
        
        return text
