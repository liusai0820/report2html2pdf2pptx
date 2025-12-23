"""
主题化 AI 客户端 - 支持主题系统的 AI 生成

功能:
1. 根据主题生成内容
2. 支持用户配置注入
3. 动态 CSS 生成
"""

import asyncio
from typing import Optional, Dict, Any
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
from themes import Theme, ThemeManager, get_theme
from themes.css_generator import generate_theme_css
from themes.prompt_generator import PromptGenerator

console = Console()


class ThemedAIClient:
    """主题化 AI 客户端"""
    
    def __init__(
        self,
        theme_id: str = "consulting",
        model: str = DEFAULT_MODEL,
        user_config: Optional[Dict[str, Any]] = None
    ):
        self.model = model
        self.user_config = user_config or {}
        
        # 加载主题
        self.theme_manager = ThemeManager()
        self.theme = self.theme_manager.get_theme(theme_id)
        if not self.theme:
            console.print(f"[yellow]⚠ 主题 '{theme_id}' 不存在，使用默认主题[/yellow]")
            self.theme = self.theme_manager.get_theme("consulting")
        
        # 应用用户配置
        if user_config:
            self.theme = self.theme_manager.apply_user_config(self.theme, user_config)
        
        # 初始化 OpenAI 客户端
        self.client = AsyncOpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            default_headers={
                "HTTP-Referer": "https://ppt.gwy.life",
                "X-Title": "SlideAI"
            }
        )
        
        # 初始化提示词生成器
        self.prompt_generator = PromptGenerator(self.theme, self.user_config)
        self.system_prompt = self.prompt_generator.generate_system_prompt()
        
        console.print(f"[green]✓[/green] 已加载主题: {self.theme.metadata.name}")
    
    def get_theme_css(self) -> str:
        """获取主题 CSS"""
        return generate_theme_css(self.theme)
    
    def get_theme_info(self) -> Dict[str, Any]:
        """获取主题信息"""
        return {
            "id": self.theme.metadata.id,
            "name": self.theme.metadata.name,
            "description": self.theme.metadata.description,
            "category": self.theme.metadata.category,
            "colors": {
                "primary": self.theme.colors.primary,
                "accent": self.theme.colors.accent,
            }
        }
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        retry_count: int = 0
    ) -> str:
        """基础生成函数（带重试机制）"""
        try:
            messages = []
            final_system_prompt = system_prompt if system_prompt else self.system_prompt
            
            if final_system_prompt:
                messages.append({"role": "system", "content": final_system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=TEMPERATURE,
                ),
                timeout=TIMEOUT_SECONDS
            )
            
            return response.choices[0].message.content.strip()
        
        except asyncio.TimeoutError:
            if retry_count < MAX_RETRIES:
                retry_count += 1
                wait_time = RETRY_DELAY * retry_count
                console.print(f"[yellow]⚠ 请求超时，{wait_time}秒后进行第{retry_count}次重试...[/yellow]")
                await asyncio.sleep(wait_time)
                return await self.generate(prompt, system_prompt, retry_count)
            else:
                console.print(f"[red]✗ 请求超时 ({TIMEOUT_SECONDS}秒)，已重试{MAX_RETRIES}次仍失败[/red]")
                raise
        except Exception as e:
            if retry_count < MAX_RETRIES and "timeout" in str(e).lower():
                retry_count += 1
                wait_time = RETRY_DELAY * retry_count
                console.print(f"[yellow]⚠ 请求失败，{wait_time}秒后进行第{retry_count}次重试...[/yellow]")
                await asyncio.sleep(wait_time)
                return await self.generate(prompt, system_prompt, retry_count)
            else:
                console.print(f"[red]✗ AI调用失败: {str(e)}[/red]")
                raise
    
    async def generate_template(self) -> str:
        """生成基础 HTML 模板"""
        css = self.get_theme_css()
        
        template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>演示文稿 - {self.theme.metadata.name}</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap');

{css}
    </style>
</head>
<body>
{{{{CONTENT_PLACEHOLDER}}}}
</body>
</html>
"""
        return template
    
    async def generate_page_content(
        self,
        page_num: int,
        total_pages: int,
        page_data: Dict[str, Any],
        source_material: str = ""
    ) -> str:
        """生成单页内容"""
        prompt = self.prompt_generator.generate_page_prompt(
            page_num, total_pages, page_data, source_material
        )
        
        html = await self.generate(prompt)
        html = self._clean_markdown(html)
        html = self._remove_header(html)
        return html
    
    def _clean_markdown(self, text: str) -> str:
        """清理 Markdown 代码块标记"""
        text = text.strip()
        if text.startswith('```html'):
            text = text[7:].strip()
        elif text.startswith('```'):
            text = text[3:].strip()
        if text.endswith('```'):
            text = text[:-3].strip()
        return text
    
    def _remove_header(self, html: str) -> str:
        """移除页眉元素"""
        import re
        html = re.sub(r'<header\s+class="slide-header"[^>]*>.*?</header>\s*', '', html, flags=re.DOTALL)
        html = re.sub(r'\.slide-header\s*\{[^}]*\}', '', html)
        return html


def create_themed_client(
    theme_id: str = "consulting",
    model: str = DEFAULT_MODEL,
    user_config: Optional[Dict[str, Any]] = None
) -> ThemedAIClient:
    """创建主题化 AI 客户端的便捷函数"""
    return ThemedAIClient(theme_id, model, user_config)


# 主题列表便捷函数
def list_available_themes():
    """列出所有可用主题"""
    manager = ThemeManager()
    return manager.list_themes()
