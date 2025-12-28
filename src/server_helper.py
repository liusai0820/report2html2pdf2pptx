
def _upload_and_notify(file_path, doc_name):
    """
    后台任务：上传并通知
    """
    try:
        from src.upload_utils import upload_to_r2, send_telegram_notify
        logger.info(f"后台任务开始: 上传 {doc_name}")
        url = upload_to_r2(file_path)
        if url:
            send_telegram_notify(doc_name, url)
            logger.info(f"后台任务完成: {doc_name} -> {url}")
        else:
            logger.error("上传失败，未发送通知")
    except Exception as e:
        logger.error(f"后台任务异常: {e}")
