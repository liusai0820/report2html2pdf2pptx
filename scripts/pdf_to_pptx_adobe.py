#!/usr/bin/env python3
"""
PDF to PPTX Converter using Adobe PDF Services API

This script converts a PDF file to PPTX format using Adobe's cloud-based API.

Usage:
    python pdf_to_pptx_adobe.py <input_pdf> [output_pptx]

Requirements:
    - pdfservices-sdk>=4.0.0
    - Adobe PDF Services credentials configured in config/.env
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
env_path = project_root / "config" / ".env"
load_dotenv(env_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def convert_pdf_to_pptx(input_pdf_path: str, output_pptx_path: str = None) -> str:
    """
    Convert a PDF file to PPTX using Adobe PDF Services API.
    
    Args:
        input_pdf_path: Path to the input PDF file
        output_pptx_path: Optional path for the output PPTX file
        
    Returns:
        Path to the generated PPTX file
    """
    from adobe.pdfservices.operation.auth.service_principal_credentials import ServicePrincipalCredentials
    from adobe.pdfservices.operation.exception.exceptions import ServiceApiException, ServiceUsageException, SdkException
    from adobe.pdfservices.operation.io.cloud_asset import CloudAsset
    from adobe.pdfservices.operation.io.stream_asset import StreamAsset
    from adobe.pdfservices.operation.pdf_services import PDFServices
    from adobe.pdfservices.operation.pdf_services_media_type import PDFServicesMediaType
    from adobe.pdfservices.operation.pdfjobs.jobs.export_pdf_job import ExportPDFJob
    from adobe.pdfservices.operation.pdfjobs.params.export_pdf.export_pdf_params import ExportPDFParams
    from adobe.pdfservices.operation.pdfjobs.params.export_pdf.export_pdf_target_format import ExportPDFTargetFormat
    from adobe.pdfservices.operation.pdfjobs.result.export_pdf_result import ExportPDFResult
    from adobe.pdfservices.operation.config.client_config import ClientConfig
    
    # Validate input file
    input_path = Path(input_pdf_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input PDF not found: {input_pdf_path}")
    
    if not input_path.suffix.lower() == '.pdf':
        raise ValueError(f"Input file must be a PDF: {input_pdf_path}")
    
    # Set output path
    if output_pptx_path is None:
        output_pptx_path = str(input_path.with_suffix('.pptx'))
    
    output_path = Path(output_pptx_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Converting PDF to PPTX...")
    logger.info(f"  Input:  {input_pdf_path}")
    logger.info(f"  Output: {output_pptx_path}")
    
    # Get Adobe credentials
    client_id = os.getenv("ADOBE_CLIENT_ID")
    client_secret = os.getenv("ADOBE_CLIENT_SECRET")
    
    # Try reading from JSON if env vars are missing
    if not client_id or not client_secret:
        json_cred_path = project_root / "config" / "pdfservices-api-credentials.json"
        if json_cred_path.exists():
            import json
            with open(json_cred_path, 'r') as f:
                creds = json.load(f)
                client_id = creds.get("client_credentials", {}).get("client_id")
                client_secret = creds.get("client_credentials", {}).get("client_secret")
                logger.info(f"Using credentials from {json_cred_path}")

    if not client_id or not client_secret:
        raise ValueError(
            "Adobe API credentials not found. Please set ADOBE_CLIENT_ID and "
            "ADOBE_CLIENT_SECRET in config/.env or provide config/pdfservices-api-credentials.json"
        )
    
    try:
        # Initialize credentials
        credentials = ServicePrincipalCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        
        # Create client config with increased timeout to handle network instability
        logger.info("Setting up Adobe PDF Services with increased timeouts...")
        client_config = ClientConfig(
            connect_timeout=15000,
            read_timeout=180000
        )
        
        # Create PDF Services instance
        pdf_services = PDFServices(credentials=credentials, client_config=client_config)
        
        # Upload the PDF file
        logger.info("Uploading PDF to Adobe Cloud...")
        with open(input_pdf_path, 'rb') as file:
            input_stream = file.read()
        
        input_asset = pdf_services.upload(
            input_stream=input_stream,
            mime_type=PDFServicesMediaType.PDF
        )
        
        # Create export parameters for PPTX
        export_pdf_params = ExportPDFParams(
            target_format=ExportPDFTargetFormat.PPTX
        )
        
        # Create the export job
        logger.info("Creating export job...")
        export_pdf_job = ExportPDFJob(
            input_asset=input_asset,
            export_pdf_params=export_pdf_params
        )
        
        # Submit the job and wait for result
        logger.info("Processing... This may take a few minutes for large files.")
        location = pdf_services.submit(export_pdf_job)
        pdf_services_response = pdf_services.get_job_result(
            location,
            ExportPDFResult
        )
        
        # Get the result asset
        result_asset: CloudAsset = pdf_services_response.get_result().get_asset()
        stream_asset: StreamAsset = pdf_services.get_content(result_asset)
        
        # Save the PPTX file
        logger.info("Saving PPTX file...")
        with open(output_pptx_path, 'wb') as file:
            file.write(stream_asset.get_input_stream())
        
        logger.info(f"✅ Conversion successful!")
        logger.info(f"   Output saved to: {output_pptx_path}")
        
        return output_pptx_path
        
    except ServiceApiException as e:
        logger.error(f"Adobe API error: {e.message}")
        logger.error(f"Error code: {e.error_code}")
        raise
    except ServiceUsageException as e:
        logger.error(f"Service usage error: {e.message}")
        raise
    except SdkException as e:
        logger.error(f"SDK error: {e.message}")
        raise


def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_pptx_adobe.py <input_pdf> [output_pptx]")
        print("\nExample:")
        print("  python pdf_to_pptx_adobe.py document.pdf")
        print("  python pdf_to_pptx_adobe.py document.pdf presentation.pptx")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    output_pptx = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result_path = convert_pdf_to_pptx(input_pdf, output_pptx)
        print(f"\n🎉 Done! PPTX saved to: {result_path}")
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
