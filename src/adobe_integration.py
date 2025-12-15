#!/usr/bin/env python3
"""
Adobe PDF Services集成模块
提供PDF到PPTX的转换功能
"""

import logging
import os
from typing import Optional, List
from pathlib import Path

from adobe_pdf_to_pptx import PDFToPPTXConverter
from rich.console import Console

console = Console()
logger = logging.getLogger(__name__)


class AdobeIntegration:
    """Adobe PDF Services集成类"""
    
    def __init__(self):
        """初始化Adobe集成"""
        self.converter = None
        self._init_converter()
    
    def _init_converter(self):
        """初始化转换器"""
        try:
            self.converter = PDFToPPTXConverter()
            console.print("[green]✓[/green] Adobe PDF Services已初始化")
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] Adobe集成初始化失败: {e}")
            console.print("[dim]PDF到PPTX功能将不可用[/dim]")
    
    def is_available(self) -> bool:
        """检查Adobe服务是否可用"""
        return self.converter is not None
    
    def pdf_to_pptx(self, pdf_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        将PDF转换为PPTX
        
        Args:
            pdf_path: PDF文件路径
            output_path: 输出PPTX路径（可选）
        
        Returns:
            输出文件路径，如果失败返回None
        """
        if not self.is_available():
            console.print("[red]✗[/red] Adobe服务不可用")
            return None
        
        try:
            console.print(f"\n[cyan]📄 PDF转PPTX: {pdf_path}[/cyan]")
            result = self.converter.convert_pdf_to_pptx(pdf_path, output_path)
            console.print(f"[green]✓[/green] 转换成功: {result}")
            return result
        except Exception as e:
            console.print(f"[red]✗[/red] 转换失败: {e}")
            return None
    
    def batch_pdf_to_pptx(self, pdf_dir: str, output_dir: Optional[str] = None) -> List[str]:
        """
        批量转换PDF到PPTX
        
        Args:
            pdf_dir: PDF文件所在目录
            output_dir: 输出目录（可选）
        
        Returns:
            成功转换的文件列表
        """
        if not self.is_available():
            console.print("[red]✗[/red] Adobe服务不可用")
            return []
        
        pdf_files = list(Path(pdf_dir).glob("*.pdf"))
        if not pdf_files:
            console.print(f"[yellow]⚠[/yellow] 未找到PDF文件: {pdf_dir}")
            return []
        
        console.print(f"\n[cyan]📦 批量转换 {len(pdf_files)} 个PDF文件[/cyan]")
        
        results = []
        for i, pdf_file in enumerate(pdf_files, 1):
            console.print(f"[dim][{i}/{len(pdf_files)}][/dim] 处理: {pdf_file.name}")
            
            output_path = None
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, pdf_file.stem + ".pptx")
            
            result = self.pdf_to_pptx(str(pdf_file), output_path)
            if result:
                results.append(result)
        
        console.print(f"\n[green]✓[/green] 完成: {len(results)}/{len(pdf_files)} 个文件转换成功")
        return results


# 全局实例
_adobe_integration = None


def get_adobe_integration() -> AdobeIntegration:
    """获取Adobe集成实例"""
    global _adobe_integration
    if _adobe_integration is None:
        _adobe_integration = AdobeIntegration()
    return _adobe_integration


def pdf_to_pptx(pdf_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """便捷函数：PDF转PPTX"""
    integration = get_adobe_integration()
    return integration.pdf_to_pptx(pdf_path, output_path)


def batch_pdf_to_pptx(pdf_dir: str, output_dir: Optional[str] = None) -> List[str]:
    """便捷函数：批量PDF转PPTX"""
    integration = get_adobe_integration()
    return integration.batch_pdf_to_pptx(pdf_dir, output_dir)
