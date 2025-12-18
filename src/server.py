"""
AI Presentation Generator - FastAPI Server
支持实时进度推送 (SSE) 和完整的生成流程
"""
import os
import sys
import json
import shutil
import asyncio
import traceback
from pathlib import Path
from typing import List, Optional, AsyncGenerator
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

# Add src to sys.path
src_path = Path(__file__).parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# 导入配置 (这会触发环境变量加载)
import config
from core import PresentationGenerator
from core.context_builder import ContextBuilder
from core.ai_orchestrator import AIOrchestrator
from core.output_renderer import OutputRenderer

# ========== Pydantic Models ==========

def adjust_color(hex_color: str, factor: float) -> str:
    """简单调整 Hex 颜色亮度"""
    if not hex_color or not hex_color.startswith('#'):
        return hex_color
    try:
        color = hex_color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = min(255, max(0, int(r * factor)))
        g = min(255, max(0, int(g * factor)))
        b = min(255, max(0, int(b * factor)))
        return "#{:02x}{:02x}{:02x}".format(r, g, b)
    except Exception:
        return hex_color

class GenerateRequest(BaseModel):
    document_name: str
    scenario: str = "consulting"
    theme_color: Optional[str] = None  # 添加缺失的主题色字段
    organization: Optional[str] = "深圳国家高技术产业创新中心"
    target_pages: int = 25
    content_depth: str = "normal"
    skip_pdf: bool = False
    skip_pptx: bool = False
    custom_instructions: Optional[str] = None  # 用户自定义 AI 指令

class FileInfo(BaseModel):
    name: str
    size: float
    unit: str

class ProgressEvent(BaseModel):
    stage: str  # context, outline, content, pdf, pptx, done, error
    message: str
    progress: int  # 0-100
    current: Optional[int] = None
    total: Optional[int] = None
    result: Optional[dict] = None

# ========== App Lifecycle ==========

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    os.makedirs("input", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    print(f"✓ Adobe PDF Services: {'可用' if config.ADOBE_AVAILABLE else '未配置'}")
    yield
    # Shutdown

app = FastAPI(title="AI Presentation Generator API", lifespan=lifespan)

# CORS - 允许 Vercel 前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应设置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载预览模板目录
previews_dir = Path("output/theme_previews")
if previews_dir.exists():
    app.mount("/previews", StaticFiles(directory=str(previews_dir)), name="previews")

# 静态文件服务
app.mount("/output", StaticFiles(directory="output"), name="output")

# ========== 场景配置 ==========

SCENARIOS = [
    {"id": "consulting", "name": "咨询研究/汇报", "desc": "政府汇报、咨询报告、研究课题"},
    {"id": "annual_review", "name": "年终述职/总结", "desc": "年终总结、工作汇报、述职报告"},
    {"id": "company_intro", "name": "公司/项目介绍", "desc": "公司介绍、项目路演、产品发布"},
    {"id": "academic", "name": "学术研究/答辩", "desc": "学术报告、论文答辩、研究分享"},
    {"id": "creative", "name": "创意/营销", "desc": "品牌推广、营销方案、创意提案"},
    {"id": "government", "name": "政府公文", "desc": "政府报告、政策解读、党建汇报"},
]

# ========== API Endpoints ==========

@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "adobe_available": config.ADOBE_AVAILABLE,
        "version": "2.0.0"
    }

@app.get("/api/scenarios")
async def get_scenarios():
    return SCENARIOS

class OutputInfo(BaseModel):
    """已生成的输出信息"""
    name: str  # 目录名
    display_name: str  # 显示名称
    timestamp: str  # 生成时间
    pages_count: int  # 页面数量
    has_pdf: bool  # 是否有 PDF
    has_pptx: bool  # 是否有 PPTX

@app.get("/api/files", response_model=List[FileInfo])
async def list_files():
    input_dir = Path("input")
    if not input_dir.exists():
        return []
    
    files = []
    for ext in ['.docx', '.doc', '.md', '.json', '.txt']:
        for f in input_dir.rglob(f"*{ext}"):
            size_bytes = f.stat().st_size
            if size_bytes < 1024:
                size, unit = size_bytes, "B"
            elif size_bytes < 1024 * 1024:
                size, unit = size_bytes / 1024, "KB"
            else:
                size, unit = size_bytes / (1024 * 1024), "MB"
            files.append(FileInfo(name=f.name, size=round(size, 1), unit=unit))
    return sorted(files, key=lambda x: x.name)


@app.get("/api/outputs", response_model=List[OutputInfo])
async def list_outputs():
    """列出 output 目录下已生成的演示文稿"""
    output_dir = Path("output")
    if not output_dir.exists():
        return []
    
    outputs = []
    for d in output_dir.iterdir():
        if not d.is_dir():
            continue
        # 排除特殊目录
        if d.name.startswith('.') or d.name == "theme_previews":
            continue
        
        pages_dir = d / "pages"
        if not pages_dir.exists():
            continue
        
        # 统计页面数
        pages_count = len(list(pages_dir.glob("page-*.html")))
        if pages_count == 0:
            continue
        
        # 检查是否有 PDF 和 PPTX
        has_pdf = any(d.glob("*.pdf"))
        has_pptx = any(d.glob("*.pptx"))
        
        # 解析时间戳（从目录名中提取）
        # 格式：xxx_YYYYMMDD_HHMMSS 或 xxx_YYYYMMDD_HHMMSS_v2
        name_parts = d.name.rsplit('_', 2)
        timestamp_str = ""
        display_name = d.name
        
        if len(name_parts) >= 2:
            # 尝试解析时间戳
            try:
                if name_parts[-1] == "v2":
                    # xxx_YYYYMMDD_HHMMSS_v2 格式
                    if len(name_parts) >= 3:
                        date_part = name_parts[-3] if len(name_parts) >= 4 else ""
                        time_part = name_parts[-2]
                        display_name = '_'.join(name_parts[:-3]) if len(name_parts) >= 4 else name_parts[0]
                        if len(date_part) == 8 and len(time_part) == 6:
                            timestamp_str = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:]} {time_part[:2]}:{time_part[2:4]}:{time_part[4:]}"
                else:
                    # xxx_YYYYMMDD_HHMMSS 格式
                    date_part = name_parts[-2]
                    time_part = name_parts[-1]
                    display_name = '_'.join(name_parts[:-2])
                    if len(date_part) == 8 and len(time_part) == 6:
                        timestamp_str = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:]} {time_part[:2]}:{time_part[2:4]}:{time_part[4:]}"
            except (IndexError, ValueError):
                pass
        
        outputs.append(OutputInfo(
            name=d.name,
            display_name=display_name or d.name,
            timestamp=timestamp_str,
            pages_count=pages_count,
            has_pdf=has_pdf,
            has_pptx=has_pptx
        ))
    
    # 按修改时间倒序排列
    return sorted(outputs, key=lambda x: x.timestamp, reverse=True)


@app.get("/api/outputs/{output_name}/load")
async def load_output(output_name: str):
    """加载指定的历史输出"""
    output_dir = Path("output") / output_name
    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="输出目录不存在")
    
    pages_dir = output_dir / "pages"
    if not pages_dir.exists():
        raise HTTPException(status_code=404, detail="页面目录不存在")
    
    # 收集所有页面
    page_files = sorted(pages_dir.glob("page-*.html"))
    pages_data = []
    
    for i, page_file in enumerate(page_files):
        # 从 HTML 中提取标题（简单解析）
        title = f"Page {i + 1}"
        try:
            with open(page_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 尝试匹配 title 标签或 h1 标签
                import re
                title_match = re.search(r'<title>([^<]+)</title>', content)
                if title_match:
                    title = title_match.group(1)
                else:
                    h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', content)
                    if h1_match:
                        title = h1_match.group(1)
        except Exception:
            pass
        
        pages_data.append({
            "index": i + 1,
            "title": title,
            "type": "CONTENT",
            "url": f"/output/{output_name}/pages/{page_file.name}"
        })
    
    # 查找 PDF 和 PPTX
    pdf_files = list(output_dir.glob("*.pdf"))
    pptx_files = list(output_dir.glob("*.pptx"))
    html_files = list(output_dir.glob("presentation.html"))
    
    result = {
        "html": str(html_files[0]) if html_files else None,
        "pages": pages_data,
        "downloads": {
            "html": f"/output/{output_name}/presentation.html" if html_files else None,
            "pdf": f"/output/{output_name}/{pdf_files[0].name}" if pdf_files else None,
            "pptx": f"/output/{output_name}/{pptx_files[0].name}" if pptx_files else None
        }
    }
    
    return result

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_location = Path("input") / file.filename
    try:
        with file_location.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")
    
    return {"filename": file.filename, "status": "success"}

# ========== SSE 实时进度生成 ==========

async def generate_with_progress(req: GenerateRequest) -> AsyncGenerator[str, None]:
    """
    使用 SSE 流式推送生成进度
    """
    def send_event(stage: str, message: str, progress: int, **kwargs):
        event = ProgressEvent(stage=stage, message=message, progress=progress, **kwargs)
        return f"data: {event.model_dump_json()}\n\n"
    
    input_file = Path("input") / req.document_name
    if not input_file.exists():
        yield send_event("error", f"文档不存在: {req.document_name}", 0)
        return
    
    try:
        # ===== Stage 1: 构建上下文 =====
        yield send_event("context", "正在解析文档...", 5)
        
        builder = ContextBuilder()
        builder.from_document(str(input_file))
        builder.with_scenario(req.scenario)
        if req.organization:
            # 兼容旧代码，将 organization 传入 ContextBuilder
            builder.with_organization(req.organization)
            
        context = builder.build()
        
        # 动态应用用户自定义颜色
        if req.theme_color and context.theme:
            print(f"Applying custom theme color: {req.theme_color}")
            context.theme.colors.primary = req.theme_color
            context.theme.colors.primary_light = adjust_color(req.theme_color, 1.2)
            context.theme.colors.primary_dark = adjust_color(req.theme_color, 0.8)
            # 也可以更新 accent，或者保持默认
            
        print(f"Context built: {context.scenario} - {context.document_name}")
        yield send_event("context", "上下文构建完成", 10)
        
        # ===== Stage 2: 生成大纲 =====
        yield send_event("outline", "AI 正在规划大纲...", 15)
        
        orchestrator = AIOrchestrator(config.DEFAULT_MODEL)
        outline = await orchestrator.generate_outline(context)
        
        # 补全大纲
        outline = _complete_outline(outline, context)
        total_pages = len(outline)
        
        # 推送大纲数据供前端展示
        yield send_event("outline", f"大纲生成完成，共 {total_pages} 页", 20, total=total_pages, result={"outline": outline})
        
        # ===== Stage 3: 创建输出目录 =====
        doc_name = Path(req.document_name).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(f"output/{doc_name}_{timestamp}")
        output_dir.mkdir(parents=True, exist_ok=True)
        pages_dir = output_dir / "pages"
        pages_dir.mkdir(exist_ok=True)
        
        renderer = OutputRenderer(str(output_dir))
        template = renderer.render_template(context)
        
        # ===== Stage 4: 并行生成页面内容 =====
        yield send_event("content", "正在生成幻灯片内容...", 25, current=0, total=total_pages)
        
        semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_REQUESTS)
        pages_html = [None] * total_pages
        completed = [0]
        
        async def generate_page(page_info, page_num):
            async with semaphore:
                html = await orchestrator.generate_page(context, page_info, page_num, total_pages)
                pages_html[page_num - 1] = html
                completed[0] += 1
                return page_num
        
        tasks = [generate_page(page_info, i + 1) for i, page_info in enumerate(outline)]
        
        for coro in asyncio.as_completed(tasks):
            page_num = await coro
            content_progress = 25 + int((completed[0] / total_pages) * 40)
            yield send_event(
                "content", 
                f"正在生成幻灯片 ({completed[0]}/{total_pages})...", 
                content_progress,
                current=completed[0],
                total=total_pages
            )
        
        # ===== Stage 5: 保存页面并准备预览 =====
        yield send_event("content", "准备预览...", 68)
        
        # 使用线程池执行同步IO操作
        await asyncio.to_thread(lambda: [renderer.save_page(i, html, template) for i, html in enumerate(pages_html, 1)])
        html_path = await asyncio.to_thread(renderer.merge_pages, pages_html, template)
        
        # 构建页面列表供前端预览
        pages_data = []
        base_url_path = f"/output/{doc_name}_{timestamp}/pages"
        for i, page_info in enumerate(outline):
            pages_data.append({
                "index": i + 1,
                "title": page_info.get("title", f"Page {i+1}"),
                "type": page_info.get("type", "CONTENT"),
                "url": f"{base_url_path}/page-{i+1:02d}.html"
            })
            
        # 关键点：立即推送 preview_ready
        preview_data = {
            "html": str(html_path),
            "pages": pages_data
        }
        yield send_event("preview_ready", "预览就绪", 70, result=preview_data)
        
        # ===== Stage 6 & 7: 后台生成 PDF 和 PPTX =====
        pdf_path = None
        pptx_path = None
        
        if not req.skip_pdf:
            yield send_event("pdf", "正在后台生成 PDF...", 75)
            try:
                # 后台生成 PDF
                pdf_path = await asyncio.to_thread(renderer.generate_pdf, doc_name)
                yield send_event("pdf_ready", "PDF 准备就绪", 85, result={"pdf": pdf_path})
                
                # 有了 PDF 后，继续生成 PPTX
                if not req.skip_pptx and pdf_path and config.ADOBE_AVAILABLE:
                    yield send_event("pptx", "正在后台转换 PPTX...", 90)
                    pptx_path = await asyncio.to_thread(renderer.generate_pptx, pdf_path)
                    
                    if pptx_path:
                        yield send_event("pptx_ready", "PPTX 准备就绪", 98, result={"pptx": pptx_path})
                    else:
                        yield send_event("error", "PPTX 转换失败", 98) # 非致命错误，暂且发个消息
            except Exception as e:
                traceback.print_exc()
                # log error but don't stop the stream if preview is already out
        
        # ===== Done =====
        final_result = {
            "downloads": {"html": str(html_path), "pdf": pdf_path, "pptx": pptx_path},
            "pages": pages_data
        }
        yield send_event("done", "全部完成", 100, result=final_result)
        
        # ===== Done =====
        # 构建页面列表供前端预览
        pages_data = []
        base_url_path = f"/output/{doc_name}_{timestamp}/pages"
        
        for i, page_info in enumerate(outline):
            pages_data.append({
                "index": i + 1,
                "title": page_info.get("title", f"Page {i+1}"),
                "type": page_info.get("type", "CONTENT"),
                "url": f"{base_url_path}/page-{i+1:02d}.html"
            })
            
        final_result = {
            "downloads": result,
            "pages": pages_data
        }
        
        yield send_event("done", "生成完成!", 100, result=final_result)
        
    except Exception as e:
        traceback.print_exc()
        yield send_event("error", f"生成失败: {str(e)[:200]}", 0)

def _complete_outline(outline, context):
    """补全大纲"""
    complete = []
    
    has_cover = any(p.get("type") == "COVER" for p in outline)
    has_agenda = any(p.get("type") == "AGENDA" for p in outline)
    has_closing = any(p.get("type") == "CLOSING" for p in outline)
    
    if not has_cover:
        title = context.project_name or context.document_name or "演示文稿"
        complete.append({"type": "COVER", "title": title, "content": ""})
    
    if not has_agenda:
        sections = [p["title"] for p in outline if p.get("type") == "SECTION"]
        if sections:
            complete.append({
                "type": "AGENDA",
                "title": "目录",
                "content": "\n".join(f"- {s}" for s in sections)
            })
    
    section_counter = 0
    for page in outline:
        page_type = page.get("type", "CONTENT")
        if page_type == "COVER" and not has_cover:
            continue
        if page_type == "SECTION":
            section_counter += 1
            page["section_num"] = section_counter
        complete.append(page)
    
    if not has_closing:
        complete.append({"type": "CLOSING", "title": "谢谢观看", "content": ""})
    
    return complete

@app.post("/api/generate-stream")
async def generate_stream(req: GenerateRequest):
    """
    SSE 流式生成端点
    前端使用 EventSource 连接
    """
    return StreamingResponse(
        generate_with_progress(req),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 nginx 缓冲
        }
    )

# 保留原有的同步 API（向后兼容）
@app.post("/api/generate")
async def generate_presentation_sync(req: GenerateRequest):
    """同步生成 API（向后兼容）"""
    input_file = Path("input") / req.document_name
    if not input_file.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    
    cfg = {
        "organization": req.organization,
        "target_pages": req.target_pages,
        "content_depth": req.content_depth
    }
    
    try:
        generator = PresentationGenerator()
        result = await generator.generate(
            document_path=str(input_file),
            scenario=req.scenario,
            config=cfg,
            skip_pdf=req.skip_pdf,
            skip_pptx=req.skip_pptx
        )
        return {"status": "success", "result": result}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ========== V2 API Integration ==========

from v2_adapter import generate_v2_stream

@app.post("/api/generate-v2")
async def generate_v2(req: GenerateRequest):
    """
    V2 端到端 AI 原生生成入口
    """
    return StreamingResponse(
        generate_v2_stream(req),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

# ========== 运行入口 ==========

if __name__ == "__main__":
    port = int(os.getenv("API_PORT", "8005"))
    host = os.getenv("API_HOST", "0.0.0.0")
    uvicorn.run("server:app", host=host, port=port, reload=True)
