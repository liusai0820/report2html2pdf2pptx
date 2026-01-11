"""
内容质量检查器 - 确保生成内容符合专业标准

检查维度：
1. 结构完整性
2. 内容质量
3. 逻辑严密性
4. 数据规范性
"""

import re
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass


@dataclass
class QualityIssue:
    """质量问题"""
    severity: str  # error, warning, info
    category: str  # structure, content, logic, data
    message: str
    suggestion: str
    location: str = ""


class QualityChecker:
    """内容质量检查器"""
    
    def __init__(self, scenario: str = "consulting"):
        self.scenario = scenario
        self.issues: List[QualityIssue] = []
    
    def check_page(self, page_data: Dict[str, Any], html_content: str) -> List[QualityIssue]:
        """检查单页内容质量"""
        self.issues = []
        
        page_type = page_data.get("type", "CONTENT")
        title = page_data.get("title", "")
        
        if page_type == "CONTENT":
            self._check_title_quality(title)
            self._check_content_structure(html_content)
            self._check_data_quality(html_content)
            self._check_so_what(html_content)
            self._check_forbidden_patterns(html_content)
        
        return self.issues
    
    def check_outline(self, pages: List[Dict[str, Any]]) -> List[QualityIssue]:
        """检查大纲质量"""
        self.issues = []
        
        self._check_outline_structure(pages)
        self._check_outline_logic(pages)
        self._check_title_patterns(pages)
        
        return self.issues
    
    def _check_title_quality(self, title: str):
        """检查标题质量"""
        # 检查是否是主题而非结论
        topic_patterns = [
            r"^.{0,4}分析$",
            r"^.{0,4}介绍$",
            r"^.{0,4}概述$",
            r"^.{0,4}情况$",
            r"^.{0,4}现状$",
            r"^关于",
            r"^浅谈",
            r"^论",
        ]
        
        for pattern in topic_patterns:
            if re.search(pattern, title):
                self.issues.append(QualityIssue(
                    severity="warning",
                    category="content",
                    message=f"标题'{title}'看起来是主题而非结论",
                    suggestion="标题应该是一个完整的观点或结论，例如'市场规模5年CAGR达23%，正处于爆发期'",
                    location="title"
                ))
                break
        
        # 检查标题长度
        if len(title) < 5:
            self.issues.append(QualityIssue(
                severity="warning",
                category="content",
                message=f"标题'{title}'过短，信息量不足",
                suggestion="标题应该包含核心观点，建议10-30个字",
                location="title"
            ))
        
        if len(title) > 50:
            self.issues.append(QualityIssue(
                severity="info",
                category="content",
                message=f"标题过长（{len(title)}字）",
                suggestion="标题建议控制在30字以内，便于阅读",
                location="title"
            ))
    
    def _check_content_structure(self, html: str):
        """检查内容结构"""
        # 检查是否有标题
        if not re.search(r'class="page-title"', html):
            self.issues.append(QualityIssue(
                severity="error",
                category="structure",
                message="缺少页面标题",
                suggestion="每页必须有 .page-title 元素",
                location="html"
            ))
        
        # 检查是否有内容区域
        if not re.search(r'class="content-area"', html):
            self.issues.append(QualityIssue(
                severity="error",
                category="structure",
                message="缺少内容区域",
                suggestion="正文页必须有 .content-area 元素",
                location="html"
            ))
        
        # 检查是否有禁止的元素
        if re.search(r'<style', html, re.IGNORECASE):
            self.issues.append(QualityIssue(
                severity="error",
                category="structure",
                message="包含禁止的 <style> 标签",
                suggestion="不要生成 CSS，使用预定义的类名",
                location="html"
            ))
        
        if re.search(r'<header', html, re.IGNORECASE):
            self.issues.append(QualityIssue(
                severity="error",
                category="structure",
                message="包含禁止的 <header> 标签",
                suggestion="不要生成页眉",
                location="html"
            ))
    
    def _check_data_quality(self, html: str):
        """检查数据质量"""
        # 检查数据卡片是否有具体数值
        data_cards = re.findall(r'class="data-val"[^>]*>([^<]+)<', html)
        for value in data_cards:
            if not re.search(r'\d', value):
                self.issues.append(QualityIssue(
                    severity="warning",
                    category="data",
                    message=f"数据卡片值'{value}'不包含数字",
                    suggestion="数据卡片应该展示具体的数值",
                    location="data-card"
                ))
        
        # 检查是否有数据来源
        if re.search(r'class="data-card"', html) or re.search(r'class="clean-table"', html):
            if not re.search(r'数据来源|来源：|Source', html):
                self.issues.append(QualityIssue(
                    severity="info",
                    category="data",
                    message="包含数据但未标注来源",
                    suggestion="建议在页脚标注数据来源",
                    location="footer"
                ))
    
    def _check_so_what(self, html: str):
        """检查是否有 So What"""
        # 检查是否有底部结论框
        if not re.search(r'class="bottom-box"', html):
            self.issues.append(QualityIssue(
                severity="info",
                category="content",
                message="缺少底部结论框",
                suggestion="建议添加 .bottom-box 说明这页内容的启示或建议",
                location="html"
            ))
    
    def _check_forbidden_patterns(self, html: str):
        """检查禁止的模式"""
        # 检查空洞表述
        empty_patterns = [
            (r"我们可以看到", "删除'我们可以看到'，直接说结论"),
            (r"根据数据显示", "删除'根据数据显示'，直接说数据"),
            (r"众所周知", "删除'众所周知'，直接说事实"),
            (r"不言而喻", "删除'不言而喻'，明确说明"),
            (r"总而言之", "删除'总而言之'，直接说结论"),
        ]
        
        for pattern, suggestion in empty_patterns:
            if re.search(pattern, html):
                self.issues.append(QualityIssue(
                    severity="warning",
                    category="content",
                    message=f"包含空洞表述'{pattern}'",
                    suggestion=suggestion,
                    location="content"
                ))
        
        # 检查 Emoji
        if re.search(r'[\U0001F300-\U0001F9FF]', html):
            self.issues.append(QualityIssue(
                severity="error",
                category="content",
                message="包含 Emoji 表情",
                suggestion="正式文档禁止使用 Emoji",
                location="content"
            ))
    
    def _check_outline_structure(self, pages: List[Dict[str, Any]]):
        """检查大纲结构"""
        # 检查是否有章节划分
        section_count = sum(1 for p in pages if p.get("type") == "SECTION")
        content_count = sum(1 for p in pages if p.get("type") == "CONTENT")
        
        if section_count == 0 and content_count > 10:
            self.issues.append(QualityIssue(
                severity="warning",
                category="structure",
                message="大纲缺少章节划分",
                suggestion="建议每5-8页内容添加一个章节过场页",
                location="outline"
            ))
        
        # 检查章节是否过长
        current_section_pages = 0
        for page in pages:
            if page.get("type") == "SECTION":
                if current_section_pages > 10:
                    self.issues.append(QualityIssue(
                        severity="info",
                        category="structure",
                        message=f"章节包含{current_section_pages}页，可能过长",
                        suggestion="建议每个章节控制在5-8页",
                        location="outline"
                    ))
                current_section_pages = 0
            else:
                current_section_pages += 1
    
    def _check_outline_logic(self, pages: List[Dict[str, Any]]):
        """检查大纲逻辑"""
        # 检查是否有逻辑递进
        titles = [p.get("title", "") for p in pages if p.get("type") == "CONTENT"]
        
        # 简单检查：是否有重复标题
        seen_titles = set()
        for title in titles:
            if title in seen_titles:
                self.issues.append(QualityIssue(
                    severity="warning",
                    category="logic",
                    message=f"标题'{title}'重复出现",
                    suggestion="每页应该有独特的观点",
                    location="outline"
                ))
            seen_titles.add(title)
    
    def _check_title_patterns(self, pages: List[Dict[str, Any]]):
        """检查标题模式"""
        for page in pages:
            if page.get("type") == "CONTENT":
                title = page.get("title", "")
                self._check_title_quality(title)
    
    def get_summary(self) -> Dict[str, Any]:
        """获取检查摘要"""
        error_count = sum(1 for i in self.issues if i.severity == "error")
        warning_count = sum(1 for i in self.issues if i.severity == "warning")
        info_count = sum(1 for i in self.issues if i.severity == "info")
        
        return {
            "total_issues": len(self.issues),
            "errors": error_count,
            "warnings": warning_count,
            "info": info_count,
            "passed": error_count == 0,
            "issues": [
                {
                    "severity": i.severity,
                    "category": i.category,
                    "message": i.message,
                    "suggestion": i.suggestion,
                }
                for i in self.issues
            ]
        }


def check_content_quality(
    page_data: Dict[str, Any],
    html_content: str,
    scenario: str = "consulting"
) -> Dict[str, Any]:
    """便捷函数：检查内容质量"""
    checker = QualityChecker(scenario)
    checker.check_page(page_data, html_content)
    return checker.get_summary()


def check_outline_quality(
    pages: List[Dict[str, Any]],
    scenario: str = "consulting"
) -> Dict[str, Any]:
    """便捷函数：检查大纲质量"""
    checker = QualityChecker(scenario)
    checker.check_outline(pages)
    return checker.get_summary()
