"""
图像生成模块 - 支持 AI 生成和 Unsplash 图库

支持两种图像来源：
1. Nano Banana Pro (Gemini 3 Pro Image) - 通过 OpenRouter API
2. Unsplash - 高质量免费图库

用于封面、章节页、结尾页的背景图生成
"""

import os
import httpx
import base64
import asyncio
import json
from pathlib import Path
from typing import Optional, Literal
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# 确保环境变量已加载
def _ensure_env_loaded():
    """确保从 config/.env 加载了环境变量"""
    try:
        from dotenv import load_dotenv
        config_dir = Path(__file__).parent.parent.parent / "config"
        env_path = config_dir / ".env"
        if env_path.exists():
            load_dotenv(env_path, override=True)  # 强制覆盖
    except Exception as e:
        logger.warning(f"Failed to load .env: {e}")

_ensure_env_loaded()


@dataclass
class GeneratedImage:
    """生成的图像结果"""
    url: str  # 图片 URL 或 data URL
    source: str  # 'ai' | 'unsplash'
    prompt: str  # 生成/搜索关键词
    width: int = 1280
    height: int = 720


class ImageGenerator:
    """图像生成器 - 支持 AI 生成和 Unsplash"""
    
    def __init__(
        self,
        openrouter_api_key: Optional[str] = None,
        unsplash_api_key: Optional[str] = None,
        openrouter_base_url: str = "https://openrouter.ai/api/v1",
        image_model: str = "google/gemini-3-pro-image-preview"  # Nano Banana Pro 正确模型名称
    ):
        # 确保环境变量已加载
        _ensure_env_loaded()
        
        self.openrouter_api_key = openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
        self.unsplash_api_key = unsplash_api_key or os.getenv("UNSPLASH_API_KEY")
        self.openrouter_base_url = openrouter_base_url
        self.image_model = image_model
        
        # 调试日志
        if self.unsplash_api_key:
            logger.info(f"Unsplash API key loaded: {self.unsplash_api_key[:8]}...")
        else:
            logger.warning("Unsplash API key not configured")
        
    async def generate_cover_image(
        self,
        title: str,
        scenario: str,
        source: Literal["ai", "unsplash"] = "unsplash"
    ) -> Optional[GeneratedImage]:
        """生成封面背景图"""
        
        # 根据场景生成合适的图像描述
        prompt = self._build_image_prompt(title, scenario, "cover")
        
        if source == "ai":
            return await self._generate_ai_image(prompt)
        else:
            return await self._fetch_unsplash_image(prompt)
    
    async def generate_section_image(
        self,
        section_title: str,
        scenario: str,
        source: Literal["ai", "unsplash"] = "unsplash"
    ) -> Optional[GeneratedImage]:
        """生成章节页背景图"""
        
        prompt = self._build_image_prompt(section_title, scenario, "section")
        
        if source == "ai":
            return await self._generate_ai_image(prompt)
        else:
            return await self._fetch_unsplash_image(prompt)
    
    async def generate_closing_image(
        self,
        organization: str,
        scenario: str,
        source: Literal["ai", "unsplash"] = "unsplash"
    ) -> Optional[GeneratedImage]:
        """生成结尾页背景图"""
        
        prompt = self._build_image_prompt(organization, scenario, "closing")
        
        if source == "ai":
            return await self._generate_ai_image(prompt)
        else:
            return await self._fetch_unsplash_image(prompt)
    
    def _build_image_prompt(self, context: str, scenario: str, page_type: str) -> str:
        """根据上下文构建图像生成 prompt - 针对 Nano Banana Pro 优化"""
        
        # 场景到专业术语的映射（更精确的描述）
        scenario_keywords = {
            "consulting": "corporate boardroom, business strategy, executive presentation, professional consulting",
            "annual_review": "annual celebration, corporate success, achievement award ceremony, year-end milestone",
            "tech_pitch": "futuristic technology, innovation hub, silicon valley startup, cutting-edge digital",
            "academic": "university campus, academic research, scholarly study, knowledge discovery",
            "government": "civic architecture, government building, public policy, institutional governance",
            "company_intro": "modern corporate headquarters, professional team collaboration, business excellence",
        }
        
        # 页面类型对应的场景描述
        page_descriptions = {
            "cover": "This is a COVER SLIDE background. Create a wide, cinematic hero image that establishes the theme.",
            "section": "This is a SECTION DIVIDER background. Create a subtle, elegant abstract background.",
            "closing": "This is a THANK YOU slide background. Create an inspiring, warm, professional closing image."
        }
        
        keywords = scenario_keywords.get(scenario, "professional business corporate")
        page_desc = page_descriptions.get(page_type, "professional presentation background")
        
        # 构建详细的 prompt
        prompt = f"""Create a high-quality professional background image for a business presentation slide.

TOPIC/CONTEXT: {context}
STYLE: {keywords}
PURPOSE: {page_desc}

REQUIREMENTS:
- Aspect ratio: 16:9 (widescreen)
- Style: Modern, clean, minimalist with depth
- Color palette: Sophisticated, professional colors
- NO TEXT in the image
- Suitable for dark text overlay (leave some areas for text)
- High resolution, photorealistic or elegant abstract
- Professional, premium aesthetic

Generate a stunning, visually striking image that matches this theme perfectly."""
        
        return prompt
    
    async def _generate_ai_image(self, prompt: str) -> Optional[GeneratedImage]:
        """使用 OpenRouter + Gemini (Nano Banana) 生成图像"""
        
        if not self.openrouter_api_key:
            logger.warning("OpenRouter API key not set, falling back to Unsplash")
            return await self._fetch_unsplash_image(prompt)
        
        try:
            logger.info(f"Generating AI image with model: {self.image_model}")
            logger.debug(f"Prompt: {prompt[:200]}...")
            
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    f"{self.openrouter_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://slidecraft.ai",
                        "X-Title": "SlideCraft AI Image Generator"
                    },
                    json={
                        "model": self.image_model,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "modalities": ["image", "text"],  # 必须包含 image
                        "stream": False,
                        "max_tokens": 4096,
                        # 图像配置 - 16:9 宽屏
                        "image_config": {
                            "aspect_ratio": "16:9"
                        }
                    }
                )
                
                if response.status_code != 200:
                    error_text = response.text[:500]
                    logger.error(f"OpenRouter image generation failed: {response.status_code} - {error_text}")
                    return await self._fetch_unsplash_image(prompt)
                
                result = response.json()
                logger.debug(f"AI response: {json.dumps(result, ensure_ascii=False)[:500]}")
                
                # 检查是否有错误
                choices = result.get("choices", [])
                if choices and "error" in choices[0]:
                    error_info = choices[0]["error"]
                    logger.error(f"API error: {error_info.get('message', 'Unknown error')}")
                    return await self._fetch_unsplash_image(prompt)
                
                # 解析响应，提取图像
                message = choices[0].get("message", {}) if choices else {}
                
                # 官方文档：图像在 message["images"] 字段中
                images = message.get("images", [])
                if images:
                    for image in images:
                        image_url = image.get("image_url", {}).get("url", "")
                        if image_url:
                            logger.info(f"AI image generated successfully: {image_url[:50]}...")
                            return GeneratedImage(
                                url=image_url,
                                source="ai",
                                prompt=prompt
                            )
                
                # 备用解析：检查 content 是否为列表格式（部分模型可能用这种格式）
                content = message.get("content", "")
                if isinstance(content, list):
                    for part in content:
                        if part.get("type") == "image_url":
                            image_url = part.get("image_url", {}).get("url", "")
                            if image_url:
                                logger.info(f"AI image from content: {image_url[:50]}...")
                                return GeneratedImage(
                                    url=image_url,
                                    source="ai",
                                    prompt=prompt
                                )
                
                # 如果 content 是字符串，可能只返回了文本
                if isinstance(content, str) and content:
                    logger.warning(f"AI returned text instead of image: {content[:100]}...")
                
                # 如果没有图像，回退到 Unsplash
                logger.warning("No image in AI response, falling back to Unsplash")
                return await self._fetch_unsplash_image(prompt)
                
        except Exception as e:
            logger.error(f"AI image generation error: {e}")
            import traceback
            traceback.print_exc()
            return await self._fetch_unsplash_image(prompt)
    
    async def _fetch_unsplash_image(self, query: str) -> Optional[GeneratedImage]:
        """从 Unsplash 获取图片"""
        
        if not self.unsplash_api_key:
            logger.warning("Unsplash API key not set")
            return None
        
        try:
            # 简化查询词，取前几个关键词
            simple_query = " ".join(query.split()[:5])
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    "https://api.unsplash.com/photos/random",
                    params={
                        "query": simple_query,
                        "orientation": "landscape",
                        "w": 1920,
                        "h": 1080
                    },
                    headers={
                        "Authorization": f"Client-ID {self.unsplash_api_key}"
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Unsplash API error: {response.status_code}")
                    return None
                
                data = response.json()
                
                # 获取适合的尺寸
                urls = data.get("urls", {})
                image_url = urls.get("regular") or urls.get("full") or urls.get("raw")
                
                if image_url:
                    return GeneratedImage(
                        url=image_url,
                        source="unsplash",
                        prompt=query,
                        width=data.get("width", 1920),
                        height=data.get("height", 1080)
                    )
                
                return None
                
        except Exception as e:
            logger.error(f"Unsplash fetch error: {e}")
            return None


# 单例实例
_generator: Optional[ImageGenerator] = None

def get_image_generator() -> ImageGenerator:
    """获取图像生成器单例"""
    global _generator
    if _generator is None:
        _generator = ImageGenerator()
    return _generator


# 测试代码
if __name__ == "__main__":
    async def test():
        gen = ImageGenerator(
            unsplash_api_key=os.getenv("UNSPLASH_API_KEY")
        )
        
        # 测试 Unsplash
        result = await gen.generate_cover_image(
            title="2024年度总结",
            scenario="annual_review",
            source="unsplash"
        )
        
        if result:
            print(f"Generated image from {result.source}: {result.url[:100]}...")
        else:
            print("Failed to generate image")
    
    asyncio.run(test())
