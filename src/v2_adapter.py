"""
V2 API Adapter - 适配 Flask Server

将 v2 引擎集成到现有的 FastAPI 服务中
"""

import os
from pathlib import Path
from typing import AsyncGenerator
from v2.engine import PresentationEngine
import config

async def generate_v2_stream(req) -> AsyncGenerator[str, None]:
    """
    v2 版本的流式生成适配器
    """
    
    # 辅助函数：发送 SSE 事件
    def send_event(stage: str, message: str, progress: int, **kwargs):
        import json
        data = {
            "stage": stage,
            "message": message,
            "progress": progress,
            **kwargs
        }
        return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

    try:
        # 1. 准备环境
        input_file = Path("input") / req.document_name
        if not input_file.exists():
            yield send_event("error", f"文档不存在: {req.document_name}", 0)
            return

        # 读取文档内容
        # 简单处理：如果是 md/txt 直接读取，如果是 docx 需要解析
        content = ""
        if input_file.suffix in ('.txt', '.md'):
            content = input_file.read_text(encoding='utf-8')
        else:
            # 复用 v1 的解析逻辑
            from document_parser import DocumentParser
            doc_data = DocumentParser.load_document(str(input_file))
            content = doc_data.get('full_content', '')
            
        if not content:
            yield send_event("error", "文档内容为空或解析失败", 0)
            return

        # 2. 初始化引擎（使用高并发模型）
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        engine = PresentationEngine(
            api_key=config.OPENROUTER_API_KEY,
            base_url=config.OPENROUTER_BASE_URL,
            model=config.DEFAULT_MODEL,  # 使用配置的模型
            output_dir=f"output/{input_file.stem}_{timestamp}_v2",
            max_concurrent=config.MAX_CONCURRENT_REQUESTS
        )

        # 3. 定义进度回调
        # 为了能够将进度发送给 yield，我们需要一特殊的队列或机制
        # 或者简化处理：因为 engine.generate 是 async 的，我们稍微修改 engine 接口或许更好
        # 但为了保持 engine 纯净，我们在这里处理 adapter 逻辑
        
        # 现在的 engine.generate 接受一个 on_progress 回调
        # 但这个回调是在 async 函数内部调用的，我们无法直接 yield
        # 解决方案：使用 Queue 进行通信，或者重写 engine 逻辑为生成器
        
        # 这里为了快速集成，我们暂时采用非流式的回调（打印日志），
        # 真正的流式推送由 engine 内部的步骤决定。
        # 更好的方案是让 engine.generate 本身就是一个 AsyncGenerator
        
        # 重新封装 engine.generate 为生成器模式比较复杂，
        # 我们采用 Hack 方案：手动分步调用 engine 的内部方法，
        # 或者修改 engine.generate 让它接受一个 async callback
        
        # 让我们修改 engine.generate 让它更灵活。
        # 但现在，我们先尝试在 adapter 里分步调用，还原 engine 的逻辑
        
        # --- 手动编排 v2 流程以支持 yield ---
        
        yield send_event("context", "正在初始化 V2 AI 原生引擎...", 5)
        
        # 初始化设计系统
        from v2.design_system import DesignSystem
        from v2.ai_designer import GenerationContext
        from v2.validator import SlideValidator
        from v2.ai_designer import PageInfo
        
        ds = DesignSystem.from_scenario(req.scenario, custom_primary=req.theme_color, font_style=req.font_style or "modern")
        context = GenerationContext(
            document_content=content,
            document_name=req.document_name,
            organization=req.organization or "汇报单位",
            scenario=req.scenario,
            design_system=ds,
            target_pages=req.target_pages,
            content_depth=req.content_depth,
            custom_instructions=req.custom_instructions or "",  # 用户自定义指令
            bg_image_source=getattr(req, 'bg_image_source', 'none')  # 背景图来源
        )
        validator = SlideValidator(ds)
        
        # 生成大纲
        yield send_event("outline", "AI 设计师正在规划大纲...", 10)
        outline_result = await engine.designer.generate_outline(context)
        # 提取 AI 生成的标题和页面列表
        ai_title = outline_result.get("title")  # AI 生成的干净标题
        outline_pages = outline_result.get("pages", [])
        outline_pages = engine._complete_outline(outline_pages, context, ai_title)
        total_pages = len(outline_pages)
        
        yield send_event("outline", f"大纲规划完成，共 {total_pages} 页", 20, result={"outline": outline_pages})
        
        # 并行生成
        yield send_event("content", "AI 设计师正在创作页面 (端到端设计)...", 25, total=total_pages, current=0)
        
        import asyncio
        semaphore = asyncio.Semaphore(engine.max_concurrent)
        completed_count = 0
        pages_html = [None] * total_pages
        
        # 进度队列
        progress_queue = asyncio.Queue()
        
        async def generate_worker(index, page_data):
            nonlocal completed_count
            async with semaphore:
                try:
                    info = PageInfo(
                        type=page_data['type'],
                        title=page_data.get('title', ''),
                        content=page_data.get('content', ''),
                        page_num=index + 1,
                        total_pages=total_pages,
                        section_num=page_data.get('section_num', 0)
                    )
                    
                    html = await engine.designer.generate_page(context, info)
                    
                    # 验证
                    validation = validator.validate(html)
                    if not validation.is_valid:
                        html = validator.fix_html(html)
                    
                    pages_html[index] = html
                    completed_count += 1
                    
                    await progress_queue.put(completed_count) # 通知进度
                    
                except Exception as e:
                    print(f"Error generating page {index}: {e}")
                    pages_html[index] = f"<div class='error'>Error: {e}</div>"
                    completed_count += 1
                    await progress_queue.put(completed_count)

        # 启动任务
        tasks = [generate_worker(i, p) for i, p in enumerate(outline_pages)]
        # 不等待 tasks 完成，而是启动它们并在后台运行
        background_tasks = asyncio.gather(*tasks)
        
        # 监听进度 (带心跳机制，防止 Cloudflare Tunnel 超时)
        last_heartbeat = asyncio.get_event_loop().time()
        HEARTBEAT_INTERVAL = 5  # 每 5 秒发送心跳（Cloudflare 超时约 100 秒，留足余量）
        
        while completed_count < total_pages:
            try:
                # 使用超时等待，确保可以定期发送心跳
                current = await asyncio.wait_for(progress_queue.get(), timeout=HEARTBEAT_INTERVAL)
                percent = 25 + int(60 * current / total_pages)
                yield send_event(
                    "content", 
                    f"正在创作页面 ({current}/{total_pages})", 
                    percent, 
                    current=current, 
                    total=total_pages
                )
                last_heartbeat = asyncio.get_event_loop().time()
            except asyncio.TimeoutError:
                # 超时未收到进度，发送心跳保持连接
                yield send_event(
                    "heartbeat",
                    f"AI 正在深度思考... ({completed_count}/{total_pages})",
                    25 + int(60 * completed_count / total_pages),
                    current=completed_count,
                    total=total_pages
                )
        
        # 确保所有任务真的完成了
        await background_tasks
        
        # 合并
        yield send_event("content", "正在合并页面...", 85)
        
        pages_result = []
        for i, html in enumerate(pages_html):
            if html:
                page_path = engine.output_dir / "pages" / f"page-{i+1:02d}.html"
                full_page_html = engine._wrap_page_html(html, ds)
                page_path.write_text(full_page_html, encoding='utf-8')
                
                pages_result.append({
                    "index": i + 1,
                    "title": outline_pages[i].get('title', f'Page {i+1}'),
                    "type": outline_pages[i].get('type', 'CONTENT'),
                    "url": f"/output/{engine.output_dir.name}/pages/page-{i+1:02d}.html"
                })
        
        merged_path = engine.output_dir / "presentation.html"
        merged_html = engine._merge_all_pages(pages_html, ds)
        merged_path.write_text(merged_html, encoding='utf-8')
        
        # 预览就绪
        preview_data = {
            "html": str(merged_path),
            "pages": pages_result
        }
        yield send_event("preview_ready", "预览就绪", 90, result=preview_data)
        
        # 如果需要 PDF (调用 v1 的 renderer)
        pdf_path = None
        pptx_path = None
        
        if not req.skip_pdf:
            yield send_event("pdf", "正在生成 PDF（可能需要较长时间）...", 92)
            # 复用 v1 renderer 的 PDF 生成功能
            from core.output_renderer import OutputRenderer
            v1_renderer = OutputRenderer(str(engine.output_dir))
            
            try:
                # 使用后台任务 + 心跳循环，确保 SSE 连接不被断开
                pdf_task = asyncio.create_task(
                    asyncio.to_thread(v1_renderer.generate_pdf, context.document_name)
                )
                
                # PDF 生成心跳循环 - 每 5 秒发送一次心跳
                heartbeat_count = 0
                while not pdf_task.done():
                    await asyncio.sleep(5)
                    heartbeat_count += 1
                    yield send_event(
                        "pdf_progress",
                        f"PDF 生成中... ({heartbeat_count * 5}秒)",
                        93 + min(heartbeat_count, 4),  # 93-97 之间
                    )
                
                pdf_path = await pdf_task
                yield send_event("pdf_ready", "PDF 准备就绪", 98, result={"pdf": pdf_path})
                
                # 2. 生成 PPTX (依赖 PDF, 且需要用户勾选)
                if not req.skip_pptx and pdf_path:
                    try:
                        yield send_event("pptx", "正在转换 PPTX (可能需要 1-2 分钟)...", 99)
                        
                        pptx_task = asyncio.create_task(
                            asyncio.to_thread(v1_renderer.generate_pptx, pdf_path)
                        )
                        
                        # PPTX 生成心跳循环
                        heartbeat_count = 0
                        while not pptx_task.done():
                            await asyncio.sleep(5)
                            heartbeat_count += 1
                            yield send_event(
                                "pptx_progress",
                                f"PPTX 转换中... ({heartbeat_count * 5}秒)",
                                99,
                            )
                        
                        pptx_path = await pptx_task
                        if pptx_path:
                            yield send_event("pptx_ready", "PPTX 准备就绪", 99, result={"pptx": pptx_path})
                        else:
                            yield send_event("pptx_skipped", "PPTX 转换未成功，但 PDF 可用", 99)
                    except Exception as pptx_err:
                        # PPTX 失败不影响整体流程
                        print(f"PPTX conversion failed: {pptx_err}")
                        yield send_event("pptx_error", f"PPTX 转换失败 (PDF 仍可用): {str(pptx_err)[:80]}", 99)
                    
            except Exception as e:
                print(f"PDF generation failed: {e}")
                import traceback
                traceback.print_exc()
                yield send_event("pdf_error", f"PDF 生成失败: {str(e)[:100]}", 98)
                
        # 完成 - 无论 PPTX 是否成功都发送完成事件
        final_result = {
            "downloads": {
                "html": f"/output/{engine.output_dir.name}/presentation.html",
                "pdf": f"/output/{engine.output_dir.name}/{Path(pdf_path).name}" if pdf_path else None,
                "pptx": f"/output/{engine.output_dir.name}/{Path(pptx_path).name}" if pptx_path else None,
            },
            "output_dir": engine.output_dir.name,  # 直接返回目录名，便于前端使用
            "pages": pages_result,
            "pages_count": len(pages_result)
        }
        yield send_event("done", "全部完成", 100, result=final_result)

    except Exception as e:
        import traceback
        traceback.print_exc()
        yield send_event("error", f"V2 引擎错误: {str(e)}", 0)
