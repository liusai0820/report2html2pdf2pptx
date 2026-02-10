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

# Admin API moved to bottom

# --- Main Entry ---
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
from v2.ai_designer import AIDesigner, GenerationContext
from v2.design_system import DesignSystem
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

class GenerateSpeechRequest(BaseModel):
    output_name: str
    user_id: str  # 用户 ID，用于保存演讲稿到数据库

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
    # 管理员模型选择功能
    model: Optional[str] = None  # 管理员可选模型
    user_email: Optional[str] = None  # 用户邮箱（用于判断管理员权限）

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

# 确保必要的目录存在（在 mount 之前）
os.makedirs("input", exist_ok=True)
os.makedirs("output", exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"✓ Adobe PDF Services: {'可用' if config.ADOBE_AVAILABLE else '未配置'}")

    # Initialize Scheduler
    scheduler = AsyncIOScheduler()
    # 每天 23:00 (Asia/Shanghai)
    scheduler.add_job(reporter.send_daily_report, CronTrigger(hour=23, minute=0))
    scheduler.start()
    print("📅 Daily report scheduler started (Target: 23:00 Beijing Time)")
    
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
from jwt import PyJWKClient

# JWT 验证辅助函数
def verify_jwt_token(token: str) -> Optional[dict]:
    """验证 JWT token 并返回用户信息 (自动适配 HS256/RS256/ES256)"""
    if not token:
        return None
    try:
        # 优先尝试 JWKS (公钥) 验证 (推荐方式，支持 RS256/ES256)
        # 构造 JWKS URL: https://<project>.supabase.co/auth/v1/jwks.json
        if config.VITE_SUPABASE_URL:
            try:
                jwks_url = f"{config.VITE_SUPABASE_URL.rstrip('/')}/auth/v1/jwks.json"
                jwks_client = PyJWKClient(jwks_url)
                signing_key = jwks_client.get_signing_key_from_jwt(token)

                return jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=["RS256", "ES256", "HS256"],
                    audience="authenticated"
                )
            except Exception as jwks_e:
                # 如果 JWKS 失败（例如网络问题或 token 是旧的 HS256），回退到 Secret 验证
                # logger.debug(f"JWKS verify failed, falling back to secret: {jwks_e}")
                pass

        # 回退：尝试使用 Secret 验证 (兼容旧的 HS256)
        if config.SUPABASE_JWT_SECRET:
            return jwt.decode(
                token,
                config.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated"
            )

        return None

    except Exception as e:
        logger.warning(f"JWT验证失败: {e}")
        return None

@app.middleware("http")
async def protect_output_directory(request: Request, call_next):
    """保护 /output 目录 - 临时简化版（全部放行）
    
    TODO: 待前端支持传递 auth token 后，恢复完整的权限验证
    """
    
    # 只拦截 /output 路径
    if not request.url.path.startswith("/output/"):
        return await call_next(request)
    
    # 排除预览模板（公开访问）
    if "/theme_previews" in request.url.path or "/previews/" in request.url.path:
        return await call_next(request)
    
    # 临时：全部放行，仅做日志记录
    # logger.info(f"[Output访问] 路径: {request.url.path}")
    
    return await call_next(request)


# 挂载预览模板目录（公开）
# 挂载预览模板目录（公开）
# 优先使用 src/previews (源码内置)，回退到 output/theme_previews (旧逻辑)
previews_src = Path(__file__).parent / "previews"
previews_output = Path("output/theme_previews")

if previews_src.exists():
    app.mount("/previews", StaticFiles(directory=str(previews_src)), name="previews")
    print(f"✓ Mounted previews from source: {previews_src}")
elif previews_output.exists():
    app.mount("/previews", StaticFiles(directory=str(previews_output)), name="previews")
    print(f"✓ Mounted previews from output: {previews_output}")
else:
    print("⚠ No preview directory found!")

# 静态文件服务（已由上面的中间件保护）
app.mount("/output", StaticFiles(directory="output"), name="output")

# ========== 场景配置 ==========

SCENARIOS = [
    {"id": "consulting", "name": "咨询研究/汇报", "desc": "政府汇报、咨询报告、研究课题", "color": "#0A1628"},
    {"id": "annual_review", "name": "年终述职/总结", "desc": "年终总结、工作汇报、述职报告", "color": "#1A365D"},
    {"id": "thesis_proposal", "name": "大学生开题报告", "desc": "毕业论文开题、答辩汇报", "color": "#1E40AF"},
    {"id": "company_intro", "name": "公司/项目介绍", "desc": "公司介绍、项目路演、产品发布", "color": "#00D4FF"},
    {"id": "academic", "name": "学术研究/答辩", "desc": "学术报告、论文答辩、研究分享", "color": "#1E3A5F"},
    {"id": "creative", "name": "创意/营销", "desc": "品牌推广、营销方案、创意提案", "color": "#E94560"},
    {"id": "government", "name": "政府公文", "desc": "政府报告、政策解读、党建汇报", "color": "#8B1538"},
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
async def upload_file(
    file: UploadFile = File(...), 
    user_email: str = Form(None)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_location = Path("input") / file.filename
    try:
        with file_location.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")
    
    # 发送 Telegram 通知 (异步，不阻塞)
    if config.TELEGRAM_ENABLED:
        try:
            file_size = file_location.stat().st_size
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            # 加上用户邮箱
            user_info = f"👤 {user_email}\\n" if user_email else ""
            caption = f"📂 *新文件上传*\\n\\n{user_info}📄 `{file.filename}`\\n📊 大小: {size_str}\\n🕐 {beijing_now().strftime('%H:%M:%S')}"
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

    # 异步上传到 Cloudflare R2 (备份)
    try:
        async def upload_to_r2_task(file_path: Path):
            try:
                from r2_storage import get_storage
                storage = get_storage()
                if storage.enabled:
                    # 按日期分层: inputs/2024/12/30/filename.pdf
                    from datetime import datetime
                    now = datetime.now()
                    key = f"inputs/{now.year}/{now.month:02d}/{now.day:02d}/{file_path.name}"
                    storage.upload_file(file_path, key)
                    logger.info(f"Uploaded input to R2: {key}")
            except Exception as e:
                logger.error(f"R2 input upload failed: {e}")

        asyncio.create_task(upload_to_r2_task(file_location))
    except Exception as e:
        logger.error(f"Failed to start R2 upload task: {e}")

    return {"filename": file.filename, "status": "success"}

# ========== 新用户注册通知 ==========

OCCUPATION_LABELS = {
    "student": "大学生/研究生",
    "teacher": "教师/讲师",
    "researcher": "研究员/学者",
    "employee": "企业员工",
    "manager": "管理层/高管",
    "consultant": "咨询顾问",
    "freelancer": "自由职业",
    "entrepreneur": "创业者",
    "government": "政府/事业单位",
    "other": "其他"
}

class NewUserNotification(BaseModel):
    user_email: str
    user_id: Optional[str] = None
    occupation: Optional[str] = None

@app.post("/api/notify-new-user")
async def notify_new_user(notification: NewUserNotification):
    """发送新用户注册通知到 Telegram，并保存职业信息"""
    
    # 保存职业信息到 profiles
    if notification.user_id and notification.occupation:
        try:
            from db import get_client
            client = get_client()
            if client:
                client.table("profiles").update({
                    "occupation": notification.occupation
                }).eq("id", notification.user_id).execute()
                logger.info(f"Saved occupation for user {notification.user_id}: {notification.occupation}")
        except Exception as e:
            logger.warning(f"Failed to save occupation: {e}")
    
    if not config.TELEGRAM_ENABLED:
        return {"status": "skipped", "reason": "telegram not enabled"}
    
    try:
        occupation_label = OCCUPATION_LABELS.get(notification.occupation, notification.occupation or "未填写")
        
        message = (
            f"🎉 *新用户注册*\n\n"
            f"👤 邮箱: `{notification.user_email}`\n"
            f"💼 身份: {occupation_label}\n"
            f"🕐 时间: {beijing_now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"#NewUser #Registration"
        )
        
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": config.TELEGRAM_CHAT_ID,
                    "text": message,
                    "parse_mode": "Markdown"
                }
            )
            
            if response.status_code == 200:
                logger.info(f"New user notification sent: {notification.user_email}")
                return {"status": "sent"}
            else:
                logger.warning(f"Telegram notification failed: {response.text}")
                return {"status": "failed", "reason": response.text}
                
    except Exception as e:
        logger.error(f"Failed to send new user notification: {e}")
        return {"status": "error", "reason": str(e)}

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

        # 【新增】保存元数据 metadata.json (用于演讲稿生成等后续任务)
        try:
            metadata = {
                "document_name": req.document_name,
                "scenario": req.scenario,
                "organization": req.organization,
                "theme_color": req.theme_color,
                "font_style": req.font_style,
                "target_pages": req.target_pages,
                "content_depth": req.content_depth,
                "created_at": timestamp,
                "pages": outline,
            }
            metadata_path = output_dir / "metadata.json"
            import json
            metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
            logger.info(f"Metadata saved: {metadata_path}")
        except Exception as e:
            logger.warning(f"Failed to save metadata in V1: {e}")

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
        
        # ===== 发送 HTML 到 Telegram (供本地转 PDF) =====
        if config.TELEGRAM_ENABLED and html_path:
            async def send_html_to_telegram():
                try:
                    import httpx
                    html_file_path = Path(html_path)
                    if html_file_path.exists():
                        # 获取用户邮箱（如果有）
                        user_info = f"👤 {req.user_email}\n" if hasattr(req, 'user_email') and req.user_email else ""
                        caption = (
                            f"📄 *生成完成*\n\n"
                            f"{user_info}"
                            f"📁 `{html_file_path.name}`\n"
                            f"🕐 {beijing_now().strftime('%H:%M:%S')}\n"
                            f"#HTML #ToPDF"
                        )
                        
                        logger.info(f"Preparing to send HTML to Telegram: {html_file_path}")
                        async with httpx.AsyncClient(timeout=60.0) as client:
                            with open(html_file_path, 'rb') as f:
                                files = {'document': (html_file_path.name, f, 'text/html')}
                                data = {'chat_id': config.TELEGRAM_CHAT_ID, 'caption': caption, 'parse_mode': 'Markdown'}
                                
                                response = await client.post(
                                    f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendDocument",
                                    files=files,
                                    data=data
                                )
                                
                                if response.status_code == 200:
                                    logger.info(f"HTML sent to Telegram: {html_file_path.name}")
                                else:
                                    logger.warning(f"Failed to send HTML to Telegram: {response.text}")
                    else:
                        logger.error(f"HTML file not found for Telegram: {html_path}")
                except Exception as e:
                    logger.error(f"Error sending HTML to Telegram: {e}")
                    traceback.print_exc()
            
            asyncio.create_task(send_html_to_telegram())
            
    except Exception as e:
        logger.error(f"Generation error: {e}")
        traceback.print_exc()
        yield send_event("error", f"生成出错: {str(e)}", 0)

# Debug Endpoint for Telegram
@app.post("/api/debug/telegram")
async def debug_telegram(test_email: str = "test@example.com"):
    """测试 Telegram 发送功能"""
    if not config.TELEGRAM_ENABLED:
        return {"status": "error", "message": "Telegram not enabled"}
    
    try:
        import httpx
        # create a dummy file
        dummy_path = Path("test_telegram.html")
        dummy_path.write_text("<h1>Test Telegram</h1><p>If you see this, it works.</p>")
        
        caption = f"🧪 *Test Message*\n👤 {test_email}\n🕐 {beijing_now().strftime('%H:%M:%S')}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            with open(dummy_path, 'rb') as f:
                files = {'document': ('test.html', f, 'text/html')}
                data = {'chat_id': config.TELEGRAM_CHAT_ID, 'caption': caption, 'parse_mode': 'Markdown'}
                
                response = await client.post(
                    f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendDocument",
                    files=files,
                    data=data
                )
                
                result = {
                    "status_code": response.status_code,
                    "response": response.text,
                    "bot_token_prefix": config.TELEGRAM_BOT_TOKEN[:5] + "...",
                    "chat_id": config.TELEGRAM_CHAT_ID
                }
                
        dummy_path.unlink(missing_ok=True)
        return result
        
    except Exception as e:
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}

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
    rating: int
    comment: Optional[str] = None
    user_email: Optional[str] = None
    document_name: Optional[str] = None
    generation_id: Optional[str] = None
    user_id: Optional[str] = None

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

    # 3. 发送汇总是知到 Telegram
    if config.TELEGRAM_ENABLED:
        # 评分表情映射
        rating_emoji = {1: "😞", 2: "😐", 3: "🙂", 4: "😊", 5: "🤩"}
        stars = "⭐" * feedback.rating + "☆" * (5 - feedback.rating)
        
        # 构建消息
        message = f"""📊 *新用户反馈*
━━━━━━━━━━━━━━━━━
{stars} {rating_emoji.get(feedback.rating, "")}

"""
        if feedback.comment:
            message += f"💬 *评论:* {feedback.comment}\n\n"
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

# ========== 演讲稿 API ==========

@app.get("/api/speech/{output_name}")
async def get_speech(output_name: str):
    """
    获取已缓存的演讲稿

    Returns:
        - {"status": "found", "script": content} 如果存在缓存
        - {"status": "not_found"} 如果不存在
    """
    cached_script = db.get_speech_script(output_name)

    if cached_script:
        return {"status": "found", "script": cached_script}
    else:
        return {"status": "not_found"}


@app.post("/api/generate-speech")
async def generate_speech(req: GenerateSpeechRequest):
    """
    根据已生成的演示文稿生成演讲稿
    """
    output_dir = Path("output") / req.output_name
    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="演示文稿不存在")

    metadata_path = output_dir / "metadata.json"
    if not metadata_path.exists():
        # 尝试向后兼容：如果是刚生成的但没有 metadata (极其罕见)，或者是旧的
        # 这里我们严格一点，没有 metadata 就无法高质量生成
        raise HTTPException(status_code=400, detail="该演示文稿不支持演讲稿生成 (元数据丢失)")

    try:
        import json
        metadata = json.loads(metadata_path.read_text(encoding='utf-8'))

        # 1. 重建上下文
        document_name = metadata.get('document_name')
        if not document_name:
             raise HTTPException(status_code=400, detail="元数据损坏")

        input_file = Path("input") / document_name

        content = ""
        if input_file.exists():
             # 复用解析逻辑
            try:
                if input_file.suffix.lower() in ('.txt', '.md'):
                    content = input_file.read_text(encoding='utf-8')
                else:
                    from document_parser import DocumentParser
                    doc_data = DocumentParser.load_document(str(input_file))
                    content = doc_data.get('full_content', '')
            except Exception as e:
                logger.warning(f"Failed to read input file {input_file}: {e}")

        # 如果 content 为空，脚本生成质量会下降，但我们仍然允许生成 (基于 slide content)

        # 初始化 DesignSystem
        ds = DesignSystem.from_scenario(metadata.get('scenario', 'consulting'))

        context = GenerationContext(
            document_content=content,
            document_name=document_name,
            organization=metadata.get('organization', '汇报单位'),
            scenario=metadata.get('scenario', 'consulting'),
            design_system=ds,
            target_pages=metadata.get('target_pages', 20),
            content_depth=metadata.get('content_depth', 'normal')
        )

        # 2. 初始化 Designer
        designer = AIDesigner(
            api_key=config.OPENROUTER_API_KEY,
            base_url=config.OPENROUTER_BASE_URL,
            model=config.DEFAULT_MODEL
        )

        # 3. 生成演讲稿
        pages = metadata.get('pages', [])
        if not pages:
             raise HTTPException(status_code=400, detail="演示文稿页面数据为空")

        script = await designer.generate_speech_script(context, pages)

        # 4. 保存到数据库
        db.save_speech_script(req.output_name, req.user_id, script)

        return {"status": "success", "script": script}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate speech failed: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"生成演讲稿失败: {str(e)}")

# ========== 运行入口 ==========

# --- Admin API ---

class UpgradeRequest(BaseModel):
    key: str
    user_id: str
    plan_type: str
    quota: int
    validity_days: int

@app.get("/api/admin/users")
async def admin_get_users(key: str = "", limit: int = 200):
    """获取用户列表 (需要 Access Key)"""
    import os
    admin_key = os.getenv("ADMIN_KEY", "123456") 
    
    if key != admin_key:
        raise HTTPException(status_code=403, detail="Invalid Admin Key")
        
    try:
        from db import get_all_users
        try:
            # 确保传递了 limit 参数，如果不需要分页可以调整逻辑
            users = get_all_users(limit=limit)
            return {"users": users}
        except TypeError:
            # 如果db.py里的get_all_users没接收limit参数，尝试不带参数调用
            users = get_all_users()
            return {"users": users}
            
    except Exception as e:
        logger.error(f"Admin fetch users error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/upgrade")
async def admin_upgrade_user(req: UpgradeRequest):
    """升级用户套餐"""
    import os
    admin_key = os.getenv("ADMIN_KEY", "123456")
    
    if req.key != admin_key:
        raise HTTPException(status_code=403, detail="Invalid Admin Key")
        
    try:
        from db import set_user_plan
        success, msg = set_user_plan(req.user_id, req.plan_type, req.quota, req.validity_days)
        if success:
            return {"status": "success", "message": msg}
        else:
            raise HTTPException(status_code=500, detail=msg)
    except Exception as e:
        logger.error(f"Admin upgrade error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/generations")
async def admin_get_generations(key: str = "", limit: int = 50):
    """获取生成记录列表"""
    import os
    admin_key = os.getenv("ADMIN_KEY", "123456")
    
    if key != admin_key:
        raise HTTPException(status_code=403, detail="Invalid Admin Key")
        
    try:
        from db import get_client
        client = get_client()
        if not client:
            return {"generations": []}
        
        # 查询 admin_generations 视图
        res = client.table("admin_generations").select("*").limit(limit).execute()
        return {"generations": res.data or []}
    except Exception as e:
        logger.error(f"Admin fetch generations error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("API_PORT", "8005"))
    host = os.getenv("API_HOST", "0.0.0.0")
    uvicorn.run("server:app", host=host, port=port, reload=True)
