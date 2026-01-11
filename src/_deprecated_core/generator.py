"""
统一生成器 - 整合所有组件的入口

这是 AI 原生架构的核心：
1. ContextBuilder 收集信息
2. AIOrchestrator 与 AI 交互
3. OutputRenderer 输出结果

没有复杂的分支逻辑，没有硬编码的模板选择。
所有决策都由 AI 根据上下文做出。
"""

import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from .context_builder import ContextBuilder, PresentationContext, build_context_from_config
from .ai_orchestrator import AIOrchestrator
from .output_renderer import OutputRenderer

console = Console()


class PresentationGenerator:
    """
    演示文稿生成器
    
    使用方式：
    ```python
    generator = PresentationGenerator()
    await generator.generate(
        document_path="input/report.docx",
        scenario="consulting",
        config={"organization": "XX公司", "target_pages": 30}
    )
    ```
    """
    
    def __init__(self, model: str = None):
        from config import DEFAULT_MODEL
        self.model = model or DEFAULT_MODEL
        self.orchestrator = AIOrchestrator(self.model)
    
    async def generate(
        self,
        document_path: str,
        scenario: str = "consulting",
        config: Optional[Dict[str, Any]] = None,
        output_dir: Optional[str] = None,
        skip_pdf: bool = False,
        skip_pptx: bool = False,
    ) -> Dict[str, str]:
        """
        生成演示文稿
        
        Args:
            document_path: 源文档路径
            scenario: 场景类型
            config: 用户配置
            output_dir: 输出目录
            skip_pdf: 跳过 PDF 生成
            skip_pptx: 跳过 PPTX 生成
        
        Returns:
            包含输出文件路径的字典
        """
        config = config or {}
        
        # 1. 构建上下文
        console.print("\n[cyan]📋 构建上下文...[/cyan]")
        context = self._build_context(document_path, scenario, config)
        console.print(f"[green]✓[/green] 上下文已构建")
        console.print(f"[dim]  场景: {scenario}[/dim]")
        console.print(f"[dim]  目标: {context.target_pages} 页[/dim]")
        
        # 2. 创建输出目录
        if not output_dir:
            doc_name = Path(document_path).stem
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"output/{doc_name}_{timestamp}"
        
        renderer = OutputRenderer(output_dir)
        
        # 3. 生成大纲
        console.print("\n[cyan]📝 AI 正在规划大纲...[/cyan]")
        outline = await self.orchestrator.generate_outline(context)
        
        # 添加封面、目录、封底
        outline = self._complete_outline(outline, context)
        console.print(f"[green]✓[/green] 大纲已生成: {len(outline)} 页")
        
        # 预览大纲
        self._preview_outline(outline)
        
        # 4. 生成模板
        template = renderer.render_template(context)
        
        # 5. 生成所有页面
        console.print(f"\n[cyan]🎨 生成 {len(outline)} 页内容...[/cyan]")
        pages_html = await self._generate_all_pages(context, outline)
        
        # 6. 保存页面
        for i, html in enumerate(pages_html, 1):
            renderer.save_page(i, html, template)
        
        # 7. 合并页面
        html_path = renderer.merge_pages(pages_html, template)
        
        result = {"html": html_path}
        
        # 8. 生成 PDF
        if not skip_pdf:
            doc_name = Path(document_path).stem
            pdf_path = renderer.generate_pdf(doc_name)
            result["pdf"] = pdf_path
            
            # 9. 生成 PPTX
            if not skip_pptx and pdf_path:
                pptx_path = renderer.generate_pptx(pdf_path)
                if pptx_path:
                    result["pptx"] = pptx_path
        
        # 完成
        console.print("\n[bold green]✨ 生成完成！[/bold green]")
        console.print(f"\n输出目录: [cyan]{output_dir}[/cyan]")
        for fmt, path in result.items():
            console.print(f"  - {fmt.upper()}: [dim]{path}[/dim]")
        
        return result
    
    def _build_context(
        self,
        document_path: str,
        scenario: str,
        config: Dict[str, Any]
    ) -> PresentationContext:
        """构建上下文"""
        builder = ContextBuilder()
        builder.from_document(document_path)
        builder.with_scenario(scenario)
        
        if config.get("organization"):
            builder.with_organization(
                config["organization"],
                config.get("project_name", ""),
                config.get("date", "")
            )
        
        if config.get("audience"):
            builder.with_audience(
                config["audience"],
                config.get("audience_expectations", "")
            )
        
        builder.with_structure(
            config.get("target_pages", 25),
            config.get("content_depth", "normal")
        )
        
        if config.get("tone"):
            builder.with_style(
                config.get("tone", ""),
                config.get("visual_style", ""),
                config.get("color_preference", "")
            )
        
        return builder.build()
    
    def _complete_outline(
        self,
        outline: List[Dict[str, Any]],
        context: PresentationContext
    ) -> List[Dict[str, Any]]:
        """补全大纲（智能添加封面、目录、封底，避免重复）"""
        complete = []
        
        # 检查 AI 是否已经生成了封面
        has_cover = any(p.get("type") == "COVER" for p in outline)
        has_agenda = any(p.get("type") == "AGENDA" for p in outline)
        has_closing = any(p.get("type") == "CLOSING" for p in outline)
        
        # 只在没有封面时添加
        if not has_cover:
            title = context.project_name or context.document_name or "演示文稿"
            complete.append({
                "type": "COVER",
                "title": title,
                "content": ""
            })
        
        # 只在没有目录时添加
        if not has_agenda:
            sections = [p["title"] for p in outline if p.get("type") == "SECTION"]
            if sections:
                complete.append({
                    "type": "AGENDA",
                    "title": "目录",
                    "content": "\n".join(f"- {s}" for s in sections)
                })
        
        # 正文（过滤掉 AI 可能生成的重复封面/目录）
        # 同时为 SECTION 页面添加正确的章节序号
        section_counter = 0
        for page in outline:
            page_type = page.get("type", "CONTENT")
            # 跳过 AI 生成的封面（如果标题和我们的一样）
            if page_type == "COVER" and not has_cover:
                continue
            
            # 为 SECTION 页面添加章节序号
            if page_type == "SECTION":
                section_counter += 1
                page["section_num"] = section_counter
            
            complete.append(page)
        
        # 只在没有封底时添加
        if not has_closing:
            complete.append({
                "type": "CLOSING",
                "title": "谢谢观看",
                "content": ""
            })
        
        return complete
    
    def _preview_outline(self, outline: List[Dict[str, Any]]):
        """预览大纲"""
        console.print("\n[bold]大纲预览：[/bold]")
        
        section_num = 0
        for i, page in enumerate(outline[:12], 1):
            page_type = page["type"]
            title = page["title"]
            
            if page_type == "SECTION":
                section_num += 1
                console.print(f"  [cyan]{i}.[/cyan] [bold][SECTION][/bold] {title}")
            elif page_type in ["COVER", "AGENDA", "CLOSING"]:
                console.print(f"  [cyan]{i}.[/cyan] [dim][{page_type}][/dim] {title}")
            else:
                console.print(f"  [cyan]{i}.[/cyan] {title[:50]}...")
        
        if len(outline) > 12:
            console.print(f"  ... (还有 {len(outline) - 12} 页)")
    
    async def _generate_all_pages(
        self,
        context: PresentationContext,
        outline: List[Dict[str, Any]]
    ) -> List[str]:
        """并行生成所有页面"""
        total = len(outline)
        
        # 使用信号量控制并发
        from config import MAX_CONCURRENT_REQUESTS
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        
        async def generate_one(page_info: Dict, page_num: int) -> tuple:
            async with semaphore:
                html = await self.orchestrator.generate_page(
                    context, page_info, page_num, total
                )
                return page_num, html
        
        # 创建所有任务
        tasks = [
            generate_one(page_info, i + 1)
            for i, page_info in enumerate(outline)
        ]
        
        # 并行执行并显示进度
        results = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]生成页面...", total=total)
            
            for coro in asyncio.as_completed(tasks):
                page_num, html = await coro
                results[page_num] = html
                progress.update(task, advance=1)
        
        # 按页码排序
        return [results[i] for i in range(1, total + 1)]


async def generate_presentation(
    document_path: str,
    scenario: str = "consulting",
    config: Optional[Dict[str, Any]] = None,
    output_dir: Optional[str] = None,
) -> Dict[str, str]:
    """
    便捷函数：生成演示文稿
    
    示例：
    ```python
    result = await generate_presentation(
        "input/report.docx",
        scenario="consulting",
        config={"organization": "XX公司"}
    )
    print(result["pdf"])
    ```
    """
    generator = PresentationGenerator()
    return await generator.generate(
        document_path,
        scenario,
        config,
        output_dir
    )
