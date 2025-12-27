"""
PayJS 支付模块

@input:  config (PAYJS_MCHID, PAYJS_KEY)
@output: create_payment() -> 创建支付订单，返回二维码 URL
         check_payment() -> 查询订单支付状态
@pos:    被 server.py 的支付接口调用

使用 PayJS Native 扫码支付：
1. 用户点击下载 -> 前端调用 /api/payment/create
2. 后端生成订单并返回二维码
3. 前端展示二维码，用户扫码支付
4. 前端轮询 /api/payment/check 等待支付完成
5. 支付成功后解锁下载
"""

import hashlib
import time
import httpx
import logging
from typing import Optional, Tuple
import config

logger = logging.getLogger(__name__)

# PayJS API 端点
PAYJS_NATIVE_URL = "https://payjs.cn/api/native"
PAYJS_CHECK_URL = "https://payjs.cn/api/check"

def _sign(params: dict) -> str:
    """生成 PayJS 签名"""
    # 1. 按 key 排序
    sorted_params = sorted(params.items())
    # 2. 拼接成 key=value&key=value 格式
    sign_str = "&".join(f"{k}={v}" for k, v in sorted_params if v)
    # 3. 追加密钥
    sign_str += f"&key={config.PAYJS_KEY}"
    # 4. MD5 并大写
    return hashlib.md5(sign_str.encode()).hexdigest().upper()


async def create_payment(
    order_id: str,
    amount_yuan: float,
    body: str = "AI演示文稿下载"
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    创建 PayJS Native 扫码支付订单
    
    Args:
        order_id: 内部订单号（唯一）
        amount_yuan: 金额（元）
        body: 订单描述
        
    Returns:
        (success, qrcode_url, payjs_order_id)
    """
    if not config.PAYJS_MCHID or not config.PAYJS_KEY:
        logger.error("PayJS credentials not configured")
        return False, None, None
    
    # 金额转为分
    amount_fen = int(amount_yuan * 100)
    
    params = {
        "mchid": config.PAYJS_MCHID,
        "total_fee": str(amount_fen),
        "out_trade_no": order_id,
        "body": body,
    }
    params["sign"] = _sign(params)
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(PAYJS_NATIVE_URL, data=params, timeout=10)
            data = resp.json()
            
        if data.get("return_code") == 1:
            qrcode = data.get("qrcode")  # 二维码内容（用于生成二维码图片）
            code_url = data.get("code_url")  # 微信支付链接
            payjs_order_id = data.get("payjs_order_id")
            logger.info(f"PayJS order created: {order_id} -> {payjs_order_id}")
            return True, qrcode or code_url, payjs_order_id
        else:
            logger.error(f"PayJS error: {data}")
            return False, None, None
            
    except Exception as e:
        logger.error(f"PayJS request failed: {e}")
        return False, None, None


async def check_payment(payjs_order_id: str) -> Tuple[bool, int]:
    """
    查询 PayJS 订单支付状态
    
    Args:
        payjs_order_id: PayJS 返回的订单号
        
    Returns:
        (is_paid, status_code)
        status_code: 0=未支付, 1=已支付
    """
    if not config.PAYJS_MCHID or not config.PAYJS_KEY:
        return False, -1
    
    params = {
        "payjs_order_id": payjs_order_id,
    }
    params["sign"] = _sign(params)
    
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(PAYJS_CHECK_URL, data=params, timeout=10)
            data = resp.json()
            
        if data.get("return_code") == 1:
            status = data.get("status", 0)  # 0=待支付, 1=已支付
            return status == 1, status
        else:
            return False, -1
            
    except Exception as e:
        logger.error(f"PayJS check failed: {e}")
        return False, -1
