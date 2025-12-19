"""
统一样式系统 - 确保每一页的样式一致

核心理念：
1. 预定义 CSS 类名 - AI 只需要选择类名，不需要写内联样式
2. 统一的页面结构 - 标题区、内容区、结论区的位置固定
3. ECharts 图表支持 - 提供标准的图表代码模板
"""

# 字体族预设 - 使用 Web 字体确保 PDF 可编辑
# 关键：使用国内镜像 CDN，确保网络访问稳定
# fonts.loli.net 是 Google Fonts 的国内镜像
FONT_FAMILIES = {
    "modern": {
        # 现代风格 - 黑体系（思源黑体）
        "primary": "'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif",
        "display_name": "现代简约（黑体）",
        # 使用国内镜像 - fonts.loli.net
        "import_url": "https://fonts.loli.net/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap",
        # woff2 使用 gstatic.loli.net 镜像
        "woff2_url": "https://gstatic.loli.net/s/notosanssc/v26/k3kXo84MPvpLmixcA63oeALhLOCT-xWNm8Hqd37g1OkDRZe7lR4sg1IzSy-MNbE9VH8V.0.woff2"
    },
    "classic": {
        # 典雅风格 - 楷体系
        # 使用霞鹜文楷 (LXGW WenKai) 或 Ma Shan Zheng
        "primary": "'LXGW WenKai', 'Ma Shan Zheng', 'STKaiti', 'KaiTi', serif",
        "display_name": "典雅庄重（楷体）",
        # 使用国内镜像
        "import_url": "https://fonts.loli.net/css2?family=Ma+Shan+Zheng&family=LXGW+WenKai:wght@300;400;700&display=swap",
        # woff2 使用 gstatic.loli.net 镜像
        "woff2_url": "https://gstatic.loli.net/s/mashanzheng/v10/NaPecZTIAOuHOAAy39FUqIcU0PJoDQ.woff2"
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
    font_import_url = font_config["import_url"]
    
    # 根据字体风格生成不同的 @font-face
    if font_style == "classic":
        # 楷体风格 - 使用霞鹜文楷和 Ma Shan Zheng（国内镜像）
        font_face_css = """
/* @font-face 声明 - 楷体 (使用国内镜像确保访问) */
@font-face {
    font-family: 'LXGW WenKai';
    font-style: normal;
    font-weight: 400;
    font-display: swap;
    src: url(https://gstatic.loli.net/s/lxgwwenkai/v3/1cXxaULGY-g1qwHiY2yBe_-7VBs2JG_T.woff2) format('woff2');
    unicode-range: U+4E00-9FFF, U+3400-4DBF, U+20000-2A6DF, U+2A700-2B73F, U+2B740-2B81F, U+2B820-2CEAF, U+2CEB0-2EBEF, U+30000-3134F, U+31350-323AF, U+F900-FAFF, U+FE30-FE4F;
}
@font-face {
    font-family: 'Ma Shan Zheng';
    font-style: normal;
    font-weight: 400;
    font-display: swap;
    src: url(https://gstatic.loli.net/s/mashanzheng/v10/NaPecZTIAOuHOAAy39FUqIcU0PJoDQ.woff2) format('woff2');
    unicode-range: U+4E00-9FFF, U+3400-4DBF;
}
"""
    else:
        # 黑体风格 - 使用思源黑体（国内镜像）
        font_face_css = """
/* @font-face 声明 - 黑体 (使用国内镜像确保访问) */
@font-face {
    font-family: 'Noto Sans SC';
    font-style: normal;
    font-weight: 400;
    font-display: swap;
    src: url(https://gstatic.loli.net/s/notosanssc/v26/k3kXo84MPvpLmixcA63oeALhLOCT-xWNm8Hqd37g1OkDRZe7lR4sg1IzSy-MNbE9VH8V.0.woff2) format('woff2');
    unicode-range: U+4E00-9FFF, U+3400-4DBF, U+20000-2A6DF, U+2A700-2B73F, U+2B740-2B81F, U+2B820-2CEAF, U+2CEB0-2EBEF, U+30000-3134F, U+31350-323AF, U+F900-FAFF, U+FE30-FE4F;
}
@font-face {
    font-family: 'Noto Sans SC';
    font-style: normal;
    font-weight: 700;
    font-display: swap;
    src: url(https://gstatic.loli.net/s/notosanssc/v26/k3kXo84MPvpLmixcA63oeALhLOCT-xWNm8Hqd37g1OkDRZe7lR4sg1IzSy-MNbE9VH8V.0.woff2) format('woff2');
    unicode-range: U+4E00-9FFF, U+3400-4DBF;
}
"""
    
    return f"""
/* ============================================
   统一样式系统 - V2 版本
   确保每一页的样式严格一致
   字体风格: {font_config['display_name']}
   ============================================ */

/* ============================================
   字体嵌入 - 确保 PDF 中的字体可编辑，避免 Type3 字体
   
   核心策略：
   1. 使用 @font-face 显式声明 Web 字体
   2. 使用国内镜像 (fonts.loli.net / gstatic.loli.net) 确保访问稳定
   3. 这样 Puppeteer 会将字体嵌入 PDF
   ============================================ */

/* 字体导入（国内镜像） */
@import url('{font_import_url}');

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

/* 强制全局字体覆盖 - 确保所有元素使用 Web 字体 */
html, body, body * {{
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
    align-items: center;
    text-align: center;
}}

.cover-title {{
    font-size: 48px;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.35;
    max-width: 1000px;
    word-break: keep-all;
    letter-spacing: 0.12em;    /* 大标题需要更宽松的字间距 */
}}

.cover-subtitle {{
    font-size: 20px;
    color: var(--text-secondary);
    margin-top: 16px;
    letter-spacing: 0.1em;
}}

.cover-meta {{
    position: absolute;
    bottom: 60px;
    left: 0;
    right: 0;
    display: flex;
    justify-content: space-between;
    padding: 0 60px;
    font-size: 14px;
    color: var(--text-light);
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
