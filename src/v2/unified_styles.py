"""
统一样式系统 - 确保每一页的样式一致

核心理念：
1. 预定义 CSS 类名 - AI 只需要选择类名，不需要写内联样式
2. 统一的页面结构 - 标题区、内容区、结论区的位置固定
3. ECharts 图表支持 - 提供标准的图表代码模板
"""


def generate_unified_css(primary_color: str = "#003366") -> str:
    """生成统一的 CSS 样式"""
    
    # 根据主色计算其他颜色
    accent_color = _lighten_color(primary_color, 0.3)
    
    return f"""
/* ============================================
   统一样式系统 - V2 版本
   确保每一页的样式严格一致
   ============================================ */

/* ============================================
   字体嵌入 - 确保 PDF 中的字体可编辑
   ============================================ */

/* Web 字体加载 - 思源黑体 (Noto Sans SC) */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap');

/* 定义可编辑的 Web 字体 */
@font-face {{
    font-family: 'Presentation Font';
    src: local('Noto Sans SC'), 
         local('Microsoft YaHei'), 
         local('微软雅黑'),
         url('https://fonts.gstatic.com/s/notosanssc/v36/k3kCo84MPvpLmixcA63oedfCh2BO5p-8.woff2') format('woff2');
    font-weight: 400;
    font-style: normal;
    font-display: swap;
}}

@font-face {{
    font-family: 'Presentation Font';
    src: local('Noto Sans SC Bold'), 
         local('Microsoft YaHei Bold'),
         url('https://fonts.gstatic.com/s/notosanssc/v36/k3kCo84MPvpLmixcA63oedfCh2BO5p-8.woff2') format('woff2');
    font-weight: 700;
    font-style: normal;
    font-display: swap;
}}

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
    
    /* 字体 - 使用嵌入字体，确保 PDF 可编辑 */
    --font-family: 'Presentation Font', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
    
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
    letter-spacing: 0.02em;
    word-break: keep-all;       /* 防止中文掉行 */
    overflow-wrap: break-word;  /* 长英文单词可换行 */
    max-width: 100%;            /* 确保标题使用全部可用宽度 */
}}

.slide-subtitle {{
    font-size: 16px;
    color: var(--text-secondary);
    margin-top: 8px;
    line-height: 1.5;
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
    word-break: keep-all;
}}

.card-content {{
    font-size: 15px;
    color: var(--text-secondary);
    line-height: 1.6;
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
    letter-spacing: 0.02em;
}}

.cover-subtitle {{
    font-size: 20px;
    color: var(--text-secondary);
    margin-top: 16px;
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
    letter-spacing: 0.03em;
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
