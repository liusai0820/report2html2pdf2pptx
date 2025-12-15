"""PDF生成器 - 使用Puppeteer将HTML转换为PDF"""
import asyncio
import os
import shutil
from pyppeteer import launch
from rich.console import Console

console = Console()

def find_chrome_path():
    """查找系统Chrome路径"""
    possible_paths = [
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',  # macOS
        '/Applications/Chromium.app/Contents/MacOS/Chromium',  # macOS Chromium
        'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',  # Windows
        'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',  # Windows 32-bit
        '/usr/bin/google-chrome',  # Linux
        '/usr/bin/chromium-browser',  # Linux Chromium
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # 尝试使用which命令查找
    chrome_cmd = shutil.which('google-chrome') or shutil.which('chromium') or shutil.which('chrome')
    if chrome_cmd:
        return chrome_cmd
    
    return None

class PDFGenerator:
    def __init__(self):
        self.browser = None
    
    async def __aenter__(self):
        chrome_path = find_chrome_path()
        
        launch_options = {
            'headless': True,
            'args': [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
            ]
        }
        
        if chrome_path:
            console.print(f"[green]✓[/green] 使用系统Chrome: {chrome_path}")
            launch_options['executablePath'] = chrome_path
        else:
            console.print("[yellow]⚠[/yellow] 未找到系统Chrome，将下载Chromium...")
        
        self.browser = await launch(**launch_options)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.browser:
            await self.browser.close()
    
    async def generate_pdf(self, html_path: str, pdf_path: str, 
                          landscape: bool = True, format: str = 'A4', timeout: int = 60):
        """生成PDF"""
        if not os.path.exists(html_path):
            raise FileNotFoundError(f"HTML文件不存在: {html_path}")
        
        console.print(f"[cyan]正在生成PDF...[/cyan]")
        
        try:
            page = await self.browser.newPage()
            
            # 设置视口大小（1280x720 for 16:9）
            await page.setViewport({'width': 1280, 'height': 720})
            
            # 加载HTML文件（使用更宽松的等待条件和超时）
            file_url = f'file://{os.path.abspath(html_path)}'
            console.print(f"[dim]加载HTML: {file_url}[/dim]")
            
            # 使用domcontentloaded而不是networkidle0，更快
            await asyncio.wait_for(
                page.goto(file_url, {'waitUntil': 'domcontentloaded', 'timeout': 30000}),
                timeout=timeout
            )
            
            # 等待字体加载完成 - 解决Type3字体问题
            try:
                await asyncio.wait_for(
                    page.evaluateHandle('document.fonts.ready'),
                    timeout=10
                )
            except:
                pass  # 字体加载超时，继续处理
            
            # 等待一小段时间确保渲染完成
            await asyncio.sleep(1)
            
            # 生成PDF
            os.makedirs(os.path.dirname(pdf_path) if os.path.dirname(pdf_path) else '.', exist_ok=True)
            
            pdf_options = {
                'path': pdf_path,
                'format': format,
                'landscape': landscape,
                'printBackground': True,
                'margin': {
                    'top': '0',
                    'right': '0',
                    'bottom': '0',
                    'left': '0'
                },
                'preferCSSPageSize': True,
                # 字体嵌入选项 - 解决Type3字体问题
                'displayHeaderFooter': False,
            }
            
            console.print(f"[dim]生成PDF文件...[/dim]")
            await asyncio.wait_for(page.pdf(pdf_options), timeout=timeout)
            await page.close()
            
            console.print(f"[green]✓[/green] PDF已生成: {pdf_path}")
            
            # 显示文件大小
            if os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path) / 1024 / 1024
                console.print(f"[dim]文件大小: {file_size:.2f} MB[/dim]")
            else:
                console.print(f"[yellow]⚠[/yellow] PDF文件未找到")
                
        except asyncio.TimeoutError:
            console.print(f"[red]✗[/red] PDF生成超时（{timeout}秒）")
            raise
        except Exception as e:
            console.print(f"[red]✗[/red] PDF生成失败: {str(e)}")
            raise

async def generate_pdf_from_html(html_path: str, pdf_path: str):
    """便捷函数：从HTML生成PDF"""
    async with PDFGenerator() as generator:
        await generator.generate_pdf(html_path, pdf_path)
