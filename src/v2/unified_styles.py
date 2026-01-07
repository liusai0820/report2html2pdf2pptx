"""
统一样式系统 - 确保每一页的样式一致

核心理念：
1. 预定义 CSS 类名 - AI 只需要选择类名，不需要写内联样式
2. 统一的页面结构 - 标题区、内容区、结论区的位置固定
3. ECharts 图表支持 - 提供标准的图表代码模板
"""

# 字体族预设 - 使用 Docker 容器中已安装的字体
# fonts-noto-cjk: Noto Sans CJK SC (思源黑体), Noto Serif CJK SC (思源宋体)
# fonts-arphic-ukai: AR PL UKai CN (文鼎楷体)
# fonts-arphic-uming: AR PL UMing CN (文鼎明体)
FONT_FAMILIES = {
    "modern": {
        # 现代风格 - 黑体系（思源黑体）
        # Docker 中安装的字体名: 'Noto Sans CJK SC'
        "primary": "'Noto Sans CJK SC', 'PingFang SC', 'Microsoft YaHei', 'Heiti SC', sans-serif",
        "display_name": "现代简约（黑体）",
        "use_local": True,
    },
    "classic": {
        # 典雅风格 - 楷体系
        # Docker 中安装的字体名: 'AR PL UKai CN' (文鼎楷体)
        # 备选: 'Noto Serif CJK SC' (思源宋体)
        "primary": "'AR PL UKai CN', 'Noto Serif CJK SC', 'STKaiti', 'KaiTi', 'Songti SC', serif",
        "display_name": "典雅庄重（楷体）",
        "use_local": True,
    }
}


def generate_unified_css(primary_color: str = "#003366", font_style: str = "modern") -> str:
    """生成统一的 CSS 样式
    
    Args:
        primary_color: 主题色
        font_style: 字体风格，'modern' (黑体) 或 'classic' (楷体)
    """
    
    # 根据主色计算其他颜色
    accent_color = _lighten_color(primary_color, 0.3)
    
    # 获取字体配置
    font_config = FONT_FAMILIES.get(font_style, FONT_FAMILIES["modern"])
    font_family = font_config["primary"]
    
    # 使用系统本地字体，不需要 @font-face 和网络加载
    # 这样可以避免 Type3 字体问题，因为 Puppeteer 直接使用系统字体
    font_face_css = """
/* 使用系统本地字体 - 无需网络加载 */
/* Docker 容器中已安装: fonts-noto-cjk (Noto Sans CJK SC) */
"""
    
    return f"""
/* ============================================
   统一样式系统 - V2 版本
   确保每一页的样式严格一致
   字体风格: {font_config['display_name']}
   ============================================ */

/* ============================================
   字体策略 - 使用系统本地字体
   
   核心策略：
   1. Docker 容器中已安装 fonts-noto-cjk (思源黑体)
   2. 直接使用系统字体，避免网络加载失败
   3. Puppeteer 使用系统字体生成 PDF，确保可编辑
   ============================================ */

{font_face_css}

/* 全局变量 */
:root {{
    /* 品牌色 */
    --primary: {primary_color};
    --primary-light: {accent_color};
    --accent: #f59e0b;
    
    /* 文字色 */
    --text-primary: #1f2937;
    --text-secondary: #6b7280;
    --text-light: #9ca3af;
    --text-inverse: #ffffff;
    
    /* 背景色 */
    --bg-white: #ffffff;
    --bg-gray: #f5f7fa;
    --bg-dark: {primary_color};
    
    /* 边框 */
    --border-color: #e5e7eb;
    
    /* 语义色 */
    --success: #10b981;
    --danger: #ef4444;
    --warning: #f59e0b;
    
    /* 字体 - 根据风格动态设置 */
    --font-family: {font_family};
    
    /* 画布尺寸 */
    --slide-width: 1280px;
    --slide-height: 720px;
    --padding-x: 60px;
    --padding-top: 50px;
    --padding-bottom: 40px;
}}

/* 全局重置 */
* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    /* 全局字间距 - 补偿 Adobe PPTX 转换时的紧缩 */
    letter-spacing: 0.05em;
}}

/* 强制全局字体覆盖 - 确保所有元素使用系统字体 */
/* 使用多重选择器和 !important 来覆盖内联样式 */
html, body, body *,
div, span, p, h1, h2, h3, h4, h5, h6,
table, tr, td, th,
ul, ol, li,
[style*="font-family"] {{
    font-family: {font_family} !important;
}}

/* ============================================
   基础容器
   ============================================ */

.slide {{
    width: var(--slide-width);
    height: var(--slide-height);
    background: var(--bg-white);
    font-family: var(--font-family);
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    padding: var(--padding-top) var(--padding-x) var(--padding-bottom);
}}

/* ============================================
   标题区 - 每页固定结构
   ============================================ */

.slide-header {{
    flex-shrink: 0;
    margin-bottom: 32px;
    width: 100%;
}}

.slide-title {{
    font-size: 32px;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.35;
    margin: 0;
    letter-spacing: 0.1em;        /* 大标题需要更大字间距 */
    word-break: keep-all;         /* 防止中文掉行 */
    overflow-wrap: break-word;    /* 长英文单词可换行 */
    max-width: 100%;              /* 确保标题使用全部可用宽度 */
}}

.slide-subtitle {{
    font-size: 16px;
    color: var(--text-secondary);
    margin-top: 8px;
    line-height: 1.5;
    letter-spacing: 0.08em;       /* 增加字间距 */
    word-break: keep-all;
}}

/* ============================================
   内容区 - 自动填充剩余空间
   ============================================ */

.slide-body {{
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 0; /* 防止 flex 子项溢出 */
}}

/* ============================================
   结论区 - 固定在底部
   ============================================ */

.slide-footer {{
    flex-shrink: 0;
    margin-top: auto;
    padding-top: 24px;
}}

.conclusion-box {{
    background: var(--bg-gray);
    padding: 16px 20px;
    border-left: 4px solid var(--primary);
}}

.conclusion-text {{
    font-size: 16px;
    font-weight: 600;
    color: var(--primary);
    line-height: 1.5;
}}

/* ============================================
   布局系统
   ============================================ */

/* 两栏布局 */
.layout-two-col {{
    display: flex;
    gap: 40px;
    flex: 1;
}}

.layout-two-col > .col {{
    flex: 1;
    display: flex;
    flex-direction: column;
}}

/* 三栏布局 */
.layout-three-col {{
    display: flex;
    gap: 24px;
    flex: 1;
}}

.layout-three-col > .col {{
    flex: 1;
}}

/* 卡片网格 */
.card-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
}}

.card-grid-2 {{
    grid-template-columns: repeat(2, 1fr);
}}

/* ============================================
   卡片组件
   ============================================ */

.card {{
    background: var(--bg-gray);
    border-radius: 8px;
    padding: 24px;
}}

.card-title {{
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 12px;
    letter-spacing: 0.08em;
    word-break: keep-all;
}}

.card-content {{
    font-size: 15px;
    color: var(--text-secondary);
    line-height: 1.6;
    letter-spacing: 0.06em;
}}

/* 数据卡片 */
.data-card {{
    background: var(--bg-gray);
    border-radius: 8px;
    padding: 24px;
    text-align: center;
}}

.data-value {{
    font-size: 48px;
    font-weight: 700;
    color: var(--primary);
    line-height: 1.2;
}}

.data-label {{
    font-size: 14px;
    color: var(--text-secondary);
    margin-top: 8px;
    letter-spacing: 0.08em;
    word-break: keep-all;
}}

.data-trend {{
    font-size: 14px;
    margin-top: 8px;
}}

.data-trend.up {{
    color: var(--success);
}}

.data-trend.down {{
    color: var(--danger);
}}

/* ============================================
   列表样式
   ============================================ */

.list {{
    list-style: none;
    padding: 0;
}}

.list li {{
    font-size: 18px;
    color: var(--text-primary);
    line-height: 1.6;
    padding: 12px 0;
    padding-left: 24px;
    position: relative;
    border-bottom: 1px solid var(--border-color);
    letter-spacing: 0.06em;
    word-break: keep-all;
}}

.list li:last-child {{
    border-bottom: none;
}}

.list li::before {{
    content: '';
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 8px;
    height: 8px;
    background: var(--primary);
    border-radius: 2px;
}}

/* 简洁列表 */
.list-simple li {{
    border-bottom: none;
    padding: 8px 0;
}}

/* ============================================
   表格样式
   ============================================ */

.table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 15px;
}}

.table th {{
    text-align: left;
    padding: 12px 16px;
    background: var(--bg-gray);
    color: var(--text-primary);
    font-weight: 600;
    border-bottom: 2px solid var(--primary);
}}

.table td {{
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-color);
    color: var(--text-primary);
}}

.table tr:last-child td {{
    border-bottom: none;
}}

/* ============================================
   图表容器
   ============================================ */

.chart-container {{
    width: 100%;
    height: 350px;
    position: relative;
}}

.chart {{
    width: 100%;
    height: 100%;
}}

/* ============================================
   特殊页面 - 封面
   ============================================ */

.slide-cover {{
    justify-content: center;
    align-items: flex-start; /* 左对齐 */
    text-align: left;
    padding-left: 140px !important; /* 让出左侧边栏空间 */
}}

/* 左侧装饰栏 */
.left-bar {{
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 60px;
    background: linear-gradient(180deg, var(--primary) 0%, var(--primary-dark, #001a33) 100%);
    z-index: 10;
}}

/* 顶部装饰圆 */
.top-deco {{
    position: absolute;
    top: -100px;
    right: -50px;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(59,130,246,0.05) 0%, rgba(255,255,255,0) 70%);
    border-radius: 50%;
    pointer-events: none;
}}

/* 封面内容容器 */
.cover-content {{
    width: 100%;
    padding-top: 40px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    position: relative;
    z-index: 5;
}}

/* 封面徽章 */
.cover-badge {{
    display: inline-flex;
    align-items: center;
    gap: 12px;
    padding: 8px 0;
    margin-bottom: 30px;
    border-bottom: 2px solid var(--accent);
}}

.badge-text {{
    font-size: 18px;
    font-weight: 700;
    color: var(--primary);
    letter-spacing: 1px;
    text-transform: uppercase;
}}

.cover-title {{
    font-size: 56px;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.25;
    max-width: 950px;             /* 稍微增加最大宽度 */
    margin-bottom: 24px;
    word-wrap: break-word;        /* 允许长单词换行 */
    overflow-wrap: break-word;    /* 标准属性 */
    letter-spacing: -0.02em;
}}

.cover-subtitle {{
    font-size: 24px;
    color: var(--text-secondary);
    margin-top: 0;
    margin-bottom: 40px;
    padding-left: 20px;
    border-left: 4px solid var(--primary-light);
    letter-spacing: 0.05em;
    line-height: 1.5;
}}

/* 封面信息网格 */
.cover-info-grid {{
    margin-top: 140px;            /* 大幅增加顶部间距，使其靠下 */
    display: grid;
    grid-template-columns: auto auto;
    gap: 20px 80px;               /* 增加列间距 */
    max-width: 900px;
}}

.cover-footer-item {{
    display: flex;
    flex-direction: column;
    gap: 4px;
}}

.cover-label {{
    font-size: 14px;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 1px;
    opacity: 0.8;
}}

.cover-value {{
    font-size: 20px;
    color: var(--text-primary);
    font-weight: 600;
}}

.cover-meta {{
    /* 兼容旧逻辑，隐藏备用 */
    display: none;
}}

/* ============================================
   特殊页面 - 章节
   ============================================ */

.slide-section {{
    background: var(--bg-dark);
    justify-content: center;
    align-items: center;
}}

.section-number {{
    font-size: 72px;
    font-weight: 300;
    color: rgba(255, 255, 255, 0.3);
    margin-bottom: 16px;
}}

.section-divider {{
    width: 40px;
    height: 2px;
    background: rgba(255, 255, 255, 0.5);
    margin-bottom: 24px;
}}

.section-title {{
    font-size: 36px;
    font-weight: 700;
    color: var(--text-inverse);
    word-break: keep-all;
    letter-spacing: 0.12em;    /* 章节标题 */
}}

/* ============================================
   特殊页面 - 目录
   ============================================ */

.agenda-list {{
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding: 20px 0;
}}

.agenda-item {{
    display: flex;
    align-items: center;
    gap: 24px;
    padding-bottom: 20px;
    border-bottom: 1px solid var(--border-color);
}}

.agenda-item:last-child {{
    border-bottom: none;
}}

.agenda-number {{
    font-size: 24px;
    font-weight: 700;
    color: var(--primary);
    min-width: 40px;
}}

.agenda-title {{
    font-size: 20px;
    color: var(--text-primary);
    word-break: keep-all;
}}

/* ============================================
   特殊页面 - 结尾
   ============================================ */

.slide-closing {{
    justify-content: center;
    align-items: center;
}}

.closing-text {{
    font-size: 48px;
    font-weight: 700;
    color: var(--primary);
}}

.closing-org {{
    font-size: 16px;
    color: var(--text-secondary);
    margin-top: 24px;
}}

/* ============================================
   辅助类
   ============================================ */

.text-primary {{ color: var(--text-primary); }}
.text-secondary {{ color: var(--text-secondary); }}
.text-accent {{ color: var(--primary); }}
.text-success {{ color: var(--success); }}
.text-danger {{ color: var(--danger); }}

.font-bold {{ font-weight: 700; }}
.font-medium {{ font-weight: 500; }}

.text-center {{ text-align: center; }}
.text-right {{ text-align: right; }}

.mt-auto {{ margin-top: auto; }}
.mb-4 {{ margin-bottom: 16px; }}
.mb-6 {{ margin-bottom: 24px; }}

/* ============================================
   打印优化
   ============================================ */

@media print {{
    .slide {{
        break-inside: avoid;
        page-break-after: always;
    }}
}}
"""


def _lighten_color(hex_color: str, amount: float) -> str:
    """使颜色变亮"""
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = min(255, int(r + (255 - r) * amount))
    g = min(255, int(g + (255 - g) * amount))
    b = min(255, int(b + (255 - b) * amount))
    return f"#{r:02x}{g:02x}{b:02x}"


# ECharts 图表模板
ECHARTS_BAR_TEMPLATE = """
<div class="chart-container">
    <div id="chart_{chart_id}" class="chart"></div>
</div>
<script>
(function() {{
    var chart = echarts.init(document.getElementById('chart_{chart_id}'));
    var option = {{
        animation: false,
        color: ['{primary}', '{accent}', '#8893a1'],
        title: {{ text: '{title}', textStyle: {{ fontSize: 14, fontWeight: 'normal' }} }},
        tooltip: {{ trigger: 'axis' }},
        grid: {{ top: 50, bottom: 30, left: 50, right: 20, containLabel: true }},
        xAxis: {{
            type: 'category',
            data: {x_data},
            axisLabel: {{ fontSize: 12 }}
        }},
        yAxis: {{
            type: 'value',
            axisLabel: {{ fontSize: 12 }},
            splitLine: {{ lineStyle: {{ type: 'dashed' }} }}
        }},
        series: [{{
            data: {y_data},
            type: 'bar',
            barWidth: '50%',
            itemStyle: {{ borderRadius: [4, 4, 0, 0] }}
        }}]
    }};
    chart.setOption(option);
}})();
</script>
"""

ECHARTS_LINE_TEMPLATE = """
<div class="chart-container">
    <div id="chart_{chart_id}" class="chart"></div>
</div>
<script>
(function() {{
    var chart = echarts.init(document.getElementById('chart_{chart_id}'));
    var option = {{
        animation: false,
        color: ['{primary}', '{accent}', '#8893a1'],
        title: {{ text: '{title}', textStyle: {{ fontSize: 14, fontWeight: 'normal' }} }},
        tooltip: {{ trigger: 'axis' }},
        grid: {{ top: 50, bottom: 30, left: 50, right: 20, containLabel: true }},
        xAxis: {{
            type: 'category',
            data: {x_data},
            axisLabel: {{ fontSize: 12 }}
        }},
        yAxis: {{
            type: 'value',
            axisLabel: {{ fontSize: 12 }},
            splitLine: {{ lineStyle: {{ type: 'dashed' }} }}
        }},
        series: [{{
            data: {y_data},
            type: 'line',
            smooth: true,
            lineStyle: {{ width: 3 }},
            areaStyle: {{ opacity: 0.1 }}
        }}]
    }};
    chart.setOption(option);
}})();
</script>
"""

ECHARTS_PIE_TEMPLATE = """
<div class="chart-container">
    <div id="chart_{chart_id}" class="chart"></div>
</div>
<script>
(function() {{
    var chart = echarts.init(document.getElementById('chart_{chart_id}'));
    var option = {{
        animation: false,
        color: ['{primary}', '{accent}', '#8893a1', '#64748b', '#94a3b8'],
        title: {{ text: '{title}', textStyle: {{ fontSize: 14, fontWeight: 'normal' }} }},
        tooltip: {{ trigger: 'item' }},
        series: [{{
            type: 'pie',
            radius: ['40%', '70%'],
            center: ['50%', '55%'],
            data: {data},
            label: {{
                formatter: '{{b}}: {{d}}%',
                fontSize: 12
            }}
        }}]
    }};
    chart.setOption(option);
}})();
</script>
"""
