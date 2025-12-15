#!/usr/bin/env python3
"""
上下文管理器 - 智能检索与注入
为每一页 PPT 生成提供最相关的源文档片段
"""

import re
from typing import List, Dict, Tuple
from collections import Counter
import jieba
import jieba.analyse
from rich.console import Console

console = Console()


class ContextManager:
    """上下文管理器 - 智能检索源文档相关内容"""
    
    def __init__(self, full_document: str, max_context_length: int = 4000):
        """
        初始化上下文管理器
        
        Args:
            full_document: 完整文档内容
            max_context_length: 最大上下文长度（字符数）
        """
        self.full_document = full_document
        self.max_context_length = max_context_length
        
        # 将文档分段（按段落）
        self.paragraphs = self._split_into_paragraphs(full_document)
        
        # 为每个段落提取关键词
        self.paragraph_keywords = self._extract_paragraph_keywords()
        
        console.print(f"[dim]  上下文管理器已初始化: {len(self.paragraphs)} 个段落[/dim]")
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """将文档分割成段落"""
        # 按双换行或标题分割
        paragraphs = re.split(r'\n\s*\n+', text)
        
        # 过滤空段落，保留有实质内容的段落
        paragraphs = [p.strip() for p in paragraphs if len(p.strip()) > 20]
        
        return paragraphs
    
    def _extract_paragraph_keywords(self) -> List[List[str]]:
        """为每个段落提取关键词"""
        paragraph_keywords = []
        
        for para in self.paragraphs:
            # 使用 jieba 的 TF-IDF 提取关键词
            keywords = jieba.analyse.extract_tags(para, topK=10, withWeight=False)
            paragraph_keywords.append(keywords)
        
        return paragraph_keywords
    
    def get_relevant_context(self, page_title: str, page_content: str, top_k: int = 5) -> str:
        """
        获取与当前页面最相关的上下文
        
        Args:
            page_title: 页面标题
            page_content: 页面内容指令
            top_k: 返回最相关的前 k 个段落
        
        Returns:
            相关上下文文本
        """
        # 1. 提取查询关键词
        query_text = f"{page_title} {page_content}"
        query_keywords = self._extract_keywords(query_text)
        
        if not query_keywords:
            # 如果没有提取到关键词，返回文档开头部分
            return self._get_document_head()
        
        # 2. 计算每个段落与查询的相关性得分
        scores = self._calculate_relevance_scores(query_keywords)
        
        # 3. 获取得分最高的段落
        top_paragraphs = self._get_top_paragraphs(scores, top_k)
        
        # 4. 组装上下文
        context = self._assemble_context(top_paragraphs, query_keywords)
        
        return context
    
    def _extract_keywords(self, text: str, top_k: int = 15) -> List[str]:
        """提取文本关键词"""
        # 使用 TF-IDF 提取关键词
        keywords = jieba.analyse.extract_tags(text, topK=top_k, withWeight=False)
        
        # 同时提取文本中的数字（数字往往是重要信息）
        numbers = re.findall(r'\d+(?:\.\d+)?(?:[亿万千百十%])?', text)
        
        # 提取专有名词（大写字母开头的词、机构名等）
        proper_nouns = re.findall(r'[A-Z][A-Za-z]+|[《【][^》】]+[》】]', text)
        
        # 合并所有关键词
        all_keywords = keywords + numbers + proper_nouns
        
        return list(set(all_keywords))  # 去重
    
    def _calculate_relevance_scores(self, query_keywords: List[str]) -> List[float]:
        """计算每个段落与查询的相关性得分"""
        scores = []
        
        for i, para_keywords in enumerate(self.paragraph_keywords):
            # 方法1：关键词重叠度
            overlap = len(set(query_keywords) & set(para_keywords))
            
            # 方法2：直接文本匹配（更精确）
            para_text = self.paragraphs[i]
            direct_matches = sum(1 for kw in query_keywords if kw in para_text)
            
            # 方法3：数字匹配（如果查询中有数字，优先匹配包含数字的段落）
            has_numbers = bool(re.search(r'\d+', para_text))
            number_bonus = 0.5 if has_numbers and any(re.search(r'\d', kw) for kw in query_keywords) else 0
            
            # 综合得分
            score = overlap * 1.0 + direct_matches * 2.0 + number_bonus
            scores.append(score)
        
        return scores
    
    def _get_top_paragraphs(self, scores: List[float], top_k: int) -> List[Tuple[int, str, float]]:
        """获取得分最高的段落"""
        # 按得分排序
        indexed_scores = [(i, self.paragraphs[i], score) for i, score in enumerate(scores)]
        indexed_scores.sort(key=lambda x: x[2], reverse=True)
        
        # 返回前 top_k 个
        return indexed_scores[:top_k]
    
    def _assemble_context(self, top_paragraphs: List[Tuple[int, str, float]], query_keywords: List[str]) -> str:
        """组装上下文文本"""
        context_parts = []
        current_length = 0
        
        for idx, para, score in top_paragraphs:
            # 检查是否超过最大长度
            if current_length + len(para) > self.max_context_length:
                # 如果超过，截取部分内容
                remaining = self.max_context_length - current_length
                if remaining > 100:  # 至少保留 100 字
                    para = para[:remaining] + "..."
                else:
                    break
            
            # 添加段落标记（方便 AI 识别）
            context_parts.append(f"【相关段落 {len(context_parts)+1}】\n{para}")
            current_length += len(para)
        
        # 如果没有找到相关内容，返回文档开头
        if not context_parts:
            return self._get_document_head()
        
        # 在开头添加关键词提示
        keyword_hint = f"【本页关键词】：{', '.join(query_keywords[:10])}\n\n"
        
        return keyword_hint + "\n\n".join(context_parts)
    
    def _get_document_head(self) -> str:
        """获取文档开头部分（作为兜底）"""
        head_text = self.full_document[:self.max_context_length]
        return f"【文档开头部分】\n{head_text}"
    
    def get_full_context_summary(self) -> str:
        """获取全文档摘要（用于封面、目录等特殊页面）"""
        # 提取文档的关键信息
        # 1. 提取所有标题
        titles = re.findall(r'^[一二三四五六七八九十]+[、．.].*$|^第[一二三四五六七八九十\d]+[章节部分].*$', 
                           self.full_document, re.MULTILINE)
        
        # 2. 提取关键数字
        numbers = re.findall(r'\d+(?:\.\d+)?[亿万千百%]', self.full_document)
        number_summary = "、".join(list(set(numbers))[:10])
        
        # 3. 提取核心关键词
        keywords = jieba.analyse.extract_tags(self.full_document, topK=20, withWeight=False)
        
        summary = f"""
【文档结构】
{chr(10).join(titles[:10])}

【核心数据】
{number_summary}

【关键词】
{', '.join(keywords)}

【文档开头】
{self.full_document[:500]}...
"""
        return summary


class SmartContextInjector:
    """智能上下文注入器 - 根据页面类型选择注入策略"""
    
    def __init__(self, context_manager: ContextManager):
        self.context_manager = context_manager
    
    def get_context_for_page(self, page_type: str, page_title: str, page_content: str) -> str:
        """
        根据页面类型获取合适的上下文
        
        Args:
            page_type: 页面类型（COVER, AGENDA, SECTION, CONTENT, CLOSING）
            page_title: 页面标题
            page_content: 页面内容指令
        
        Returns:
            上下文文本
        """
        if page_type in ['COVER', 'AGENDA']:
            # 封面和目录：使用全文档摘要
            return self.context_manager.get_full_context_summary()
        
        elif page_type == 'SECTION':
            # 章节过场页：使用该章节的概述
            return self.context_manager.get_relevant_context(page_title, page_content, top_k=3)
        
        elif page_type == 'CONTENT':
            # 正文页：使用精确检索
            return self.context_manager.get_relevant_context(page_title, page_content, top_k=5)
        
        elif page_type == 'CLOSING':
            # 封底：使用全文档摘要
            return self.context_manager.get_full_context_summary()
        
        else:
            # 默认：使用相关内容检索
            return self.context_manager.get_relevant_context(page_title, page_content, top_k=5)


def test_context_manager():
    """测试上下文管理器"""
    # 测试文本
    test_doc = """
    第一章 产业现状分析
    
    深圳生物医药产业规模达到500亿元，同比增长20%。其中创新药占比35%，医疗器械占比45%。
    龙头企业包括华大基因、迈瑞医疗等，年营收超过100亿元。
    
    第二章 存在问题
    
    当前面临的主要问题包括：研发投入不足，仅占营收的8%；高端人才缺乏，博士学历人才仅占5%。
    此外，产业链不完整，关键原料依赖进口。
    
    第三章 发展建议
    
    建议加大研发投入，设立100亿元产业基金；引进海外高层次人才，提供住房补贴和科研启动经费。
    同时，建设产业园区，完善上下游配套。
    """
    
    cm = ContextManager(test_doc, max_context_length=500)
    injector = SmartContextInjector(cm)
    
    # 测试检索
    context = injector.get_context_for_page(
        'CONTENT',
        '生物医药产业规模分析',
        '展示产业规模、增长率、细分领域占比'
    )
    
    print("检索结果：")
    print(context)


if __name__ == "__main__":
    test_context_manager()
