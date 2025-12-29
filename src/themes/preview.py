"""
主题预览生成器 - 生成场景化主题预览 HTML

功能:
1. 生成场景专属预览页面
2. 展示符合场景特点的示例内容
3. 体现不同场景的设计差异
"""

from pathlib import Path
from typing import Optional
from .theme_manager import Theme
from .css_generator import generate_theme_css


# 场景专属预览内容配置
SCENARIO_PREVIEW_CONTENT = {
    "consulting": {
        "doc_type": "战略咨询研究报告",
        "title": "数字化转型战略规划",
        "subtitle": "咨询研究报告",
        "section_title": "第一部分 市场环境分析",
        "section_desc": "外部环境扫描与发展趋势研判",
        "content_title": "市场规模5年CAGR达23%，正处于爆发期",
        "content_items": [
            "2023年市场规模突破800亿元，头部效应显著",
            "技术成熟度曲线显示已进入稳定应用期",
            "政策支持力度持续加大，多项利好陆续出台"
        ],
        "data_1_val": "23%",
        "data_1_lbl": "年均复合增长率",
        "data_2_val": "800亿",
        "data_2_lbl": "市场规模(2023)",
        "bottom_text": "战略建议：聚焦核心赛道，加速技术布局，抢占市场先机",
        "catalog": [
            ("01", "市场环境分析", "宏观趋势与竞争格局深度解读"),
            ("02", "问题诊断", "核心痛点与根因分析"),
            ("03", "战略建议", "可落地的解决方案与实施路径")
        ]
    },
    "annual_review": {
        "doc_type": "年度工作总结",
        "title": "2024年度述职报告",
        "subtitle": "个人/团队工作总结",
        "section_title": "核心业绩亮点",
        "section_desc": "用数据说话，用成果证明",
        "content_title": "年度销售额突破历史新高，超额完成目标127%",
        "content_items": [
            "全年签单金额达1.2亿元，同比增长45%",
            "新开拓重点客户12家，留存率达95%",
            "带领团队获得年度最佳销售团队荣誉"
        ],
        "data_1_val": "127%",
        "data_1_lbl": "目标完成率",
        "data_2_val": "1.2亿",
        "data_2_lbl": "年度签单额",
        "bottom_text": "个人成长：从区域负责人晋升为大区总监，管理能力显著提升",
        "catalog": [
            ("01", "年度高光", "核心业绩与突破成就"),
            ("02", "重点项目", "标杆项目复盘与经验萃取"),
            ("03", "明年展望", "新年度目标与行动计划")
        ]
    },
    "company_intro": {
        "doc_type": "公司简介",
        "title": "领先的数字化解决方案提供商",
        "subtitle": "公司介绍",
        "section_title": "核心产品与服务",
        "section_desc": "为企业提供端到端的数字化转型方案",
        "content_title": "服务超过500家行业头部客户，交付满意度98%",
        "content_items": [
            "国家高新技术企业，拥有核心专利50+项",
            "与阿里云、华为等头部企业建立深度合作",
            "覆盖金融、制造、零售三大核心行业"
        ],
        "data_1_val": "500+",
        "data_1_lbl": "服务客户数",
        "data_2_val": "98%",
        "data_2_lbl": "客户满意度",
        "bottom_text": "使命：用技术创新驱动行业数字化升级，成为最值得信赖的合作伙伴",
        "catalog": [
            ("01", "公司概览", "使命愿景与发展历程"),
            ("02", "核心能力", "产品矩阵与技术优势"),
            ("03", "合作邀请", "携手共创，合作共赢")
        ]
    },
    "academic": {
        "doc_type": "学术研究报告",
        "title": "人工智能赋能教育创新的实证研究",
        "subtitle": "研究汇报",
        "section_title": "研究方法与设计",
        "section_desc": "实证研究设计与数据分析方法",
        "content_title": "AI辅助教学显著提升学生自主学习能力(β=0.67, p<0.001)",
        "content_items": [
            "采用混合研究方法：问卷调查+深度访谈+实验对比",
            "样本量N=1,256，覆盖10所高校，具有良好代表性",
            "使用结构方程模型验证研究假设，模型拟合度良好"
        ],
        "data_1_val": "1,256",
        "data_1_lbl": "有效样本量",
        "data_2_val": "0.67***",
        "data_2_lbl": "核心效应系数",
        "bottom_text": "理论贡献：构建了AI赋能教育的理论模型，填补了该领域的研究空白",
        "catalog": [
            ("01", "问题提出", "研究背景与核心问题"),
            ("02", "文献综述", "理论基础与研究假设"),
            ("03", "研究发现", "实证结果与深入讨论")
        ]
    },
    "creative": {
        "doc_type": "创意提案",
        "title": "「心动瞬间」品牌年度整合营销方案",
        "subtitle": "创意提案",
        "section_title": "消费者洞察",
        "section_desc": "找到那个触动心弦的情感连接点",
        "content_title": "Z世代渴望「真实而不完美」的品牌连接",
        "content_items": [
            "调研发现：73%的年轻人厌倦了过度美化的品牌叙事",
            "他们希望品牌能真实展现「不完美但真诚」的一面",
            "关键洞察：与其讲述完美，不如分享成长"
        ],
        "data_1_val": "73%",
        "data_1_lbl": "消费者认同度",
        "data_2_val": "5亿",
        "data_2_lbl": "预估曝光量",
        "bottom_text": "Big Idea：「不必完美，只要真实」—— 让每一刻心动都被看见",
        "catalog": [
            ("01", "洞察挖掘", "深入年轻人的情感世界"),
            ("02", "创意概念", "Big Idea与核心创意"),
            ("03", "执行方案", "全渠道传播策略与落地方案")
        ]
    },
    "government": {
        "doc_type": "工作报告",
        "title": "关于推进数字政府建设工作情况的报告",
        "subtitle": "工作汇报",
        "section_title": "第一部分 工作成效",
        "section_desc": "扎实推进各项任务落地见效",
        "content_title": "政务服务事项网上可办率达98%，群众满意度显著提升",
        "content_items": [
            "全面完成省级部署的12项重点任务，进度位居全市前列",
            "建成统一政务服务平台，实现一网通办全覆盖",
            "创新一件事一次办模式，减少群众跑腿次数60%以上"
        ],
        "data_1_val": "98%",
        "data_1_lbl": "网上可办率",
        "data_2_val": "60%",
        "data_2_lbl": "跑腿次数减少",
        "bottom_text": "下一步将深入贯彻落实上级决策部署，持续深化数字政府建设",
        "catalog": [
            ("01", "总体情况", "工作背景与目标任务"),
            ("02", "主要成效", "重点工作推进情况"),
            ("03", "下步计划", "工作思路与保障措施")
        ]
    }
}


def generate_theme_preview(theme: Theme, output_path: Optional[str] = None) -> str:
    """生成主题预览 HTML - 场景化版本"""
    
    css = generate_theme_css(theme)
    
    # 获取场景专属内容
    category = theme.metadata.category
    content = SCENARIO_PREVIEW_CONTENT.get(category, SCENARIO_PREVIEW_CONTENT["consulting"])
    
    # 生成目录HTML
    catalog_html = ""
    for idx, name, desc in content["catalog"]:
        catalog_html += f'''
                        <div class="catalog-item">
                            <div class="catalog-idx">{idx}</div>
                            <div class="catalog-content">
                                <div class="catalog-name">{name}</div>
                                <div class="catalog-desc">{desc}</div>
                            </div>
                        </div>'''
    
    # 生成列表项HTML
    list_html = ""
    for item in content["content_items"]:
        list_html += f"<li>{item}</li>\n"
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>主题预览 - {theme.metadata.name}</title>
    <style>
{css}

/* 预览页面样式 */
body {{
    background: #f0f0f0;
    padding: 40px;
}}

.preview-container {{
    max-width: 1400px;
    margin: 0 auto;
}}

.preview-header {{
    text-align: center;
    margin-bottom: 40px;
    padding: 30px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}}

.preview-header h1 {{
    font-size: 32px;
    color: var(--primary);
    margin-bottom: 10px;
}}

.preview-header p {{
    color: var(--text-secondary);
    font-size: 16px;
}}

.color-palette {{
    display: flex;
    gap: 10px;
    justify-content: center;
    margin-top: 20px;
    flex-wrap: wrap;
}}

.color-swatch {{
    width: 60px;
    height: 60px;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-end;
    padding-bottom: 5px;
    font-size: 10px;
    color: white;
    text-shadow: 0 1px 2px rgba(0,0,0,0.5);
}}

.slide-preview {{
    margin-bottom: 40px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    border-radius: 8px;
    overflow: hidden;
}}

.slide-label {{
    background: var(--primary);
    color: white;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: bold;
}}
    </style>
</head>
<body>
    <div class="preview-container">
        <!-- 预览头部 -->
        <div class="preview-header">
            <h1>{theme.metadata.name}</h1>
            <p>{theme.metadata.description}</p>
            <p><strong>场景:</strong> {category} | <strong>适用:</strong> {', '.join(theme.metadata.tags)}</p>
            
            <!-- 配色展示 -->
            <div class="color-palette">
                <div class="color-swatch" style="background: {theme.colors.primary};">Primary</div>
                <div class="color-swatch" style="background: {theme.colors.primary_light};">Light</div>
                <div class="color-swatch" style="background: {theme.colors.accent};">Accent</div>
                <div class="color-swatch" style="background: {theme.colors.text_primary};">Text</div>
                <div class="color-swatch" style="background: {theme.colors.background_alt}; color: #333;">BG Alt</div>
            </div>
        </div>
        
        <!-- 封面页预览 -->
        <div class="slide-preview">
            <div class="slide-label">封面页 (Cover)</div>
            <div class="slide-container cover-slide">
                <div class="cover-top">
                    <div class="brand-line"></div>
                    <div class="doc-type">{content["doc_type"]}</div>
                    <h1 class="main-title">{content["title"]}</h1>
                    <h2 class="sub-title">{content["subtitle"]}</h2>
                </div>
                <div class="cover-middle"></div>
                <div class="cover-bottom">
                    <div class="footer-row">
                        <div class="footer-item">汇报单位：示例单位名称</div>
                    </div>
                    <div class="footer-row">
                        <div class="footer-item">日期：2025年12月</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 章节页预览 -->
        <div class="slide-preview">
            <div class="slide-label">章节过场页 (Section)</div>
            <div class="slide-container section-slide">
                <div class="section-bg-pattern"></div>
                <div class="section-content">
                    <div class="section-number">01</div>
                    <div class="section-line"></div>
                    <h1 class="section-title">{content["section_title"]}</h1>
                    <div class="section-desc">{content["section_desc"]}</div>
                </div>
            </div>
        </div>
        
        <!-- 正文页预览 -->
        <div class="slide-preview">
            <div class="slide-label">正文页 (Content)</div>
            <div class="slide-container">
                <main class="content-area">
                    <div class="title-box">
                        <h1 class="page-title">{content["content_title"]}</h1>
                    </div>
                    <div class="layout-box two-col">
                        <div class="col">
                            <div class="text-block">
                                <h3 class="sub-head">核心要点</h3>
                                <ul class="big-list">
                                    {list_html}
                                </ul>
                            </div>
                        </div>
                        <div class="col">
                            <div class="data-card">
                                <div class="data-val">{content["data_1_val"]}</div>
                                <div class="data-lbl">{content["data_1_lbl"]}</div>
                            </div>
                            <div class="data-card" style="margin-top: 20px;">
                                <div class="data-val">{content["data_2_val"]}</div>
                                <div class="data-lbl">{content["data_2_lbl"]}</div>
                            </div>
                        </div>
                    </div>
                    <div class="bottom-box">
                        <div class="bottom-text">{content["bottom_text"]}</div>
                    </div>
                </main>
                <footer class="slide-footer">
                    <span>数据来源：课题组整理</span>
                </footer>
            </div>
        </div>
        
        <!-- 目录页预览 -->
        <div class="slide-preview">
            <div class="slide-label">目录页 (Catalog)</div>
            <div class="slide-container">
                <main class="content-area">
                    <div class="title-box">
                        <h1 class="page-title">报告核心框架</h1>
                    </div>
                    <div class="catalog-list">
                        {catalog_html}
                    </div>
                </main>
            </div>
        </div>
        
        <!-- 封底页预览 -->
        <div class="slide-preview">
            <div class="slide-label">封底页 (Closing)</div>
            <div class="slide-container closing-slide">
                <div class="closing-title">谢 谢 观 看</div>
                <div class="closing-contact">
                    <p>如有疑问，请联系项目组</p>
                    <p>联系邮箱：example@company.com</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    if output_path:
        Path(output_path).write_text(html, encoding='utf-8')
    
    return html


def generate_all_theme_previews(output_dir: str = "theme_previews"):
    """生成所有主题的预览"""
    from .theme_registry import THEME_REGISTRY
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 生成索引页
    index_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>主题预览索引</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 40px; background: #f5f5f5; }
        h1 { text-align: center; color: #333; }
        .theme-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto; }
        .theme-card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .theme-card h2 { margin: 0 0 10px 0; font-size: 18px; }
        .theme-card p { color: #666; font-size: 14px; margin: 0 0 15px 0; }
        .theme-card a { display: inline-block; padding: 8px 16px; background: #0066cc; color: white; text-decoration: none; border-radius: 4px; }
        .theme-card a:hover { background: #0052a3; }
        .color-bar { display: flex; height: 8px; border-radius: 4px; overflow: hidden; margin-bottom: 15px; }
        .color-bar span { flex: 1; }
    </style>
</head>
<body>
    <h1>🎨 场景化主题预览</h1>
    <div class="theme-grid">
"""
    
    for theme_id, theme in THEME_REGISTRY.items():
        # 生成单个主题预览
        preview_file = f"{theme_id}.html"
        generate_theme_preview(theme, str(output_path / preview_file))
        
        # 添加到索引
        index_html += f"""
        <div class="theme-card">
            <div class="color-bar">
                <span style="background: {theme.colors.primary};"></span>
                <span style="background: {theme.colors.primary_light};"></span>
                <span style="background: {theme.colors.accent};"></span>
            </div>
            <h2>{theme.metadata.name}</h2>
            <p>{theme.metadata.description}</p>
            <a href="{preview_file}">查看预览</a>
        </div>
"""
    
    index_html += """
    </div>
</body>
</html>
"""
    
    (output_path / "index.html").write_text(index_html, encoding='utf-8')
    
    return str(output_path / "index.html")
