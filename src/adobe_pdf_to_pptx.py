#!/usr/bin/env python3
"""
Adobe PDF Services API - PDF to PPTX Converter
将PDF文件转换为PowerPoint演示文稿
"""

import logging
import os
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse

from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
from adobe.pdfservices.operation.config.client_config import ClientConfig
from adobe.pdfservices.operation.config.proxy.proxy_scheme import ProxyScheme
from adobe.pdfservices.operation.config.proxy.proxy_server_config import ProxyServerConfig
from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
from adobe.pdfservices.operation.io.stream_asset import StreamAsset
from adobe.pdfservices.operation.pdf_services import PDFServices
from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
from adobe.pdfservices.operation.pdfjobs.jobs.export_pdf_job import ExportPDFJob
from adobe.pdfservices.operation.pdfjobs.params.export_pdf.export_pdf_params import ExportPDFParams
from adobe.pdfservices.operation.pdfjobs.params.export_pdf.export_pdf_target_format import ExportPDFTargetFormat
from adobe.pdfservices.operation.pdfjobs.result.export_pdf_result import ExportPDFResult
from adobe.pdfservices.operation.pdfjobs.jobs.create_pdf_job import CreatePDFJob
from adobe.pdfservices.operation.pdfjobs.result.create_pdf_result import CreatePDFResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFToPPTXConverter:
    """PDF到PPTX转换器"""
    
    def __init__(self):
        """初始化转换器"""
        try:
            self.client_id = os.getenv('PDF_SERVICES_CLIENT_ID')
            self.client_secret = os.getenv('PDF_SERVICES_CLIENT_SECRET')
            
            if not self.client_id or not self.client_secret:
                raise ValueError(
                    "缺少Adobe API凭证。请设置环境变量:\n"
                    "export PDF_SERVICES_CLIENT_ID=<your_client_id>\n"
                    "export PDF_SERVICES_CLIENT_SECRET=<your_client_secret>"
                )
            
            self.credentials = ServicePrincipalCredentials(
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            
            # 配置代理（如果系统环境变量中有代理设置）
            client_config = self._create_client_config()
            
            self.pdf_services = PDFServices(
                credentials=self.credentials,
                client_config=client_config
            )
            logger.info("✓ Adobe PDF Services已初始化")
            
        except Exception as e:
            logger.error(f"✗ 初始化失败: {e}")
            raise
    
    @staticmethod
    def _create_client_config() -> ClientConfig:
        """创建客户端配置，包括代理设置"""
        # 检查系统环境变量中的代理设置
        https_proxy = os.getenv('https_proxy') or os.getenv('HTTPS_PROXY')
        http_proxy = os.getenv('http_proxy') or os.getenv('HTTP_PROXY')
        
        proxy_config = None
        
        if https_proxy:
            logger.info(f"📡 检测到HTTPS代理: {https_proxy}")
            proxy_config = PDFToPPTXConverter._parse_proxy_url(https_proxy)
        elif http_proxy:
            logger.info(f"📡 检测到HTTP代理: {http_proxy}")
            proxy_config = PDFToPPTXConverter._parse_proxy_url(http_proxy)
        
        if proxy_config:
            logger.info(f"✓ 代理已配置: {proxy_config['host']}:{proxy_config['port']}")
            return ClientConfig(
                connect_timeout=60000,    # 60 秒连接超时
                read_timeout=300000,      # 5 分钟读取超时（大文件需要更长时间）
                proxy_server_config=ProxyServerConfig(
                    host=proxy_config['host'],
                    scheme=proxy_config['scheme'],
                    port=proxy_config['port']
                )
            )
        else:
            # 无代理配置
            return ClientConfig(
                connect_timeout=60000,    # 60 秒连接超时
                read_timeout=300000       # 5 分钟读取超时
            )
    
    @staticmethod
    def _parse_proxy_url(proxy_url: str) -> dict:
        """解析代理URL"""
        parsed = urlparse(proxy_url)
        scheme = ProxyScheme.HTTP if parsed.scheme == 'http' else ProxyScheme.HTTPS
        port = parsed.port or (80 if parsed.scheme == 'http' else 443)
        
        return {
            'host': parsed.hostname,
            'port': port,
            'scheme': scheme
        }
    
    def convert_html_to_pdf(self, input_path: str, output_path: Optional[str] = None) -> str:
        """
        将HTML文件或HTML包(ZIP)转换为PDF
        
        Args:
            input_path: .html文件或包含index.html的.zip文件路径
            output_path: 输出PDF文件路径
            
        Returns:
            输出文件路径
        """
        try:
            logger.info(f"📄 [CreatePDF] 开始转换: {input_path}")
            
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"文件不存在: {input_path}")
            
            file_ext = os.path.splitext(input_path.lower())[1]
            if file_ext == '.zip':
                mime_type = PDFServicesMediaType.ZIP
            elif file_ext in ['.html', '.htm']:
                mime_type = PDFServicesMediaType.HTML
            else:
                mime_type = PDFServicesMediaType.HTML # Default fallback
            
            with open(input_path, 'rb') as f:
                input_stream = f.read()
            
            logger.info(f"☁️  上传文件({file_ext})到Adobe云...")
            input_asset = self.pdf_services.upload(
                input_stream=input_stream,
                mime_type=mime_type
            )
            
            logger.info("🚀 提交CreatePDF任务...")
            # CreatePDFJob 无需参数，默认自适应
            create_pdf_job = CreatePDFJob(input_asset=input_asset)
            
            location = self.pdf_services.submit(create_pdf_job)
            
            logger.info("⏳ 等待渲染完成...")
            pdf_services_response = self.pdf_services.get_job_result(
                location,
                CreatePDFResult
            )
            
            result_asset = pdf_services_response.get_result().get_asset()
            stream_asset = self.pdf_services.get_content(result_asset)
            
            if output_path is None:
                output_path = zip_path.replace('.zip', '.pdf')
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            logger.info(f"💾 保存PDF: {output_path}")
            with open(output_path, "wb") as f:
                f.write(stream_asset.get_input_stream())
                
            return output_path
            
        except Exception as e:
            logger.error(f"✗ HTML转PDF失败: {e}")
            raise

    
    def convert_pdf_to_pptx(self, pdf_path: str, output_path: Optional[str] = None) -> str:
        """
        将PDF转换为PPTX
        
        Args:
            pdf_path: PDF文件路径
            output_path: 输出PPTX文件路径（可选）
        
        Returns:
            输出文件路径
        """
        try:
            logger.info(f"📄 开始转换: {pdf_path}")
            
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
            
            with open(pdf_path, 'rb') as f:
                input_stream = f.read()
            
            logger.info(f"📦 文件大小: {len(input_stream) / 1024 / 1024:.2f} MB")
            
            logger.info("☁️  上传文件到Adobe云存储...")
            input_asset = self.pdf_services.upload(
                input_stream=input_stream,
                mime_type=PDFServicesMediaType.PDF
            )
            
            logger.info("⚙️  配置转换参数...")
            export_pdf_params = ExportPDFParams(
                target_format=ExportPDFTargetFormat.PPTX
            )
            
            export_pdf_job = ExportPDFJob(
                input_asset=input_asset,
                export_pdf_params=export_pdf_params
            )
            
            logger.info("🚀 提交转换任务...")
            location = self.pdf_services.submit(export_pdf_job)
            
            logger.info("⏳ 等待转换完成...")
            pdf_services_response = self.pdf_services.get_job_result(
                location,
                ExportPDFResult
            )
            
            result_asset: CloudAsset = pdf_services_response.get_result().get_asset()
            stream_asset: StreamAsset = self.pdf_services.get_content(result_asset)
            
            if output_path is None:
                output_path = self._generate_output_path(pdf_path)
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            logger.info(f"💾 保存文件: {output_path}")
            with open(output_path, "wb") as f:
                f.write(stream_asset.get_input_stream())
            
            file_size = os.path.getsize(output_path) / 1024 / 1024
            logger.info(f"✓ 转换成功! 文件大小: {file_size:.2f} MB")
            
            return output_path
            
        except (ServiceApiException, ServiceUsageException, SdkException) as e:
            logger.error(f"✗ Adobe API错误: {e}")
            raise
        except Exception as e:
            logger.error(f"✗ 转换失败: {e}")
            raise
    
    @staticmethod
    def _generate_output_path(pdf_path: str) -> str:
        """生成输出文件路径"""
        now = datetime.now()
        time_stamp = now.strftime("%Y-%m-%dT%H-%M-%S")
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_dir = "output/PDFToPPTX"
        os.makedirs(output_dir, exist_ok=True)
        return f"{output_dir}/{base_name}_{time_stamp}.pptx"


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python adobe_pdf_to_pptx.py <pdf_file> [output_pptx]")
        print("示例: python adobe_pdf_to_pptx.py input.pdf output.pptx")
        sys.exit(1)
    
    pdf_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        converter = PDFToPPTXConverter()
        result = converter.convert_pdf_to_pptx(pdf_file, output_file)
        print(f"\n✓ 转换完成: {result}")
    except Exception as e:
        print(f"\n✗ 转换失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
