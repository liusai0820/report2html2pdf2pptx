"""
AI 编排器 - AI 原生的核心引擎

核心理念：
1. 最小化硬编码 - 让 AI 自己决定
2. 上下文驱动 - 所有信息作为上下文传递
3. 单一职责 - 只负责与 AI 交互
"""

import asyncio
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from rich.console import Console

from config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    DEFAULT_MODEL,
    TIMEOUT_SECONDS,
    MAX_RETRIES,
    RETRY_DELAY,
    TEMPERATURE,
)
from .context_builder import PresentationContext

console = Console()


# 核心系统提示词 - 这是唯一的"硬编码"，但它是元级别的指导
MASTER_SYSTEM_PROMPT = """
你是一位世界级的演示文稿设计专家，融合了麦肯锡的结构化思维、IDEO的设计思维、TED的演讲艺术。

## 你的核心能力

1. **金字塔思维**：结论先行，以上统下，归类分组，逻辑递进
2. **洞察提炼**：从海量信息中提炼关键洞察
3. **故事构建**：用 SCQA 框架构建有说服力的叙事
4. **视觉表达**：让复杂信息简单易懂

## 你的工作原则

### 内容原则
1. **一页一观点**：每页只传达一个核心信息
2. **标题即结论**：标题不是主题，是这页的核心观点
3. **数据说话**：用数字代替形容词，用事实代替观点
4. **So What**：每页都要回答"这意味着什么"

### 质量红线
1. **禁止编造**：没有的数据不写，没有的案例不编
2. **禁止废话**：删除所有没有信息量的表述
3. **禁止跳跃**：每个结论都要有依据
4. **禁止出现"So What"字样**：底部结论框直接写结论性语句，不要写"So What"这种提示词

### 输出规范
1. 使用预定义的 CSS 类名
2. 不生成 <style> 标签
3. 不生成 <header> 标签
4. 结构清晰，语义化

## 预定义 CSS 类名

- `.slide-container` - 幻灯片容器
- `.cover-slide` - 封面页
- `.section-slide` - 章节过场页
- `.content-area` - 内容区域
- `.page-title` - 页面标题（36px，结论式）
- `.sub-head` - 子标题（24px）
- `.big-list` - 大号列表（20px）
- `.data-card` - 数据卡片
- `.data-val` - 数据值（大号数字）
- `.data-lbl` - 数据标签
- `.bottom-box` - 底部结论框（So What）
- `.clean-table` - 表格
- `.chart-container` - 图表容器

## 你的任务

根据用户提供的上下文，生成高质量的演示文稿内容。
你会收到完整的背景信息，请根据这些信息自主决定最佳的呈现方式。
"""


class AIOrchestrator:
    """
    AI 编排器
    
    职责：
    1. 接收上下文
    2. 与 AI 交互
    3. 返回结果
    
    不做：
    1. 不做业务逻辑判断
    2. 不做模板选择
    3. 不做硬编码规则
    """
    
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.client = AsyncOpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
        )
    
    async def generate_outline(self, context: PresentationContext) -> List[Dict[str, Any]]:
        """
        生成大纲
        
        让 AI 根据完整上下文自主决定：
        - 分几个章节
        - 每章几页
        - 每页讲什么
        """
        prompt = f"""
{context.to_prompt_context()}

# 你的任务

请为这份演示文稿规划正文大纲（封面、目录、封底由系统自动生成，你只需规划正文内容）。

## 输出要求

1. 每行一条，格式：`类型|标题|内容要点`
2. 类型只有两种：
   - SECTION：章节分隔页（如"第一部分 xxx"）
   - CONTENT：正文内容页
3. 不要生成 COVER、AGENDA、CLOSING 类型（系统会自动添加）
4. 标题必须是结论，不是主题
5. 内容要点要具体，包含关键数据和观点

## 示例

SECTION|第一部分 市场洞察|
CONTENT|市场规模5年翻倍，年复合增长率达23%|2023年500亿，2028年预计1200亿；驱动因素：政策+技术+需求
CONTENT|头部三家占70%份额，格局已定|A公司35%、B公司20%、C公司15%；中小企业空间被压缩
SECTION|第二部分 竞争分析|
CONTENT|技术壁垒是核心护城河|专利数量、研发投入、人才储备三大指标领先

请开始规划（目标约{context.target_pages}页正文内容）：
"""
        
        response = await self._generate(prompt)
        return self._parse_outline(response)
    
    async def generate_page(
        self,
        context: PresentationContext,
        page_info: Dict[str, Any],
        page_num: int,
        total_pages: int
    ) -> str:
        """
        生成单页内容
        
        让 AI 根据上下文和页面信息自主决定：
        - 用什么布局
        - 放什么内容
        - 怎么呈现
        """
        page_type = page_info.get("type", "CONTENT")
        title = page_info.get("title", "")
        content_hints = page_info.get("content", "")
        
        prompt = self._get_content_prompt(context, page_info, page_num, total_pages)
        
        if page_type == "COVER":
            prompt = self._get_cover_prompt(context, title)
        elif page_type == "SECTION":
            # 使用正确的章节序号，而非 HTML 页码
            section_num = page_info.get("section_num", 1)
            prompt = self._get_section_prompt(title, section_num)
        elif page_type == "CLOSING":
            prompt = self._get_closing_prompt()
        
        html = await self._generate(prompt)
        return self._clean_html(html)
    
    def _get_content_prompt(self, context: PresentationContext, page_info: Dict, page_num: int, total_pages: int) -> str:
        """正文页提示词 - 多种布局和图表支持"""
        title = page_info.get("title", "")
        content_hints = page_info.get("content", "")
        
        return f"""
# 背景信息
- 场景：{context.scenario_description[:200]}
- 单位：{context.organization}
- 风格：{context.tone or '专业严谨'}

# 当前任务
生成第 {page_num}/{total_pages} 页的 HTML 代码。

## 页面信息
- 标题：{title}
- 内容要点：{content_hints}

## 核心要求
1. 标题"{title}"是结论，正文要支撑这个结论
2. 底部结论框直接写核心启示，禁止出现"So What"字样
3. 数据必须来自内容要点，禁止编造
4. 根据内容特点选择最合适的布局

## 输出规范（极其重要，必须遵守）
1. **只输出 HTML 代码**，不要输出任何其他内容
2. **禁止输出解释、说明、选择理由**
3. **禁止输出 ```html 标记**
4. **第一个字符必须是 <**
5. 违反以上规则会导致页面显示失败

## 样式规范
1. **简洁设计**：不要使用边框装饰（border-left、border-top 等）
2. **颜色克制**：
   - 主色：#003366（深蓝）用于标题
   - 辅助色：#0066CC（亮蓝）用于图表
   - 背景：#F5F7FA（浅灰）用于卡片
   - 避免过多颜色，保持专业简洁
3. **中文标点**：使用中文引号""、逗号，、句号。
4. **排版规范**（重要）：
   - 列表项、段落文字必须左对齐（text-align: left）
   - 避免单字掉行：使用 white-space: nowrap 或调整文字长度
   - 底部结论框的文字要完整，不要出现"值。"这种单字掉行
   - 示例：错误 → "提升理论模型的普适性与实践价<br>值。" 正确 → "提升理论模型的普适性与实践价值。"
5. **间距规范**（重要）：
   - 内容区域和底部结论框之间必须有明显间距
   - 不要让卡片背景和底部结论框背景连在一起
   - 底部结论框前面要有足够的留白（至少 30px）

## 布局选择
根据内容特点选择布局，避免连续使用相同布局：
- 数据对比 → 图表
- 并列要点 → 多栏布局
- 对比分析 → 左右对比
- 论述内容 → 双栏文字
- 避免连续3页以上使用相同布局类型

## 可用布局模板

### 布局1: 左文右图表（适合数据展示）
<div class="slide-container">
  <main class="content-area">
    <div class="title-box"><h1 class="page-title">标题</h1></div>
    <div class="layout-box two-col">
      <div class="col">
        <h3 class="sub-head">关键发现</h3>
        <ul class="big-list">
          <li>要点1</li>
          <li>要点2</li>
        </ul>
      </div>
      <div class="col">
        <div class="chart-container" id="chart_{page_num}" style="width:100%;height:350px;"></div>
        <script>
          var chart_{page_num} = echarts.init(document.getElementById('chart_{page_num}'));
          chart_{page_num}.setOption({{
            color: ['#003366', '#0066CC', '#00AA88'],
            tooltip: {{}},
            xAxis: {{ type: 'category', data: ['A', 'B', 'C'] }},
            yAxis: {{ type: 'value' }},
            series: [{{ type: 'bar', data: [120, 200, 150] }}]
          }});
        </script>
      </div>
    </div>
    <div class="bottom-box"><div class="bottom-text">核心启示内容</div></div>
  </main>
  <footer class="slide-footer"><span>数据来源</span></footer>
</div>

### 布局2: 三栏数据卡片（适合多指标展示）
<div class="slide-container">
  <main class="content-area">
    <div class="title-box"><h1 class="page-title">标题</h1></div>
    <div class="layout-box three-col">
      <div class="col">
        <div style="background: #F5F7FA; padding: 25px; border-radius: 8px; text-align: center;">
          <div style="font-size: 48px; color: #003366; font-weight: bold; margin-bottom: 10px;">100+</div>
          <div style="font-size: 18px; color: #666;">指标说明</div>
        </div>
        <ul class="big-list" style="margin-top: 15px; text-align: left;">
          <li style="font-size: 15px;">要点描述</li>
        </ul>
      </div>
      <div class="col">
        <div style="background: #F5F7FA; padding: 25px; border-radius: 8px; text-align: center;">
          <div style="font-size: 48px; color: #0066CC; font-weight: bold; margin-bottom: 10px;">50%</div>
          <div style="font-size: 18px; color: #666;">核心指标</div>
        </div>
        <ul class="big-list" style="margin-top: 15px; text-align: left;">
          <li style="font-size: 15px;">要点描述</li>
        </ul>
      </div>
      <div class="col">
        <div style="background: #F5F7FA; padding: 25px; border-radius: 8px; text-align: center;">
          <div style="font-size: 48px; color: #003366; font-weight: bold; margin-bottom: 10px;">3x</div>
          <div style="font-size: 18px; color: #666;">增长倍数</div>
        </div>
        <ul class="big-list" style="margin-top: 15px; text-align: left;">
          <li style="font-size: 15px;">要点描述</li>
        </ul>
      </div>
    </div>
    <div class="bottom-box"><div class="bottom-text">核心启示内容</div></div>
  </main>
</div>

### 布局3: 饼图+说明（适合占比分析）
<div class="slide-container">
  <main class="content-area">
    <div class="title-box"><h1 class="page-title">标题</h1></div>
    <div class="layout-box two-col">
      <div class="col">
        <div class="chart-container" id="pie_{page_num}" style="width:100%;height:380px;"></div>
        <script>
          var pie_{page_num} = echarts.init(document.getElementById('pie_{page_num}'));
          pie_{page_num}.setOption({{
            color: ['#003366', '#0066CC', '#00AA88'],
            tooltip: {{ trigger: 'item' }},
            series: [{{
              type: 'pie', radius: ['40%', '70%'],
              label: {{ show: true, formatter: '{{b}}: {{d}}%' }},
              data: [
                {{ value: 35, name: '类别A' }},
                {{ value: 30, name: '类别B' }},
                {{ value: 20, name: '类别C' }},
                {{ value: 15, name: '其他' }}
              ]
            }}]
          }});
        </script>
      </div>
      <div class="col">
        <h3 class="sub-head">结构分析</h3>
        <ul class="big-list">
          <li><strong>类别A (35%)</strong>：说明</li>
          <li><strong>类别B (30%)</strong>：说明</li>
        </ul>
      </div>
    </div>
    <div class="bottom-box"><div class="bottom-text">核心启示内容</div></div>
  </main>
</div>

### 布局4: 时间轴/流程（适合发展历程或步骤）
<div class="slide-container">
  <main class="content-area">
    <div class="title-box"><h1 class="page-title">标题</h1></div>
    <div class="timeline-box">
      <div class="timeline-item">
        <div class="timeline-dot"></div>
        <div class="timeline-content">
          <div class="timeline-year">2023</div>
          <div class="timeline-text">阶段描述</div>
        </div>
      </div>
      <div class="timeline-item">
        <div class="timeline-dot active"></div>
        <div class="timeline-content">
          <div class="timeline-year">2024</div>
          <div class="timeline-text">当前阶段</div>
        </div>
      </div>
      <div class="timeline-item">
        <div class="timeline-dot"></div>
        <div class="timeline-content">
          <div class="timeline-year">2025</div>
          <div class="timeline-text">目标阶段</div>
        </div>
      </div>
    </div>
    <div class="bottom-box"><div class="bottom-text">核心启示内容</div></div>
  </main>
</div>

### 布局5: 左右对比（适合对比分析）
<div class="slide-container">
  <main class="content-area">
    <div class="title-box"><h1 class="page-title">标题</h1></div>
    <div class="layout-box two-col compare">
      <div class="col compare-left">
        <h3 class="sub-head compare-title negative">现状/问题</h3>
        <ul class="big-list">
          <li>问题点1</li>
          <li>问题点2</li>
        </ul>
      </div>
      <div class="col compare-right">
        <h3 class="sub-head compare-title positive">目标/方案</h3>
        <ul class="big-list">
          <li>解决方案1</li>
          <li>解决方案2</li>
        </ul>
      </div>
    </div>
    <div class="bottom-box"><div class="bottom-text">核心启示内容</div></div>
  </main>
</div>

### 布局6: 全幅图表（适合趋势分析）
<div class="slide-container">
  <main class="content-area">
    <div class="title-box"><h1 class="page-title">标题</h1></div>
    <div class="chart-full">
      <div class="chart-container" id="line_{page_num}" style="width:100%;height:420px;"></div>
      <script>
        var line_{page_num} = echarts.init(document.getElementById('line_{page_num}'));
        line_{page_num}.setOption({{
          color: ['#003366', '#0066CC'],
          tooltip: {{ trigger: 'axis' }},
          legend: {{ data: ['指标1', '指标2'] }},
          xAxis: {{ type: 'category', data: ['2020', '2021', '2022', '2023', '2024'] }},
          yAxis: {{ type: 'value' }},
          series: [
            {{ name: '指标1', type: 'line', smooth: true, data: [100, 120, 150, 180, 220] }},
            {{ name: '指标2', type: 'line', smooth: true, data: [80, 100, 130, 160, 200] }}
          ]
        }});
      </script>
    </div>
    <div class="bottom-box"><div class="bottom-text">核心启示内容</div></div>
  </main>
</div>

### 布局7: 纯文字双栏（适合论述性内容）
<div class="slide-container">
  <main class="content-area">
    <div class="title-box"><h1 class="page-title">标题</h1></div>
    <div class="layout-box two-col" style="gap: 50px;">
      <div class="col">
        <h3 style="font-size: 20px; color: #003366; margin-bottom: 15px; font-weight: bold;">核心观点一</h3>
        <p style="font-size: 16px; color: #444; line-height: 1.8; margin-bottom: 20px;">详细论述内容，包含具体的分析和说明。这里可以写较长的段落来阐述观点。</p>
        <h3 style="font-size: 20px; color: #003366; margin-bottom: 15px; font-weight: bold;">核心观点二</h3>
        <p style="font-size: 16px; color: #444; line-height: 1.8;">继续论述，保持内容的连贯性和逻辑性。</p>
      </div>
      <div class="col">
        <h3 style="font-size: 20px; color: #003366; margin-bottom: 15px; font-weight: bold;">核心观点三</h3>
        <p style="font-size: 16px; color: #444; line-height: 1.8; margin-bottom: 20px;">右侧栏的内容，与左侧形成呼应或补充。</p>
        <h3 style="font-size: 20px; color: #003366; margin-bottom: 15px; font-weight: bold;">核心观点四</h3>
        <p style="font-size: 16px; color: #444; line-height: 1.8;">总结性的内容或延伸讨论。</p>
      </div>
    </div>
    <div class="bottom-box"><div class="bottom-text">核心启示内容</div></div>
  </main>
</div>

### 布局8: 表格展示（适合对比数据或分类信息）
<div class="slide-container">
  <main class="content-area">
    <div class="title-box"><h1 class="page-title">标题</h1></div>
    <table class="clean-table" style="margin-top: 20px;">
      <thead>
        <tr>
          <th style="width: 25%;">维度</th>
          <th style="width: 25%;">现状</th>
          <th style="width: 25%;">目标</th>
          <th style="width: 25%;">措施</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td><strong>维度一</strong></td>
          <td>现状描述</td>
          <td>目标描述</td>
          <td>具体措施</td>
        </tr>
        <tr>
          <td><strong>维度二</strong></td>
          <td>现状描述</td>
          <td>目标描述</td>
          <td>具体措施</td>
        </tr>
      </tbody>
    </table>
    <div class="bottom-box"><div class="bottom-text">核心启示内容</div></div>
  </main>
</div>

### 布局9: 大数字突出（适合关键成果展示）
<div class="slide-container">
  <main class="content-area">
    <div class="title-box"><h1 class="page-title">标题</h1></div>
    <div style="display: flex; justify-content: center; align-items: center; flex: 1; gap: 80px;">
      <div style="text-align: center;">
        <div style="font-size: 72px; font-weight: bold; color: #003366;">95%</div>
        <div style="font-size: 18px; color: #666; margin-top: 10px;">关键指标说明</div>
      </div>
      <div style="text-align: center;">
        <div style="font-size: 72px; font-weight: bold; color: #0066CC;">3.5x</div>
        <div style="font-size: 18px; color: #666; margin-top: 10px;">增长倍数说明</div>
      </div>
      <div style="text-align: center;">
        <div style="font-size: 72px; font-weight: bold; color: #003366;">100+</div>
        <div style="font-size: 18px; color: #666; margin-top: 10px;">数量指标说明</div>
      </div>
    </div>
    <div class="bottom-box"><div class="bottom-text">核心启示内容</div></div>
  </main>
</div>

**重要提醒**：请根据当前页面的内容特点，从以上9种布局中选择最合适的一种。避免连续使用相同布局！

请根据内容特点选择最合适的布局，生成 HTML：
"""

    def _get_cover_prompt(self, context: PresentationContext, title: str) -> str:
        """封面页提示词"""
        return f"""
生成封面页 HTML。

信息：
- 标题：{title}（必须原封不动使用）
- 单位：{context.organization}
- 日期：{context.date}

HTML 结构：
<div class="slide-container cover-slide">
  <div class="cover-top">
    <div class="brand-line"></div>
    <div class="doc-type">专项研究报告</div>
    <h1 class="main-title">{title}</h1>
    <h2 class="sub-title">2025 深圳机关党建重点课题研究报告</h2>
  </div>
  <div class="cover-middle"></div>
  <div class="cover-bottom">
    <div class="footer-row"><div class="footer-item">汇报单位：{context.organization}</div></div>
    <div class="footer-row"><div class="footer-item">日期：{context.date}</div></div>
  </div>
</div>

直接输出 HTML：
"""
    
    def _get_section_prompt(self, title: str, section_num: int) -> str:
        """章节页提示词"""
        num_str = f"{section_num:02d}"
        return f"""
生成章节过场页 HTML。

标题：{title}
序号：{num_str}

HTML 结构：
<div class="slide-container section-slide">
  <div class="section-bg-pattern"></div>
  <div class="section-content">
    <div class="section-number">{num_str}</div>
    <div class="section-line"></div>
    <h1 class="section-title">{title}</h1>
  </div>
</div>

直接输出 HTML：
"""
    
    def _get_closing_prompt(self) -> str:
        """封底页提示词"""
        return """
生成封底页 HTML。

<div class="slide-container closing-slide">
  <div class="closing-title">谢 谢 观 看</div>
  <div class="closing-contact"><p>深圳国家高技术产业创新中心</p></div>
</div>

直接输出 HTML：
"""
    
    async def _generate(self, prompt: str, retry_count: int = 0) -> str:
        """调用 AI 生成"""
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": MASTER_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=TEMPERATURE,
                ),
                timeout=TIMEOUT_SECONDS
            )
            
            # 检查响应是否有效
            if not response or not response.choices:
                raise ValueError("API 返回空响应")
            
            content = response.choices[0].message.content
            if content is None:
                raise ValueError("API 返回内容为空")
            
            return content.strip()
        
        except asyncio.TimeoutError:
            if retry_count < MAX_RETRIES:
                wait_time = RETRY_DELAY * (retry_count + 1)
                console.print(f"[yellow]⚠ 超时，{wait_time}秒后重试...[/yellow]")
                await asyncio.sleep(wait_time)
                return await self._generate(prompt, retry_count + 1)
            raise
        
        except Exception as e:
            error_msg = str(e)
            if retry_count < MAX_RETRIES:
                wait_time = RETRY_DELAY * (retry_count + 1)
                console.print(f"[yellow]⚠ 失败: {error_msg[:100]}，{wait_time}秒后重试...[/yellow]")
                await asyncio.sleep(wait_time)
                return await self._generate(prompt, retry_count + 1)
            console.print(f"[red]✗ 最终失败: {error_msg}[/red]")
            raise
    
    def _parse_outline(self, text: str) -> List[Dict[str, Any]]:
        """解析大纲"""
        pages = []
        # 系统自动生成的类型，AI 不应该生成
        auto_types = {'COVER', 'AGENDA', 'CLOSING'}
        
        for line in text.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split('|')
            if len(parts) >= 2:
                page_type = parts[0].strip().upper()
                
                # 过滤掉 AI 可能错误生成的封面/目录/封底
                if page_type in auto_types:
                    continue
                
                # 只接受 SECTION 和 CONTENT 类型
                if page_type not in {'SECTION', 'CONTENT'}:
                    page_type = 'CONTENT'
                
                pages.append({
                    'type': page_type,
                    'title': parts[1].strip(),
                    'content': parts[2].strip() if len(parts) > 2 else ''
                })
        return pages
    
    def _clean_html(self, html: str) -> str:
        """清理 HTML 并修复标点符号"""
        import re
        html = html.strip()
        
        # 移除 markdown 代码块标记
        if html.startswith('```html'):
            html = html[7:]
        elif html.startswith('```'):
            html = html[3:]
        if html.endswith('```'):
            html = html[:-3]
        
        # 移除 AI 可能输出的多余内容（在 HTML 之前的解释文字）
        # 找到第一个 <div 或 <main 标签的位置
        first_tag_match = re.search(r'<(div|main|section)\s', html, re.IGNORECASE)
        if first_tag_match and first_tag_match.start() > 0:
            # 移除 HTML 标签之前的所有内容
            html = html[first_tag_match.start():]
        
        # 移除 HTML 之后的多余内容（在最后一个 </div> 之后）
        last_div_match = list(re.finditer(r'</div>\s*$', html, re.IGNORECASE))
        if last_div_match:
            html = html[:last_div_match[-1].end()]
        
        # 移除 style 和 header 标签
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<header[^>]*>.*?</header>', '', html, flags=re.DOTALL | re.IGNORECASE)
        
        # 修复中文标点符号（在中文内容中）
        html = self._fix_chinese_punctuation(html)
        
        return html.strip()
    
    def _fix_chinese_punctuation(self, html: str) -> str:
        """修复中文标点符号
        
        将中文内容中的英文标点符号替换为中文标点符号
        注意：不影响 HTML 标签和属性中的引号
        """
        import re
        
        # 分离 HTML 标签和文本内容
        parts = []
        last_end = 0
        
        # 匹配所有 HTML 标签
        for match in re.finditer(r'<[^>]+>', html):
            # 添加标签前的文本（需要处理标点）
            if match.start() > last_end:
                text = html[last_end:match.start()]
                text = self._convert_punctuation_in_text(text)
                parts.append(text)
            
            # 添加标签本身（不处理）
            parts.append(match.group())
            last_end = match.end()
        
        # 添加最后一段文本
        if last_end < len(html):
            text = html[last_end:]
            text = self._convert_punctuation_in_text(text)
            parts.append(text)
        
        return ''.join(parts)
    
    def _convert_punctuation_in_text(self, text: str) -> str:
        """转换文本中的标点符号（仅处理包含中文的文本）"""
        import re
        
        # 如果文本中没有中文字符，不处理
        if not re.search(r'[\u4e00-\u9fff]', text):
            return text
        
        # 转换标点符号
        # 1. 英文引号 -> 中文引号（成对转换）
        # 使用状态机来正确配对引号
        result = []
        in_quote = False
        i = 0
        while i < len(text):
            if text[i] == '"':
                if not in_quote:
                    result.append('"')
                    in_quote = True
                else:
                    result.append('"')
                    in_quote = False
            else:
                result.append(text[i])
            i += 1
        
        text = ''.join(result)
        
        # 2. 其他标点符号（只在中文上下文中转换）
        # 逗号：在中文字符或百分号附近的逗号
        text = re.sub(r'([\u4e00-\u9fff%]),', r'\1，', text)
        text = re.sub(r',([\u4e00-\u9fff])', r'，\1', text)
        
        # 句号：在中文字符后的句号
        text = re.sub(r'([\u4e00-\u9fff])\.(?!\d)', r'\1。', text)
        
        # 冒号：在中文字符附近的冒号
        text = re.sub(r'([\u4e00-\u9fff]):', r'\1：', text)
        text = re.sub(r':([\u4e00-\u9fff])', r'：\1', text)
        
        # 分号：在中文字符附近的分号
        text = re.sub(r'([\u4e00-\u9fff]);', r'\1；', text)
        text = re.sub(r';([\u4e00-\u9fff])', r'；\1', text)
        
        # 问号和感叹号
        text = re.sub(r'([\u4e00-\u9fff])\?', r'\1？', text)
        text = re.sub(r'([\u4e00-\u9fff])!', r'\1！', text)
        
        return text
