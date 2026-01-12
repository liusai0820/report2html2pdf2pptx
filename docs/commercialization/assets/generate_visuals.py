import cairo
import math
import os

# Paths
OUTPUT_DIR = "/Users/qibaoba/report2html2pdf2pptx/docs/commercialization/assets"

# Colors - Light & Fresh palette (refined)
LIGHT_BG = (0.97, 0.98, 0.99)              # 浅灰白背景 #F7F8FC
LIGHT_BG_ALT = (0.94, 0.96, 0.98)          # 次级浅色背景
LIGHT_ACCENT = (0.88, 0.91, 0.95)          # 浅色强调
DEEP_NAVY = (0/255, 51/255, 102/255)       # #003366 深蓝（用于文字）
NAVY_MID = (15/255, 40/255, 75/255)        # 中蓝色
GOLD = (255/255, 165/255, 0/255)           # #FFA500 橙金色
GOLD_SOFT = (255/255, 200/255, 80/255)     # 柔和金色
PURE_WHITE = (1, 1, 1)
OFF_WHITE = (0.96, 0.97, 0.98)
DARK_TEXT = (0.15, 0.15, 0.2)              # 深色文字

def draw_rounded_rect(ctx, x, y, w, h, r):
    """Draw a rounded rectangle"""
    ctx.new_path()
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.arc(x + w - r, y + r, r, 1.5 * math.pi, 2 * math.pi)
    ctx.arc(x + w - r, y + h - r, r, 0, 0.5 * math.pi)
    ctx.arc(x + r, y + h - r, r, 0.5 * math.pi, math.pi)
    ctx.close_path()

def setup_chinese_font(ctx, size, bold=False):
    """Setup Chinese font - use system fonts"""
    weight = cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL
    # Try different Chinese fonts available on macOS
    for font_name in ["Microsoft YaHei", "Heiti SC", "PingFang SC", "STHeiti", "SimHei"]:
        try:
            ctx.select_font_face(font_name, cairo.FONT_SLANT_NORMAL, weight)
            ctx.set_font_size(size)
            return True
        except:
            continue
    # Fallback
    ctx.select_font_face("sans-serif", cairo.FONT_SLANT_NORMAL, weight)
    ctx.set_font_size(size)
    return False

def create_logo_design():
    """Create the primary logo design - refined crystalline aesthetic"""
    WIDTH, HEIGHT = 1200, 1200
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)

    # Background - light gradient simulation
    ctx.set_source_rgb(*LIGHT_BG)
    ctx.rectangle(0, 0, WIDTH, HEIGHT)
    ctx.fill()

    # Subtle radial glow from center (light blue tint)
    for i in range(50, 0, -1):
        alpha = 0.005 * (50 - i) / 50
        ctx.set_source_rgba(0.85, 0.90, 0.95, alpha)
        ctx.arc(WIDTH/2, HEIGHT/2 - 50, i * 12, 0, 2 * math.pi)
        ctx.fill()

    # Ultra-fine crystalline grid
    ctx.set_source_rgba(LIGHT_ACCENT[0], LIGHT_ACCENT[1], LIGHT_ACCENT[2], 0.3)
    ctx.set_line_width(0.5)

    grid_size = 60
    for i in range(WIDTH // grid_size + 2):
        ctx.move_to(i * grid_size, 0)
        ctx.line_to(i * grid_size, HEIGHT)
        ctx.stroke()
    for i in range(HEIGHT // grid_size + 2):
        ctx.move_to(0, i * grid_size)
        ctx.line_to(WIDTH, i * grid_size)
        ctx.stroke()

    center_x, center_y = WIDTH / 2, HEIGHT / 2 - 40

    # === MAIN SYMBOL: Document → Slides transformation ===

    # Document shape (source) - with subtle shadow
    doc_x, doc_y = center_x - 200, center_y - 100
    doc_w, doc_h = 150, 180

    # Shadow
    ctx.set_source_rgba(0, 0, 0, 0.3)
    draw_rounded_rect(ctx, doc_x + 8, doc_y + 8, doc_w, doc_h, 8)
    ctx.fill()

    # Main document
    ctx.set_source_rgb(*OFF_WHITE)
    draw_rounded_rect(ctx, doc_x, doc_y, doc_w, doc_h, 8)
    ctx.fill()

    # Document fold corner
    ctx.set_source_rgb(0.88, 0.89, 0.91)
    ctx.move_to(doc_x + doc_w - 30, doc_y)
    ctx.line_to(doc_x + doc_w, doc_y + 30)
    ctx.line_to(doc_x + doc_w - 30, doc_y + 30)
    ctx.close_path()
    ctx.fill()

    # Document content lines - precise spacing
    ctx.set_source_rgba(DEEP_NAVY[0], DEEP_NAVY[1], DEEP_NAVY[2], 0.7)
    line_heights = [50, 75, 100, 125, 145]
    line_widths = [100, 110, 85, 105, 60]
    for i, (lh, lw) in enumerate(zip(line_heights, line_widths)):
        ctx.set_line_width(6 if i == 0 else 4)
        ctx.move_to(doc_x + 20, doc_y + lh)
        ctx.line_to(doc_x + 20 + lw, doc_y + lh)
        ctx.stroke()

    # === Transformation arrow - crystalline velocity ===
    arrow_y = center_y
    arrow_start = doc_x + doc_w + 25
    arrow_end = center_x + 50

    # Arrow glow
    ctx.set_source_rgba(*GOLD, 0.2)
    ctx.set_line_width(20)
    ctx.move_to(arrow_start, arrow_y)
    ctx.line_to(arrow_end + 15, arrow_y)
    ctx.stroke()

    # Main arrow segments
    ctx.set_source_rgb(*GOLD)
    ctx.set_line_width(4)
    segments = 7
    seg_len = (arrow_end - arrow_start) / segments

    for i in range(segments):
        start = arrow_start + i * seg_len
        end = start + seg_len * 0.6
        ctx.move_to(start, arrow_y)
        ctx.line_to(end, arrow_y)
        ctx.stroke()

    # Arrow head - precise crystalline triangle
    ctx.move_to(arrow_end + 30, arrow_y)
    ctx.line_to(arrow_end + 5, arrow_y - 18)
    ctx.line_to(arrow_end + 5, arrow_y + 18)
    ctx.close_path()
    ctx.fill()

    # === Slides stack (output) ===
    slide_base_x = center_x + 70
    slide_base_y = center_y - 80
    slide_w, slide_h = 190, 115

    # Back slides (stacked effect)
    for offset in [(30, 25), (15, 12)]:
        ctx.set_source_rgba(0.7, 0.75, 0.8, 0.4)
        draw_rounded_rect(ctx, slide_base_x + offset[0], slide_base_y + offset[1] + 100, slide_w, slide_h, 6)
        ctx.fill()

    # Main slide - shadow
    ctx.set_source_rgba(0, 0, 0, 0.25)
    draw_rounded_rect(ctx, slide_base_x + 6, slide_base_y + 6, slide_w, slide_h, 6)
    ctx.fill()

    # Main slide body
    ctx.set_source_rgb(*OFF_WHITE)
    draw_rounded_rect(ctx, slide_base_x, slide_base_y, slide_w, slide_h, 6)
    ctx.fill()

    # Golden header accent
    ctx.set_source_rgb(*GOLD)
    ctx.rectangle(slide_base_x, slide_base_y, slide_w, 22)
    ctx.fill()

    # Slide content
    ctx.set_source_rgba(DEEP_NAVY[0], DEEP_NAVY[1], DEEP_NAVY[2], 0.6)
    ctx.rectangle(slide_base_x + 14, slide_base_y + 38, 70, 7)
    ctx.fill()
    ctx.rectangle(slide_base_x + 14, slide_base_y + 52, 95, 5)
    ctx.fill()
    ctx.rectangle(slide_base_x + 14, slide_base_y + 64, 80, 5)
    ctx.fill()

    # Mini chart
    ctx.set_source_rgba(DEEP_NAVY[0], DEEP_NAVY[1], DEEP_NAVY[2], 0.2)
    ctx.rectangle(slide_base_x + 125, slide_base_y + 38, 50, 45)
    ctx.fill()

    # Chart bars
    ctx.set_source_rgb(*GOLD)
    bar_heights = [25, 35, 28]
    for i, bh in enumerate(bar_heights):
        ctx.rectangle(slide_base_x + 132 + i * 15, slide_base_y + 83 - bh, 10, bh)
        ctx.fill()

    # === Typography ===
    # Brand name - English part
    ctx.set_source_rgb(*DARK_TEXT)
    setup_chinese_font(ctx, 78, bold=True)
    text = "SlideCraft"
    extents = ctx.text_extents(text)
    text_x = center_x - extents.width/2 - 30

    ctx.move_to(text_x, center_y + 230)
    ctx.show_text(text)

    # AI suffix
    ctx.set_source_rgb(*GOLD)
    ctx.move_to(text_x + extents.width + 12, center_y + 230)
    ctx.show_text("AI")

    # Tagline - English (避免中文字体问题)
    ctx.set_source_rgba(0.3, 0.3, 0.35, 0.8)
    setup_chinese_font(ctx, 22, bold=False)
    tagline = "Document to Presentation · Instant Transformation"
    ext = ctx.text_extents(tagline)
    ctx.move_to(center_x - ext.width/2, center_y + 275)
    ctx.show_text(tagline)

    # === Corner crystalline accents ===
    ctx.set_source_rgb(*GOLD)
    ctx.set_line_width(1.5)

    corners = [
        (70, 70, 1, 1),      # top-left
        (WIDTH-70, 70, -1, 1),   # top-right
        (70, HEIGHT-70, 1, -1),  # bottom-left
        (WIDTH-70, HEIGHT-70, -1, -1)  # bottom-right
    ]

    for cx, cy, dx, dy in corners:
        ctx.move_to(cx, cy)
        ctx.line_to(cx, cy + 50*dy)
        ctx.move_to(cx, cy)
        ctx.line_to(cx + 50*dx, cy)
        ctx.stroke()

    # Subtle version indicator
    ctx.set_source_rgba(0.4, 0.4, 0.45, 0.5)
    ctx.set_font_size(12)
    ctx.move_to(WIDTH - 100, HEIGHT - 30)
    ctx.show_text("v2.0")

    surface.write_to_png(os.path.join(OUTPUT_DIR, "01_logo_primary.png"))
    print("Created: 01_logo_primary.png")


def create_social_poster():
    """Create social media promotional poster - museum quality"""
    WIDTH, HEIGHT = 1080, 1350
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)

    # Light background
    ctx.set_source_rgb(*LIGHT_BG)
    ctx.rectangle(0, 0, WIDTH, HEIGHT)
    ctx.fill()

    # Subtle ambient glow (soft blue)
    for i in range(40, 0, -1):
        alpha = 0.003 * (40 - i) / 40
        ctx.set_source_rgba(0.80, 0.85, 0.92, alpha)
        ctx.arc(WIDTH * 0.3, HEIGHT * 0.25, i * 15, 0, 2 * math.pi)
        ctx.fill()

    # Ultra-fine grid
    ctx.set_source_rgba(LIGHT_ACCENT[0], LIGHT_ACCENT[1], LIGHT_ACCENT[2], 0.25)
    ctx.set_line_width(0.3)

    for i in range(WIDTH // 40 + 1):
        ctx.move_to(i * 40, 0)
        ctx.line_to(i * 40, HEIGHT)
        ctx.stroke()
    for i in range(HEIGHT // 40 + 1):
        ctx.move_to(0, i * 40)
        ctx.line_to(WIDTH, i * 40)
        ctx.stroke()

    # === Hero Typography - Chinese ===
    setup_chinese_font(ctx, 150, bold=True)

    lines = [
        ("文档", DARK_TEXT, 200),
        ("一键", GOLD, 380),
        ("变 PPT", DARK_TEXT, 560),
    ]

    for text, color, y in lines:
        ctx.set_source_rgb(*color)
        ctx.move_to(80, y)
        ctx.show_text(text)

    # Decorative line
    ctx.set_source_rgb(*GOLD)
    ctx.set_line_width(3)
    ctx.move_to(80, 610)
    ctx.line_to(500, 610)
    ctx.stroke()

    # Subtle glow under line
    ctx.set_source_rgba(*GOLD, 0.15)
    ctx.set_line_width(12)
    ctx.move_to(80, 610)
    ctx.line_to(500, 610)
    ctx.stroke()

    # === Feature Cards ===
    card_y = 700
    card_height = 130
    margin_x = 80

    features = [
        ("01", "智能编排", "AI 自动规划大纲与排版"),
        ("02", "场景适配", "6 大专业场景模板"),
        ("03", "即时导出", "PDF · PPTX · HTML"),
    ]

    for i, (num, title, desc) in enumerate(features):
        y = card_y + i * (card_height + 20)

        # Card background with gradient feel
        ctx.set_source_rgba(LIGHT_ACCENT[0], LIGHT_ACCENT[1], LIGHT_ACCENT[2], 0.7)
        draw_rounded_rect(ctx, margin_x, y, WIDTH - margin_x * 2, card_height, 8)
        ctx.fill()

        # Left gold accent
        ctx.set_source_rgb(*GOLD)
        ctx.rectangle(margin_x, y + 20, 4, card_height - 40)
        ctx.fill()

        # Number
        ctx.set_source_rgb(*GOLD)
        setup_chinese_font(ctx, 42, bold=True)
        ctx.move_to(margin_x + 25, y + 55)
        ctx.show_text(num)

        # Vertical separator
        ctx.set_source_rgba(0.6, 0.6, 0.65, 0.3)
        ctx.set_line_width(1)
        ctx.move_to(margin_x + 100, y + 25)
        ctx.line_to(margin_x + 100, y + card_height - 25)
        ctx.stroke()

        # Title
        ctx.set_source_rgb(*DARK_TEXT)
        setup_chinese_font(ctx, 34, bold=True)
        ctx.move_to(margin_x + 130, y + 55)
        ctx.show_text(title)

        # Description
        ctx.set_source_rgba(0.3, 0.3, 0.35, 0.7)
        setup_chinese_font(ctx, 20, bold=False)
        ctx.move_to(margin_x + 130, y + 95)
        ctx.show_text(desc)

    # === Bottom CTA ===
    ctx.set_source_rgb(*GOLD)
    setup_chinese_font(ctx, 36, bold=True)
    ctx.move_to(80, HEIGHT - 160)
    ctx.show_text("SlideCraft")

    ctx.set_source_rgba(0.3, 0.3, 0.35, 0.6)
    setup_chinese_font(ctx, 18, bold=False)
    ctx.move_to(80, HEIGHT - 110)
    ctx.show_text("SlideCraft AI · 专业设计零门槛")

    # Corner marks
    ctx.set_source_rgb(*GOLD)
    ctx.set_line_width(1.5)

    # Top right
    ctx.move_to(WIDTH - 50, 50)
    ctx.line_to(WIDTH - 50, 100)
    ctx.move_to(WIDTH - 50, 50)
    ctx.line_to(WIDTH - 100, 50)
    ctx.stroke()

    # Bottom right
    ctx.move_to(WIDTH - 50, HEIGHT - 50)
    ctx.line_to(WIDTH - 50, HEIGHT - 100)
    ctx.move_to(WIDTH - 50, HEIGHT - 50)
    ctx.line_to(WIDTH - 100, HEIGHT - 50)
    ctx.stroke()

    surface.write_to_png(os.path.join(OUTPUT_DIR, "02_social_poster.png"))
    print("Created: 02_social_poster.png")


def create_feature_diagram():
    """Create feature introduction diagram - landscape format"""
    WIDTH, HEIGHT = 1920, 1080
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)

    # Background
    ctx.set_source_rgb(*LIGHT_BG)
    ctx.rectangle(0, 0, WIDTH, HEIGHT)
    ctx.fill()

    # Ambient glow (soft)
    for i in range(30, 0, -1):
        alpha = 0.002 * (30 - i) / 30
        ctx.set_source_rgba(0.82, 0.87, 0.93, alpha)
        ctx.arc(WIDTH/2, HEIGHT * 0.4, i * 20, 0, 2 * math.pi)
        ctx.fill()

    # Dot grid
    ctx.set_source_rgba(LIGHT_ACCENT[0], LIGHT_ACCENT[1], LIGHT_ACCENT[2], 0.5)
    for x in range(0, WIDTH + 50, 50):
        for y in range(0, HEIGHT + 50, 50):
            ctx.arc(x, y, 1, 0, 2 * math.pi)
            ctx.fill()

    # === Header ===
    ctx.set_source_rgb(*DARK_TEXT)
    setup_chinese_font(ctx, 52, bold=True)
    ctx.move_to(100, 110)
    ctx.show_text("SlideCraft")

    ctx.set_source_rgb(*GOLD)
    ctx.move_to(100 + ctx.text_extents("SlideCraft").width + 15, 110)
    ctx.show_text("AI")

    ctx.set_source_rgba(*GOLD, 0.8)
    setup_chinese_font(ctx, 24, bold=False)
    ctx.move_to(100, 150)
    ctx.show_text("智能演示文稿生成平台")

    # === Workflow Steps ===
    flow_y = 380
    steps = [
        ("上传文档", "PDF · DOCX · MD · TXT"),
        ("AI 编排", "智能大纲与内容规划"),
        ("设计生成", "专业排版与可视化"),
        ("一键导出", "PDF · PPTX · HTML"),
    ]

    step_count = len(steps)
    total_width = WIDTH - 200
    step_spacing = total_width / step_count
    start_x = 100 + step_spacing / 2

    for i, (title, subtitle) in enumerate(steps):
        x = start_x + i * step_spacing

        # Circle with glow
        ctx.set_source_rgba(*GOLD, 0.1)
        ctx.arc(x, flow_y, 75, 0, 2 * math.pi)
        ctx.fill()

        # Circle outline
        ctx.set_source_rgb(*GOLD)
        ctx.set_line_width(2.5)
        ctx.arc(x, flow_y, 55, 0, 2 * math.pi)
        ctx.stroke()

        # Inner circle
        ctx.set_source_rgba(LIGHT_BG[0], LIGHT_BG[1], LIGHT_BG[2], 0.9)
        ctx.arc(x, flow_y, 52, 0, 2 * math.pi)
        ctx.fill()

        # Number
        ctx.set_source_rgb(*GOLD)
        setup_chinese_font(ctx, 36, bold=True)
        num = str(i + 1)
        ext = ctx.text_extents(num)
        ctx.move_to(x - ext.width/2, flow_y + ext.height/3)
        ctx.show_text(num)

        # Connector
        if i < step_count - 1:
            next_x = start_x + (i + 1) * step_spacing
            ctx.set_source_rgba(*GOLD, 0.5)
            ctx.set_line_width(1.5)
            ctx.set_dash([8, 6])
            ctx.move_to(x + 65, flow_y)
            ctx.line_to(next_x - 65, flow_y)
            ctx.stroke()
            ctx.set_dash([])

            # Arrow
            ctx.set_source_rgb(*GOLD)
            arrow_x = next_x - 68
            ctx.move_to(arrow_x + 8, flow_y)
            ctx.line_to(arrow_x, flow_y - 6)
            ctx.line_to(arrow_x, flow_y + 6)
            ctx.close_path()
            ctx.fill()

        # Title
        ctx.set_source_rgb(*DARK_TEXT)
        setup_chinese_font(ctx, 26, bold=True)
        ext = ctx.text_extents(title)
        ctx.move_to(x - ext.width/2, flow_y + 95)
        ctx.show_text(title)

        # Subtitle
        ctx.set_source_rgba(0.3, 0.3, 0.35, 0.65)
        setup_chinese_font(ctx, 16, bold=False)
        ext = ctx.text_extents(subtitle)
        ctx.move_to(x - ext.width/2, flow_y + 125)
        ctx.show_text(subtitle)

    # === Scenario Cards ===
    card_y = 680
    card_width = 270
    card_height = 200
    card_gap = 28
    scenarios = [
        ("咨询研究", "#003366", "战略报告 · 政府汇报"),
        ("年终述职", "#1A365D", "工作总结 · 述职报告"),
        ("学术答辩", "#1E3A8A", "论文答辩 · 研究分享"),
        ("公司介绍", "#0A0A0A", "项目路演 · 产品发布"),
        ("创意营销", "#6C5CE7", "品牌推广 · 营销方案"),
        ("政府公文", "#8B0000", "政策解读 · 党建汇报"),
    ]

    total_cards_width = len(scenarios) * card_width + (len(scenarios) - 1) * card_gap
    start_card_x = (WIDTH - total_cards_width) / 2

    for i, (name, color_hex, desc) in enumerate(scenarios):
        x = start_card_x + i * (card_width + card_gap)

        r = int(color_hex[1:3], 16) / 255
        g = int(color_hex[3:5], 16) / 255
        b = int(color_hex[5:7], 16) / 255

        # Card shadow
        ctx.set_source_rgba(0, 0, 0, 0.2)
        draw_rounded_rect(ctx, x + 4, card_y + 4, card_width, card_height, 10)
        ctx.fill()

        # Card body
        ctx.set_source_rgba(r, g, b, 0.85)
        draw_rounded_rect(ctx, x, card_y, card_width, card_height, 10)
        ctx.fill()

        # Top gold accent
        ctx.set_source_rgb(*GOLD)
        ctx.rectangle(x + 20, card_y, card_width - 40, 3)
        ctx.fill()

        # Mini slide preview
        preview_x = x + 25
        preview_y = card_y + 30
        preview_w = card_width - 50
        preview_h = 95

        ctx.set_source_rgb(*OFF_WHITE)
        draw_rounded_rect(ctx, preview_x, preview_y, preview_w, preview_h, 4)
        ctx.fill()

        # Preview header
        ctx.set_source_rgb(*GOLD)
        ctx.rectangle(preview_x, preview_y, preview_w, 18)
        ctx.fill()

        # Preview content
        ctx.set_source_rgba(r, g, b, 0.5)
        ctx.rectangle(preview_x + 12, preview_y + 32, 80, 6)
        ctx.fill()
        ctx.rectangle(preview_x + 12, preview_y + 45, 100, 5)
        ctx.fill()
        ctx.rectangle(preview_x + 12, preview_y + 56, 70, 5)
        ctx.fill()

        # Mini chart
        ctx.set_source_rgb(*GOLD)
        bar_x = preview_x + preview_w - 55
        heights = [20, 28, 22]
        for j, h in enumerate(heights):
            ctx.rectangle(bar_x + j * 14, preview_y + 75 - h, 10, h)
            ctx.fill()

        # Scenario name
        ctx.set_source_rgb(*PURE_WHITE)
        setup_chinese_font(ctx, 20, bold=True)
        ext = ctx.text_extents(name)
        ctx.move_to(x + card_width/2 - ext.width/2, card_y + 155)
        ctx.show_text(name)

        # Description
        ctx.set_source_rgba(1, 1, 1, 0.6)
        setup_chinese_font(ctx, 12, bold=False)
        ext = ctx.text_extents(desc)
        ctx.move_to(x + card_width/2 - ext.width/2, card_y + 180)
        ctx.show_text(desc)

    # Footer
    ctx.set_source_rgba(0.3, 0.3, 0.35, 0.5)
    setup_chinese_font(ctx, 16, bold=False)
    footer = "6 大专业场景 · 智能适配 · 一键生成"
    ext = ctx.text_extents(footer)
    ctx.move_to(WIDTH/2 - ext.width/2, HEIGHT - 45)
    ctx.show_text(footer)

    # Corner marks
    ctx.set_source_rgb(*GOLD)
    ctx.set_line_width(1.5)

    ctx.move_to(50, 50)
    ctx.line_to(50, 100)
    ctx.move_to(50, 50)
    ctx.line_to(100, 50)
    ctx.stroke()

    ctx.move_to(WIDTH - 50, HEIGHT - 50)
    ctx.line_to(WIDTH - 50, HEIGHT - 100)
    ctx.move_to(WIDTH - 50, HEIGHT - 50)
    ctx.line_to(WIDTH - 100, HEIGHT - 50)
    ctx.stroke()

    surface.write_to_png(os.path.join(OUTPUT_DIR, "03_feature_diagram.png"))
    print("Created: 03_feature_diagram.png")


def create_minimal_logo():
    """Create minimal app icon"""
    WIDTH, HEIGHT = 512, 512
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
    ctx = cairo.Context(surface)

    # Background - light
    ctx.set_source_rgb(*LIGHT_BG_ALT)
    ctx.rectangle(0, 0, WIDTH, HEIGHT)
    ctx.fill()

    center = WIDTH / 2

    # Document icon (top-left quadrant feel)
    doc_x, doc_y = center - 85, center - 110
    doc_w, doc_h = 90, 110

    # Shadow
    ctx.set_source_rgba(0, 0, 0, 0.3)
    draw_rounded_rect(ctx, doc_x + 4, doc_y + 4, doc_w, doc_h, 6)
    ctx.fill()

    # Document body
    ctx.set_source_rgb(*OFF_WHITE)
    draw_rounded_rect(ctx, doc_x, doc_y, doc_w, doc_h, 6)
    ctx.fill()

    # Document lines
    ctx.set_source_rgba(DEEP_NAVY[0], DEEP_NAVY[1], DEEP_NAVY[2], 0.5)
    ctx.set_line_width(5)
    ctx.move_to(doc_x + 15, doc_y + 35)
    ctx.line_to(doc_x + 65, doc_y + 35)
    ctx.stroke()
    ctx.set_line_width(4)
    ctx.move_to(doc_x + 15, doc_y + 55)
    ctx.line_to(doc_x + 55, doc_y + 55)
    ctx.stroke()
    ctx.move_to(doc_x + 15, doc_y + 73)
    ctx.line_to(doc_x + 60, doc_y + 73)
    ctx.stroke()

    # Arrow
    ctx.set_source_rgb(*GOLD)
    arrow_y = center
    ctx.move_to(center + 5, arrow_y - 25)
    ctx.line_to(center + 35, arrow_y)
    ctx.line_to(center + 5, arrow_y + 25)
    ctx.close_path()
    ctx.fill()

    # Slide icon (bottom-right quadrant feel)
    slide_x, slide_y = center - 5, center + 30
    slide_w, slide_h = 100, 65

    # Shadow
    ctx.set_source_rgba(0, 0, 0, 0.3)
    draw_rounded_rect(ctx, slide_x + 4, slide_y + 4, slide_w, slide_h, 5)
    ctx.fill()

    # Slide body
    ctx.set_source_rgb(*OFF_WHITE)
    draw_rounded_rect(ctx, slide_x, slide_y, slide_w, slide_h, 5)
    ctx.fill()

    # Golden header
    ctx.set_source_rgb(*GOLD)
    ctx.rectangle(slide_x, slide_y, slide_w, 14)
    ctx.fill()

    # Content lines
    ctx.set_source_rgba(DEEP_NAVY[0], DEEP_NAVY[1], DEEP_NAVY[2], 0.4)
    ctx.rectangle(slide_x + 10, slide_y + 28, 35, 5)
    ctx.fill()
    ctx.rectangle(slide_x + 10, slide_y + 40, 45, 4)
    ctx.fill()

    # Mini bars
    ctx.set_source_rgb(*GOLD)
    ctx.rectangle(slide_x + 65, slide_y + 28, 8, 20)
    ctx.fill()
    ctx.rectangle(slide_x + 78, slide_y + 35, 8, 13)
    ctx.fill()

    surface.write_to_png(os.path.join(OUTPUT_DIR, "04_logo_icon.png"))
    print("Created: 04_logo_icon.png")


# Execute
if __name__ == "__main__":
    create_logo_design()
    create_social_poster()
    create_feature_diagram()
    create_minimal_logo()
    print("\n✅ All visual assets created with Chinese font support")
