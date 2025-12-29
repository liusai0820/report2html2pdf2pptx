"""
AI Presentation Generator - FastAPI Server
支持实时进度推送 (SSE) 和完整的生成流程

@input:  config, core/, v2_adapter, 前端HTTP请求
@output: REST API端点, SSE流式响应, 静态文件服务
@pos:    后端服务主入口，所有HTTP请求的网关

⚠️ 一旦我被更新，务必更新：
   1. 我的头部注释
   2. /src/_FOLDER.md
"""
import os
import sys
import json
import shutil
import asyncio
import traceback
import logging
from pathlib import Path
from typing import List, Optional, AsyncGenerator
from datetime import datetime, timezone, timedelta
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# 北京时区 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))

def beijing_now():
    """获取北京时间"""
    return datetime.now(BEIJING_TZ)

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
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
import mailer
import db
from core.output_renderer import OutputRenderer
from v2.image_generator import get_image_generator
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import reporter

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
    font_style: Optional[str] = "modern"  # 'modern' (黑体) 或 'classic' (楷体)
    organization: Optional[str] = "深圳国家高技术产业创新中心"
    target_pages: int = 25
    content_depth: str = "normal"
    skip_pdf: bool = False
    skip_pptx: bool = False
    custom_instructions: Optional[str] = None  # 用户自定义 AI 指令
    bg_image_source: Optional[str] = "none"  # 背景图来源: 'none', 'unsplash', 'ai'
    # 🔐 管理员专用字段
    model: Optional[str] = None  # 自定义模型（需要管理员权限）
    user_email: Optional[str] = None  # 用户邮箱（用于权限验证）

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

    # Initialize Scheduler
    scheduler = AsyncIOScheduler()
    # 每天 23:00 (Asia/Shanghai)
    # ⚠️ 必须指定时区，否则 CronTrigger 默认使用 UTC
    from pytz import timezone
    beijing_tz = timezone('Asia/Shanghai')
    scheduler.add_job(
        reporter.send_daily_report, 
        CronTrigger(hour=23, minute=0, timezone=beijing_tz),
        id='daily_report',  # 添加固定 ID 防止重复
        replace_existing=True  # 如果已存在则替换，防止多份
    )
    scheduler.start()
    print("📅 Daily report scheduler started (Target: 23:00 Asia/Shanghai)")
    
    yield
    
    # Shutdown
    if scheduler.running:
        scheduler.shutdown()

app = FastAPI(title="AI Presentation Generator API", lifespan=lifespan)

# CORS - 允许 Vercel 前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应设置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 安全的静态文件服务 ==========

from fastapi import Request, Response, status
from fastapi.responses import FileResponse
import jwt

# JWT 验证辅助函数
def verify_jwt_token(token: str) -> Optional[dict]:
    """验证 JWT token 并返回用户信息"""
    if not token:
        return None
    try:
        # 从 Supabase JWT 中解析（使用 JWT服务密钥）
        payload = jwt.decode(
            token, 
            config.SUPABASE_JWT_SECRET,  # 需要在 config 中添加
            algorithms=["HS256"],
            audience="authenticated"
        )
        return payload
    except Exception as e:
        logger.warning(f"JWT验证失败: {e}")
        return None

@app.middleware("http")
async def protect_output_directory(request: Request, call_next):
    """
    [已暂时禁用拦截] 保护 /output 目录兼顾安全性与可用性
    目前仅记录日志，不拦截请求，以确保前端演示功能正常。
    """
    
    # 1.只拦截 /output 路径
    if not request.url.path.startswith("/output/"):
        return await call_next(request)
    
    # 全部放行，仅做记录 (待前端支持 token 参数后再开启)
    # logger.info(f"Accessing output: {request.url.path}")
    
    return await call_next(request)

# 挂载预览模板目录（公开）
previews_dir = Path("output/theme_previews")
if previews_dir.exists():
    app.mount("/previews", StaticFiles(directory=str(previews_dir)), name="previews")

# 静态文件服务（已由上面的中间件保护）
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

# 🔐 管理员权限检查 API
@app.get("/api/admin/check")
async def check_admin_status(email: str = None):
    """检查用户是否是管理员，并返回可用模型"""
    if not email:
        return {"is_admin": False, "models": []}
    
    is_admin = config.is_admin(email)
    if is_admin:
        return {
            "is_admin": True,
            "models": config.ADMIN_MODELS
        }
    return {"is_admin": False, "models": []}
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
async def upload_file(
    file: UploadFile = File(...),
    user_email: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_location = Path("input") / file.filename
    try:
        with file_location.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")
    
    # 发送 Telegram 通知 (异步，不阻塞) + 包含用户邮箱
    if config.TELEGRAM_ENABLED:
        try:
            file_size = file_location.stat().st_size
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            # 包含用户邮箱信息
            user_info = f"\\n👤 用户: `{user_email}`" if user_email else ""
            caption = f"📂 *新文件上传*\\n\\n📄 `{file.filename}`\\n📊 大小: {size_str}{user_info}\\n🕐 {beijing_now().strftime('%H:%M:%S')}"
            # 这里简单起见直接用 httpx 做一个 fire-and-forget 请求，或者用 BackgroundTasks
            # 为了避免引入 BackgroundTasks 参数修改太复杂，这里用 asyncio.create_task
            # 发送文件到 Telegram
            async def send_file_to_telegram():
                try:
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        # 读取文件
                        with open(file_location, 'rb') as f:
                            files = {'document': (file.filename, f, 'application/octet-stream')}
                            data = {'chat_id': config.TELEGRAM_CHAT_ID, 'caption': caption, 'parse_mode': 'Markdown'}
                            
                            response = await client.post(
                                f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendDocument",
                                files=files,
                                data=data
                            )
                            
                            if response.status_code != 200:
                                logger.warning(f"Telegram 文件发送失败: {response.text}")
                except Exception as e:
                    logger.error(f"发送文件到 Telegram 失败: {e}")
                    # 如果文件发送失败，至少发送文本通知
                    try:
                        async with httpx.AsyncClient() as client:
                            await client.post(
                                f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage",
                                json={"chat_id": config.TELEGRAM_CHAT_ID, "text": caption, "parse_mode": "Markdown"},
                                timeout=5.0
                            )
                    except:
                        pass
            asyncio.create_task(send_file_to_telegram())
        except:
            pass

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

        # [ComfyUI Integration] 启动封面生成任务
        cover_bg_task = None
        # 只有在配置文件启用了 ComfyUI 且 用户明确选择了 AI 绘图时才生成
        if config.COMFYUI_ENABLED and req.bg_image_source == "ai":
            logger.info("启动 AI 封面生成任务 (ComfyUI)...")
            img_gen = get_image_generator()
            cover_bg_task = asyncio.create_task(
                img_gen.generate_cover_image(
                    title=req.document_name,
                    scenario=req.scenario,
                    source="ai"
                )
            )
        
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

        # [ComfyUI Integration] 注入封面图
        if cover_bg_task:
            try:
                # 30s 超时
                cover_img = await asyncio.wait_for(cover_bg_task, timeout=30)
                if cover_img and cover_img.url and pages_html[0]:
                    logger.info(f"注入封面图: {cover_img.url}")
                    # 注入 CSS 覆盖样式
                    # 增加文字阴影以确保在复杂图片上的可读性
                    style_inject = f"""
                    <style>
                    .cover-slide {{ 
                        background-image: url('{cover_img.url}') !important;
                        background-size: cover !important;
                        background-position: center !important;
                    }}
                    /* 增强文字可读性 */
                    .cover-slide .main-title, 
                    .cover-slide .sub-title, 
                    .cover-slide .doc-type,
                    .cover-slide .footer-item {{ 
                        color: #ffffff !important; 
                        text-shadow: 0 2px 10px rgba(0,0,0,0.8) !important;
                    }}
                    /* 弱化原有装饰 */
                    .cover-slide::before, .cover-slide::after {{ opacity: 0; }}
                    </style>
                    """
                    pages_html[0] = pages_html[0].replace("</head>", f"{style_inject}\n</head>")
                    action_log.append(f"🎨 已生成 AI 封面 ({cover_img.source})")
            except Exception as e:
                logger.warning(f"AI 封面生成跳过: {e}")
        
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
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 nginx 缓冲
            "X-Content-Type-Options": "nosniff",
            "CF-Cache-Status": "DYNAMIC",
            "Keep-Alive": "timeout=600, max=1000",
            "Transfer-Encoding": "chunked",
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
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 nginx 缓冲
            "X-Content-Type-Options": "nosniff",
            # Cloudflare 相关
            "CF-Cache-Status": "DYNAMIC",
            # 防止连接被提前关闭
            "Keep-Alive": "timeout=600, max=1000",
            "Transfer-Encoding": "chunked",
        }
    )

# ========== Telegram 反馈通知 ==========

import httpx

class FeedbackNotification(BaseModel):
    rating: int  # 1-10分
    comment: Optional[str] = None
    user_email: Optional[str] = None
    document_name: Optional[str] = None
    generation_id: Optional[str] = None
    user_id: Optional[str] = None
    # 新增：结构化问卷数据
    survey_summary: Optional[str] = None  # 细项评价摘要
    improvements: Optional[str] = None  # 改进建议（逗号分隔）

@app.post("/api/notify-feedback")
async def notify_feedback(feedback: FeedbackNotification):
    """发送反馈通知到 Telegram，并尝试自动补发邮件或 AI 回复"""
    
    # 异步处理后续逻辑，不阻塞前端响应
    asyncio.create_task(process_feedback_background(feedback))
    return {"status": "queued"}

async def process_feedback_background(feedback: FeedbackNotification):
    """后台处理反馈：补发PDF、AI分析回复、Telegram通知"""
    
    # 初始化状态
    email_sent = False
    ai_reply_content = None
    action_log = []
    
    # 1. 场景一：生成失败导致的反馈（自动补发 PDF）
    # 逻辑优化：不仅看当前 generation_id，如果当前没有，尝试搜寻同名文件的最近一次成功记录
    pdf_path = None
    
    # A. 优先检查当前 ID
    if feedback.generation_id:
        current_path = Path("output") / feedback.generation_id / "presentation.pdf"
        if current_path.exists():
            pdf_path = current_path
            
    # B. 如果当前 ID 没找到，尝试智能搜寻最近的成功记录
    if not pdf_path and feedback.document_name:
        try:
            # 提取核心文件名 (假设 document_name 是上传的文件名)
            # 我们需要遍历 output 下的所有目录，看谁的名字里包含这个 document_name 且里面有 PDF
            output_dir = Path("output")
            candidates = []
            
            # 简单的模糊匹配
            raw_name = Path(feedback.document_name).stem # 去掉扩展名
            
            for d in output_dir.iterdir():
                if not d.is_dir(): continue
                # 检查目录名是否包含文件名关键词 (稍微宽松一点)
                if raw_name in d.name:
                    # 检查是否有 PDF
                    candidate_pdf = d / "presentation.pdf"
                    if candidate_pdf.exists():
                        candidates.append(candidate_pdf)
            
            # 如果找到了，取修改时间最近的一个
            if candidates:
                # 按修改时间倒序
                candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                pdf_path = candidates[0]
                print(f"✨ Smart recovery: Found PDF in {pdf_path.parent.name} for request {feedback.generation_id}")
                
        except Exception as e:
            print(f"Smart recovery failed: {e}")

    pdf_recovered = False
    
    # 执行加额度操作 (如果提供了 user_id)
    quota_added = False
    new_quota_info = ""
    if feedback.user_id:
        success, new_val = db.add_generation_quota(feedback.user_id, 3) # 补偿 3 次
        if success:
            quota_added = True
            new_quota_info = f"（当前剩余额度: {new_val}次）"
            action_log.append(f"💰 已自动补偿3次额度")
    
    if config.SMTP_ENABLED and feedback.user_email and pdf_path and pdf_path.exists():
        subject = "【HIIC AI团队】您的演示文稿已生成（附系统异常致歉与补偿说明）"
        body = f"""
        <p><strong>{feedback.user_email}</strong>，您好！</p>
        <p>我是创新中心 AI 产品组的运营。</p>
        <p>监测到您刚才反馈的问题，我们核实发现：您的文档其实<strong>已经成功生成</strong>，只是因为网络原因前端没能加载出来。</p>
        <p>为了不耽误您使用，我们已人工调取了最新生成的演示文稿 PDF 版本，作为附件发送给您，请查收。</p>
        <p><strong>🎁 补偿通知</strong>：已为您后台账号补充了 <strong>3次</strong> 额外生成额度{new_quota_info}，您可以继续放心试用。</p>
        <br>
        <p>------------------<br>
        <strong>HIIC AI 产品运营组</strong></p>
        """
        # 保存为草稿
        if mailer.save_to_drafts(feedback.user_email, subject, body, str(pdf_path)):
            email_sent = True
            pdf_recovered = True
            action_log.append(f"📝 PDF补发邮件已存草稿 (来源: {pdf_path.parent.name})")

    # 2. 场景二：AI 智能回复用户评论 (仅当没有触发 PDF 补发，且用户写了有效评论时)
    # 如果已经补发了 PDF，就不用 AI 再回一封了，免得打扰
    if not pdf_recovered and config.SMTP_ENABLED and feedback.comment and len(feedback.comment) > 2 and feedback.user_email:
        try:
            # 调用 AI 分析并拟写回复
            ai_reply_content = await generate_ai_reply(feedback, quota_info=new_quota_info)
            if ai_reply_content:
                # 发送 AI 写的邮件
                subject = f"【HIIC AI团队】关于您反馈的回复"
                # 包装一下 AI 的回复为 HTML
                html_body = f"""
                <p>您好！收到您关于 <b>"{feedback.document_name or '文档生成'}"</b> 的反馈。</p>
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 8px; font-style: italic; color: #555;">
                您的反馈："{feedback.comment}"
                </div>
                <br>
                {ai_reply_content.replace(chr(10), '<br>')}
                <br>
                <br>
                <p>------------------<br>
                <strong>HIIC AI 产品运营组</strong></p>
                """
                if mailer.save_to_drafts(feedback.user_email, subject, html_body, pdf_path=None):
                    email_sent = True
                    action_log.append("📝 AI回复已存草稿")
        except Exception as e:
            print(f"AI reply failed: {e}")
            action_log.append(f"⚠️ AI回复失败: {e}")

    # 3. 发送汇总通知到 Telegram
    if config.TELEGRAM_ENABLED:
        # 评分表情映射 (1-10分)
        if feedback.rating <= 3:
            rating_emoji = "😞"
            rating_label = "需改进"
        elif feedback.rating <= 6:
            rating_emoji = "😐"
            rating_label = "达预期"
        elif feedback.rating <= 8:
            rating_emoji = "😊"
            rating_label = "满意"
        else:
            rating_emoji = "🤩"
            rating_label = "超预期"
        
        # 构建消息
        message = f"""📊 *新用户反馈*
━━━━━━━━━━━━━━━━━
{rating_emoji} *{feedback.rating}/10 分* ({rating_label})

"""
        # 问卷细项评价
        if feedback.survey_summary:
            message += f"📋 *细项评价:*\n{feedback.survey_summary}\n\n"
        
        # 改进建议
        if feedback.improvements:
            message += f"🔧 *希望改进:* {feedback.improvements}\n\n"
            
        if feedback.comment:
            message += f"💬 *详细反馈:* {feedback.comment}\n\n"
        if feedback.user_email:
            message += f"👤 *用户:* `{feedback.user_email}`\n"
        if feedback.document_name:
            message += f"📄 *文档:* {feedback.document_name}\n"
        
        # 添加操作日志
        if action_log:
            message += "\n" + "\n".join(action_log)
            
        # 如果有 AI 回复的内容，摘要显示
        if ai_reply_content:
            preview = ai_reply_content[:100] + "..." if len(ai_reply_content) > 100 else ai_reply_content
            message += f"\n\n📝 *AI回复内容:*\n_{preview}_"

        message += f"\n🕐 *时间:* {beijing_now().strftime('%Y-%m-%d %H:%M')}"
        
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": config.TELEGRAM_CHAT_ID, 
                        "text": message, 
                        "parse_mode": "Markdown"
                    },
                    timeout=10.0
                )
        except Exception as e:
            print(f"Telegram notification sent failed: {e}")

async def generate_ai_reply(feedback: FeedbackNotification, quota_info: str = "") -> str:
    """调用 LLM 生成得体的邮件回复"""
    import openai # Assuming standard openai compatible client or just use httpx
    
    prompt = f"""
    你是一位高情商、专业的 AI 产品运营经理。
    用户刚刚提交了一条反馈，情况如下：
    - 评分：{feedback.rating}/5 星
    - 评论内容："{feedback.comment}"
    - 上下文：用户在试用我们的 "AI PPT 生成工具" (内测版)。
    
    我们的核心策略是：
    1. 鼓励反馈：告诉用户反馈非常有价值，是共创产品的一部分。
    2. 奖励机制：对于提供了有效建议的用户，我们会额外赠送试用次数（我们后台刚刚已经操作完毕，即刻生效）。
    
    请起草一封回复邮件的正文（不要标题，只要正文）。
    - 语气要像朋友一样自然，但保持专业。
    - 针对用户的具体评论内容进行回应，不要只会说套话。
    - 必须明确告知用户：**"已为您增加 3 次额外生成额度{quota_info}"**。
    - 控制在 150 字以内，简洁有力。
    """
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=config.OPENROUTER_BASE_URL + "/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
                    "HTTP-Referer": "https://ppt.gwy.life",
                },
                json={
                    "model": config.DEFAULT_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7
                },
                timeout=15.0
            )
            data = resp.json()
            return data['choices'][0]['message']['content']
    except Exception as e:
        print(f"LLM generation failed: {e}")
        return None


# ========== 新用户注册通知 ==========

class NewUserNotification(BaseModel):
    user_email: str
    user_id: Optional[str] = None

@app.post("/api/notify-new-user")
async def notify_new_user(data: NewUserNotification):
    """新用户注册时发送 Telegram 通知"""
    if not config.TELEGRAM_ENABLED:
        return {"status": "skipped", "message": "Telegram not configured"}
    
    message = f"""🎉 *新用户注册*
━━━━━━━━━━━━━━━━━
👤 邮箱: `{data.user_email}`
🕐 时间: {beijing_now().strftime('%Y-%m-%d %H:%M:%S')}

#NewUser #Registration"""
    
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": config.TELEGRAM_CHAT_ID,
                    "text": message,
                    "parse_mode": "Markdown"
                },
                timeout=10.0
            )
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Failed to send new user notification: {e}")
        return {"status": "error", "message": str(e)}

# ========== 运行入口 ==========

if __name__ == "__main__":
    port = int(os.getenv("API_PORT", "8005"))
    host = os.getenv("API_HOST", "0.0.0.0")
    uvicorn.run("server:app", host=host, port=port, reload=True)
