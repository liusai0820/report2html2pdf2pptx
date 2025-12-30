"""
Cloudflare R2 存储客户端

@input:  config (R2 凭证), 本地文件
@output: R2 上传/下载/URL生成
@pos:    存储抽象层，支持本地开发和云端部署

⚠️ 一旦我被更新，务必更新：
   1. 我的头部注释
   2. /src/_FOLDER.md
"""
import os
import logging
from pathlib import Path
from typing import Optional, BinaryIO, Union
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

# Lazy import boto3 to avoid startup overhead when not using R2
_s3_client = None

def _get_s3_client():
    """延迟初始化 S3 客户端"""
    global _s3_client
    if _s3_client is None:
        import boto3
        from botocore.config import Config
        
        # R2 配置
        r2_account_id = os.getenv("R2_ACCOUNT_ID", "")
        r2_access_key = os.getenv("R2_ACCESS_KEY_ID", "")
        r2_secret_key = os.getenv("R2_SECRET_ACCESS_KEY", "")
        
        if not all([r2_account_id, r2_access_key, r2_secret_key]):
            logger.warning("R2 credentials not configured, storage features disabled")
            return None
        
        _s3_client = boto3.client(
            's3',
            endpoint_url=f'https://{r2_account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=r2_access_key,
            aws_secret_access_key=r2_secret_key,
            config=Config(
                signature_version='s3v4',
                retries={'max_attempts': 3, 'mode': 'adaptive'}
            ),
            region_name='auto'  # R2 不需要特定 region
        )
    return _s3_client


class R2Storage:
    """Cloudflare R2 存储客户端"""
    
    def __init__(self):
        self.bucket = os.getenv("R2_BUCKET_NAME", "slidecraft")
        self.public_url = os.getenv("R2_PUBLIC_URL", "")  # 如: https://cdn.yourdomain.com
        self.enabled = bool(os.getenv("R2_ACCOUNT_ID"))
        
        if self.enabled:
            logger.info(f"R2 Storage enabled: bucket={self.bucket}")
        else:
            logger.info("R2 Storage disabled, using local storage")
    
    def upload_file(
        self, 
        local_path: Union[str, Path], 
        remote_key: str,
        content_type: Optional[str] = None
    ) -> Optional[str]:
        """
        上传文件到 R2
        
        Args:
            local_path: 本地文件路径
            remote_key: R2 中的 key (路径)
            content_type: MIME 类型
            
        Returns:
            公开 URL 或 None
        """
        if not self.enabled:
            logger.debug(f"R2 disabled, skipping upload: {local_path}")
            return None
        
        client = _get_s3_client()
        if not client:
            return None
        
        local_path = Path(local_path)
        if not local_path.exists():
            logger.error(f"File not found: {local_path}")
            return None
        
        # 自动检测 content type
        if content_type is None:
            content_type = self._guess_content_type(local_path)
        
        try:
            extra_args = {'ContentType': content_type}
            
            client.upload_file(
                str(local_path),
                self.bucket,
                remote_key,
                ExtraArgs=extra_args
            )
            
            url = self._get_public_url(remote_key)
            logger.info(f"Uploaded to R2: {remote_key} -> {url}")
            return url
            
        except Exception as e:
            logger.error(f"R2 upload failed: {e}")
            return None
    
    def upload_fileobj(
        self,
        file_obj: BinaryIO,
        remote_key: str,
        content_type: Optional[str] = None
    ) -> Optional[str]:
        """
        上传文件对象到 R2
        
        Args:
            file_obj: 文件对象 (如 request.file)
            remote_key: R2 中的 key
            content_type: MIME 类型
            
        Returns:
            公开 URL 或 None
        """
        if not self.enabled:
            return None
        
        client = _get_s3_client()
        if not client:
            return None
        
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            client.upload_fileobj(
                file_obj,
                self.bucket,
                remote_key,
                ExtraArgs=extra_args if extra_args else None
            )
            
            url = self._get_public_url(remote_key)
            logger.info(f"Uploaded fileobj to R2: {remote_key}")
            return url
            
        except Exception as e:
            logger.error(f"R2 upload_fileobj failed: {e}")
            return None
    
    def upload_directory(
        self, 
        local_dir: Union[str, Path], 
        remote_prefix: str
    ) -> dict:
        """
        上传整个目录到 R2
        
        Args:
            local_dir: 本地目录路径
            remote_prefix: R2 中的前缀 (如 "outputs/task_123/")
            
        Returns:
            上传结果字典 {relative_path: url}
        """
        if not self.enabled:
            return {}
        
        local_dir = Path(local_dir)
        if not local_dir.exists() or not local_dir.is_dir():
            logger.error(f"Directory not found: {local_dir}")
            return {}
        
        results = {}
        
        for file_path in local_dir.rglob("*"):
            if file_path.is_file():
                relative = file_path.relative_to(local_dir)
                remote_key = f"{remote_prefix.rstrip('/')}/{relative}"
                
                url = self.upload_file(file_path, remote_key)
                if url:
                    results[str(relative)] = url
        
        logger.info(f"Uploaded directory: {len(results)} files to {remote_prefix}")
        return results
    
    def download_file(
        self, 
        remote_key: str, 
        local_path: Union[str, Path]
    ) -> bool:
        """
        从 R2 下载文件
        
        Args:
            remote_key: R2 中的 key
            local_path: 本地保存路径
            
        Returns:
            是否成功
        """
        if not self.enabled:
            return False
        
        client = _get_s3_client()
        if not client:
            return False
        
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            client.download_file(self.bucket, remote_key, str(local_path))
            logger.info(f"Downloaded from R2: {remote_key}")
            return True
        except Exception as e:
            logger.error(f"R2 download failed: {e}")
            return False
    
    def delete_file(self, remote_key: str) -> bool:
        """删除 R2 中的文件"""
        if not self.enabled:
            return False
        
        client = _get_s3_client()
        if not client:
            return False
        
        try:
            client.delete_object(Bucket=self.bucket, Key=remote_key)
            logger.info(f"Deleted from R2: {remote_key}")
            return True
        except Exception as e:
            logger.error(f"R2 delete failed: {e}")
            return False
    
    def delete_prefix(self, prefix: str) -> int:
        """删除 R2 中指定前缀的所有文件"""
        if not self.enabled:
            return 0
        
        client = _get_s3_client()
        if not client:
            return 0
        
        try:
            # 列出所有匹配的对象
            paginator = client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket, Prefix=prefix)
            
            deleted = 0
            for page in pages:
                if 'Contents' not in page:
                    continue
                
                objects = [{'Key': obj['Key']} for obj in page['Contents']]
                if objects:
                    client.delete_objects(
                        Bucket=self.bucket,
                        Delete={'Objects': objects}
                    )
                    deleted += len(objects)
            
            logger.info(f"Deleted {deleted} files with prefix: {prefix}")
            return deleted
            
        except Exception as e:
            logger.error(f"R2 delete_prefix failed: {e}")
            return 0
    
    def generate_presigned_url(
        self, 
        remote_key: str, 
        expires_in: int = 3600
    ) -> Optional[str]:
        """
        生成临时签名 URL（用于私有文件）
        
        Args:
            remote_key: R2 中的 key
            expires_in: 过期时间（秒），默认 1 小时
            
        Returns:
            签名 URL 或 None
        """
        if not self.enabled:
            return None
        
        client = _get_s3_client()
        if not client:
            return None
        
        try:
            url = client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': remote_key},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            logger.error(f"R2 presigned URL failed: {e}")
            return None
    
    def file_exists(self, remote_key: str) -> bool:
        """检查文件是否存在"""
        if not self.enabled:
            return False
        
        client = _get_s3_client()
        if not client:
            return False
        
        try:
            client.head_object(Bucket=self.bucket, Key=remote_key)
            return True
        except:
            return False
    
    def _get_public_url(self, remote_key: str) -> str:
        """获取公开访问 URL"""
        if self.public_url:
            # 使用自定义域名
            return urljoin(self.public_url.rstrip('/') + '/', remote_key)
        else:
            # 使用 R2 默认公开 URL (需要启用 public access)
            account_id = os.getenv("R2_ACCOUNT_ID", "")
            return f"https://{self.bucket}.{account_id}.r2.dev/{remote_key}"
    
    def _guess_content_type(self, path: Path) -> str:
        """根据文件扩展名猜测 MIME 类型"""
        ext = path.suffix.lower()
        mime_types = {
            '.html': 'text/html; charset=utf-8',
            '.css': 'text/css; charset=utf-8',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.pdf': 'application/pdf',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.webp': 'image/webp',
            '.woff': 'font/woff',
            '.woff2': 'font/woff2',
            '.ttf': 'font/ttf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.md': 'text/markdown',
            '.txt': 'text/plain',
        }
        return mime_types.get(ext, 'application/octet-stream')


# 全局单例
_r2_storage: Optional[R2Storage] = None

def get_storage() -> R2Storage:
    """获取存储客户端单例"""
    global _r2_storage
    if _r2_storage is None:
        _r2_storage = R2Storage()
    return _r2_storage


# 便捷函数
def upload_output_to_r2(output_dir: Union[str, Path], task_id: str) -> dict:
    """
    将输出目录上传到 R2（按日期分层）
    
    Args:
        output_dir: 本地输出目录
        task_id: 任务 ID (格式: xxx_YYYYMMDD_HHMMSS_v2)
        
    Returns:
        {
            "base_url": "https://cdn.xxx/outputs/2024/12/30/task_id/",
            "files": {...},
            "local": False
        }
        
    存储结构:
        outputs/
        ├── 2024/
        │   └── 12/
        │       └── 30/
        │           ├── 文档名_160000_v2/
        │           └── 另一个任务_170000_v2/
    """
    import re
    from datetime import datetime
    
    storage = get_storage()
    
    if not storage.enabled:
        # 本地模式，返回本地 URL
        return {
            "base_url": f"/output/{task_id}/",
            "files": {},
            "local": True
        }
    
    # 从 task_id 中提取日期 (格式: xxx_YYYYMMDD_HHMMSS_v2)
    match = re.search(r'_(\d{4})(\d{2})(\d{2})_(\d{6})(?:_v2)?$', task_id)
    
    if match:
        year, month, day, time_part = match.groups()
        # 简化 task_id：去掉日期，只保留文档名和时间
        base_name = task_id[:match.start()]
        short_task_id = f"{base_name}_{time_part}"
        if task_id.endswith('_v2'):
            short_task_id += '_v2'
        
        prefix = f"outputs/{year}/{month}/{day}/{short_task_id}"
    else:
        # 无法解析日期，使用当前日期
        now = datetime.now()
        prefix = f"outputs/{now.year}/{now.month:02d}/{now.day:02d}/{task_id}"
    
    files = storage.upload_directory(output_dir, prefix)
    
    return {
        "base_url": storage._get_public_url(f"{prefix}/"),
        "files": files,
        "local": False,
        "prefix": prefix  # 返回实际使用的前缀
    }


def cleanup_old_outputs(days: int = 7) -> int:
    """
    清理超过指定天数的输出文件
    
    这个函数应该由定时任务调用
    """
    # TODO: 实现基于 R2 对象元数据的清理逻辑
    # 目前 R2 支持 lifecycle rules，建议在 Cloudflare Dashboard 配置
    logger.info(f"cleanup_old_outputs called with days={days}")
    return 0
