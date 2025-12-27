"""
虎皮椒支付 (XunHuPay) 模块

@input:  config (XUNHU_APPID, XUNHU_APPSECRET)
@output: create_payment() -> 创建支付订单，返回支付页面 URL
         check_payment() -> 查询订单支付状态
@pos:    被 server.py 的支付接口调用

API 文档: https://www.xunhupay.com/doc/api.html
支付网关: https://api.xunhupay.com/payment/do.html
"""

import hashlib
import time
import httpx
import logging
from typing import Optional, Tuple
from urllib.parse import urlencode
import config

logger = logging.getLogger(__name__)

# 虎皮椒 API 端点
XUNHU_GATEWAY_URL = "https://api.xunhupay.com/payment/do.html"
XUNHU_QUERY_URL = "https://api.xunhupay.com/payment/query.html"


def _generate_hash(params: dict, appsecret: str) -> str:
    """
    生成虎皮椒签名
    1. 按 key 字母排序
    2. 拼接成 key=value&key=value 格式
    3. 末尾追加 appsecret
    4. MD5 并小写
    """
    # 过滤空值和 hash 字段
    filtered = {k: v for k, v in params.items() if v and k != 'hash'}
    # 按 key 排序
    sorted_params = sorted(filtered.items())
    # 拼接
    sign_str = "&".join(f"{k}={v}" for k, v in sorted_params)
    # 追加密钥
    sign_str += appsecret
    # MD5
    return hashlib.md5(sign_str.encode()).hexdigest()


async def create_payment(
    order_id: str,
    amount_yuan: float,
    title: str = "AI演示文稿下载",
    notify_url: str = "",
    return_url: str = ""
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    创建虎皮椒支付订单
    
    Args:
        order_id: 商户订单号（唯一）
        amount_yuan: 金额（元）
        title: 订单标题
        notify_url: 异步通知回调地址
        return_url: 同步跳转地址
        
    Returns:
        (success, payment_url, trade_order_id)
        - payment_url: 跳转支付页面的 URL
        - trade_order_id: 虎皮椒订单号
    """
    if not config.XUNHU_APPID or not config.XUNHU_APPSECRET:
        logger.error("XunHuPay credentials not configured")
        return False, None, None
    
    # 构建请求参数
    params = {
        "version": "1.1",
        "appid": config.XUNHU_APPID,
        "trade_order_id": order_id,
        "total_fee": str(amount_yuan),
        "title": title,
        "time": str(int(time.time())),
        "notify_url": notify_url or config.XUNHU_NOTIFY_URL,
        "return_url": return_url,
        "nonce_str": hashlib.md5(str(time.time()).encode()).hexdigest()[:16],
    }
    
    # 生成签名
    params["hash"] = _generate_hash(params, config.XUNHU_APPSECRET)
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(XUNHU_GATEWAY_URL, data=params, timeout=15)
            data = resp.json()
            
        if data.get("errcode") == 0:
            # 成功
            payment_url = data.get("url") or data.get("url_qrcode")
            trade_order_id = data.get("order_id")  # 虎皮椒订单号
            logger.info(f"XunHuPay order created: {order_id} -> {trade_order_id}")
            return True, payment_url, trade_order_id
        else:
            logger.error(f"XunHuPay error: {data.get('errmsg', data)}")
            return False, None, None
            
    except Exception as e:
        logger.error(f"XunHuPay request failed: {e}")
        return False, None, None


async def check_payment(trade_order_id: str) -> Tuple[bool, str]:
    """
    查询虎皮椒订单支付状态
    
    Args:
        trade_order_id: 商户订单号
        
    Returns:
        (is_paid, status)
        status: OD (已支付), WP (待支付), CD (已取消)
    """
    if not config.XUNHU_APPID or not config.XUNHU_APPSECRET:
        return False, "NOT_CONFIGURED"
    
    params = {
        "appid": config.XUNHU_APPID,
        "out_trade_order": trade_order_id,
        "time": str(int(time.time())),
        "nonce_str": hashlib.md5(str(time.time()).encode()).hexdigest()[:16],
    }
    params["hash"] = _generate_hash(params, config.XUNHU_APPSECRET)
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(XUNHU_QUERY_URL, data=params, timeout=10)
            data = resp.json()
            
        if data.get("errcode") == 0:
            status = data.get("status", "WP")  # OD=已支付, WP=待支付, CD=已取消
            is_paid = status == "OD"
            return is_paid, status
        else:
            logger.warning(f"XunHuPay query error: {data.get('errmsg', data)}")
            return False, "ERROR"
            
    except Exception as e:
        logger.error(f"XunHuPay query failed: {e}")
        return False, "ERROR"


def verify_callback(params: dict) -> bool:
    """
    验证虎皮椒回调签名
    用于异步通知 (notify_url) 的签名验证
    """
    if not config.XUNHU_APPSECRET:
        return False
        
    received_hash = params.get("hash", "")
    calculated_hash = _generate_hash(params, config.XUNHU_APPSECRET)
    
    return received_hash == calculated_hash
