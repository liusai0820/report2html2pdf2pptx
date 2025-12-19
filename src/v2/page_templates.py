"""
页面模板 Prompt - 确保样式一致性

核心思想：
1. 给 AI 预定义的 HTML 结构模板
2. AI 只需要填充内容，不需要设计样式
3. 支持 ECharts 图表生成
"""


# ============================================================================
# 系统提示词 - 强调样式一致性
# ============================================================================

SYSTEM_PROMPT_V3 = """
# 你是一位专业的演示文稿内容生成专家

你的任务是将信息填充到预定义的 HTML 模板中，确保每一页的样式严格一致。

## 🎯 核心原则

### 1. 样式一致性（最重要）
- 使用预定义的 CSS 类名，**不要写任何内联样式**
- 每页结构统一：标题区 → 内容区 → 结论区
- 字号、间距、颜色都由 CSS 类控制

### 2. 内容忠实度
- 所有内容必须来自原始素材
- **禁止编造数据**（如果没有数据，就不要写数据卡片）
- 可以提炼、总结、润色，但不能改变原意

### 3. 防溢出约束
- 列表项最多 4 条，每条不超过 40 字
- 卡片最多 3 个
- 表格最多 5 行
- 整页文字不超过 300 字

### 4. 图表生成（重要）
- 当内容包含数据趋势、对比、分布时，优先使用图表
- 使用提供的 ECharts 模板代码
- 图表高度固定 350px

## 🚫 禁止事项

1. **禁止使用 style 属性** - 所有样式通过 class 控制
2. **禁止编造数据** - 没有的数据不要写
3. **禁止使用 Emoji** - 不要用 💡🚀 等图标
4. **禁止溢出** - 内容必须在页面范围内

## ✅ 必须做到

1. 使用预定义的 CSS 类名
2. 保持每页结构一致
3. 数据内容必须来自原文
4. 输出完整的 HTML 代码

## 📐 输出格式

直接输出 HTML 代码，不需要解释。
"""


# ============================================================================
# 页面模板 - 封面
# ============================================================================

def get_cover_template(title: str, org: str, date: str) -> str:
    return f'''<div class="slide slide-cover">
    <h1 class="cover-title">{title}</h1>
    <div class="cover-meta">
        <span>汇报单位：{org}</span>
        <span>{date}</span>
    </div>
</div>'''


# ============================================================================
# 页面模板 - 目录
# ============================================================================

def get_agenda_prompt(sections: str, colors: dict) -> str:
    return f"""
# 目录页生成

## 章节列表
{sections}

## 输出模板

请按以下结构输出 HTML：

```html
<div class="slide">
    <div class="slide-header">
        <h1 class="slide-title">目录</h1>
    </div>
    
    <div class="slide-body">
        <div class="agenda-list">
            <!-- 每个章节一行 -->
            <div class="agenda-item">
                <span class="agenda-number">01</span>
                <span class="agenda-title">第一章节标题</span>
            </div>
            <div class="agenda-item">
                <span class="agenda-number">02</span>
                <span class="agenda-title">第二章节标题</span>
            </div>
            <!-- 以此类推，最多 6 个章节 -->
        </div>
    </div>
</div>
```

直接输出 HTML，不要任何解释。
"""


# ============================================================================
# 页面模板 - 章节
# ============================================================================

def get_section_template(section_num: int, title: str) -> str:
    return f'''<div class="slide slide-section">
    <div class="section-number">0{section_num}</div>
    <div class="section-divider"></div>
    <h1 class="section-title">{title}</h1>
</div>'''


# ============================================================================
# 页面模板 - 结尾
# ============================================================================

def get_closing_template(org: str) -> str:
    return f'''<div class="slide slide-closing">
    <div class="closing-text">谢谢</div>
    <div class="closing-org">{org}</div>
</div>'''


# ============================================================================
# 正文页 Prompt - 核心
# ============================================================================

def get_content_prompt(
    page_num: int,
    total_pages: int,
    title: str,
    content: str,
    source_material: str,
    colors: dict
) -> str:
    return f"""
# 正文页生成（第 {page_num}/{total_pages} 页）

## 页面信息

### 标题（核心观点）
{title}

### 内容要点
{content}

### 原始素材
```
{source_material}
```

## 布局选择指南

根据内容类型选择最合适的布局：

### 布局 A：左右两栏（对比/分类内容）
```html
<div class="slide">
    <div class="slide-header">
        <h1 class="slide-title">标题文字</h1>
        <p class="slide-subtitle">简短的引导语</p>
    </div>
    
    <div class="slide-body">
        <div class="layout-two-col">
            <div class="col">
                <div class="card">
                    <h3 class="card-title">左侧标题</h3>
                    <ul class="list list-simple">
                        <li>要点一</li>
                        <li>要点二</li>
                    </ul>
                </div>
            </div>
            <div class="col">
                <div class="card">
                    <h3 class="card-title">右侧标题</h3>
                    <ul class="list list-simple">
                        <li>要点一</li>
                        <li>要点二</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
    
    <div class="slide-footer">
        <div class="conclusion-box">
            <p class="conclusion-text">一句话结论</p>
        </div>
    </div>
</div>
```

### 布局 B：三数据卡片（展示关键指标）
```html
<div class="slide">
    <div class="slide-header">
        <h1 class="slide-title">标题文字</h1>
    </div>
    
    <div class="slide-body">
        <div class="card-grid">
            <div class="data-card">
                <div class="data-value">数值</div>
                <div class="data-label">标签</div>
                <div class="data-trend up">↑ 增长描述</div>
            </div>
            <div class="data-card">
                <div class="data-value">数值</div>
                <div class="data-label">标签</div>
            </div>
            <div class="data-card">
                <div class="data-value">数值</div>
                <div class="data-label">标签</div>
            </div>
        </div>
    </div>
</div>
```

### 布局 C：列表+图表（趋势/统计数据）
```html
<div class="slide">
    <div class="slide-header">
        <h1 class="slide-title">标题文字</h1>
    </div>
    
    <div class="slide-body">
        <div class="layout-two-col">
            <div class="col">
                <ul class="list">
                    <li>第一个要点，不超过40字</li>
                    <li>第二个要点</li>
                    <li>第三个要点</li>
                </ul>
            </div>
            <div class="col">
                <!-- ECharts 图表 -->
                <div class="chart-container">
                    <div id="chart_page{page_num}" class="chart"></div>
                </div>
                <script>
                (function() {{
                    var chart = echarts.init(document.getElementById('chart_page{page_num}'));
                    var option = {{
                        animation: false,
                        color: ['{colors["primary"]}', '{colors["accent"]}'],
                        tooltip: {{ trigger: 'axis' }},
                        grid: {{ top: 30, bottom: 30, left: 50, right: 20 }},
                        xAxis: {{
                            type: 'category',
                            data: ['类别1', '类别2', '类别3', '类别4'],
                            axisLabel: {{ fontSize: 12 }}
                        }},
                        yAxis: {{
                            type: 'value',
                            axisLabel: {{ fontSize: 12 }}
                        }},
                        series: [{{
                            data: [120, 200, 150, 80],
                            type: 'bar',
                            barWidth: '50%'
                        }}]
                    }};
                    chart.setOption(option);
                }})();
                </script>
            </div>
        </div>
    </div>
    
    <div class="slide-footer">
        <div class="conclusion-box">
            <p class="conclusion-text">结论句子</p>
        </div>
    </div>
</div>
```

### 布局 D：纯列表（多个要点）
```html
<div class="slide">
    <div class="slide-header">
        <h1 class="slide-title">标题文字</h1>
        <p class="slide-subtitle">引导语</p>
    </div>
    
    <div class="slide-body">
        <ul class="list">
            <li>第一个要点，详细说明</li>
            <li>第二个要点，详细说明</li>
            <li>第三个要点，详细说明</li>
            <li>第四个要点（最多4条）</li>
        </ul>
    </div>
    
    <div class="slide-footer">
        <div class="conclusion-box">
            <p class="conclusion-text">一句话结论</p>
        </div>
    </div>
</div>
```

### 布局 E：表格（对比/矩阵）
```html
<div class="slide">
    <div class="slide-header">
        <h1 class="slide-title">标题文字</h1>
    </div>
    
    <div class="slide-body">
        <table class="table">
            <thead>
                <tr>
                    <th>列1</th>
                    <th>列2</th>
                    <th>列3</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>数据</td>
                    <td>数据</td>
                    <td>数据</td>
                </tr>
                <!-- 最多4行数据 -->
            </tbody>
        </table>
    </div>
</div>
```

## 图表使用指南

当原始素材包含以下内容时，使用图表：
- 时间序列数据（年度/季度趋势） → 折线图
- 类别比较（不同项目对比） → 柱状图  
- 占比分布（市场份额等） → 饼图

### 柱状图模板
```javascript
var option = {{
    animation: false,
    color: ['{colors["primary"]}'],
    tooltip: {{ trigger: 'axis' }},
    grid: {{ top: 30, bottom: 30, left: 50, right: 20 }},
    xAxis: {{
        type: 'category',
        data: ['标签1', '标签2', '标签3'],  // 替换为实际数据
        axisLabel: {{ fontSize: 12 }}
    }},
    yAxis: {{
        type: 'value',
        axisLabel: {{ fontSize: 12 }}
    }},
    series: [{{
        data: [100, 200, 150],  // 替换为实际数据
        type: 'bar',
        barWidth: '50%'
    }}]
}};
```

### 折线图模板
```javascript
var option = {{
    animation: false,
    color: ['{colors["primary"]}'],
    tooltip: {{ trigger: 'axis' }},
    grid: {{ top: 30, bottom: 30, left: 50, right: 20 }},
    xAxis: {{
        type: 'category',
        data: ['2020', '2021', '2022', '2023'],  // 替换为实际年份
        axisLabel: {{ fontSize: 12 }}
    }},
    yAxis: {{
        type: 'value',
        axisLabel: {{ fontSize: 12 }}
    }},
    series: [{{
        data: [100, 150, 200, 280],  // 替换为实际数据
        type: 'line',
        smooth: true
    }}]
}};
```

## ⚠️ 重要约束

1. **只使用 class 控制样式**，不要写任何 style 属性
2. **列表最多 4 条**，每条不超过 40 字
3. **图表数据必须来自原文**，不要编造
4. **必须包含结论区**（除非内容太少）

## 输出

根据内容选择最合适的布局，直接输出 HTML 代码，不要任何解释。
"""
