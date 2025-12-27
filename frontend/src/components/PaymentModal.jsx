import React, { useState, useEffect } from 'react';
import { X, Loader2, Check, QrCode, CreditCard } from 'lucide-react';

/**
 * 支付弹窗组件
 * 展示微信支付二维码，轮询支付状态
 */
export default function PaymentModal({
    isOpen,
    onClose,
    onPaymentSuccess,
    generationId,
    price = 9.9
}) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [qrcodeUrl, setQrcodeUrl] = useState(null);
    const [orderId, setOrderId] = useState(null);
    const [payjsOrderId, setPayjsOrderId] = useState(null);
    const [isPaid, setIsPaid] = useState(false);
    const [polling, setPolling] = useState(false);

    // 创建订单
    useEffect(() => {
        if (!isOpen || !generationId) return;

        const createOrder = async () => {
            setLoading(true);
            setError(null);

            try {
                const resp = await fetch('/api/payment/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ generation_id: generationId })
                });
                const data = await resp.json();

                if (data.success) {
                    setQrcodeUrl(data.qrcode_url);
                    setOrderId(data.order_id);
                    setPayjsOrderId(data.payjs_order_id);
                    setPolling(true);
                } else {
                    setError(data.message || '创建订单失败');
                }
            } catch (e) {
                setError('网络错误，请重试');
            } finally {
                setLoading(false);
            }
        };

        createOrder();
    }, [isOpen, generationId]);

    // 轮询支付状态
    useEffect(() => {
        if (!polling || !payjsOrderId || !orderId) return;

        const checkPayment = async () => {
            try {
                const resp = await fetch('/api/payment/check', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        payjs_order_id: payjsOrderId,
                        order_id: orderId
                    })
                });
                const data = await resp.json();

                if (data.paid) {
                    setIsPaid(true);
                    setPolling(false);
                    // 通知父组件支付成功
                    setTimeout(() => {
                        onPaymentSuccess?.(data.download_url);
                    }, 1500);
                }
            } catch (e) {
                console.error('Check payment error:', e);
            }
        };

        // 每 2 秒检查一次
        const interval = setInterval(checkPayment, 2000);
        return () => clearInterval(interval);
    }, [polling, payjsOrderId, orderId, onPaymentSuccess]);

    // 关闭时重置状态
    const handleClose = () => {
        setPolling(false);
        setQrcodeUrl(null);
        setOrderId(null);
        setPayjsOrderId(null);
        setIsPaid(false);
        setError(null);
        onClose?.();
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                onClick={handleClose}
            />

            {/* Modal */}
            <div className="relative bg-white rounded-2xl shadow-2xl w-[380px] overflow-hidden animate-in zoom-in-95 fade-in duration-200">
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-400 to-green-600 flex items-center justify-center shadow-lg shadow-green-500/20">
                            <CreditCard className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h3 className="font-semibold text-slate-800">扫码支付</h3>
                            <p className="text-xs text-slate-500">微信扫码完成支付</p>
                        </div>
                    </div>
                    <button
                        onClick={handleClose}
                        className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
                    >
                        <X className="w-5 h-5 text-slate-400" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6">
                    {loading ? (
                        <div className="flex flex-col items-center justify-center py-12">
                            <Loader2 className="w-8 h-8 animate-spin text-slate-400" />
                            <p className="mt-3 text-sm text-slate-500">正在创建订单...</p>
                        </div>
                    ) : error ? (
                        <div className="flex flex-col items-center justify-center py-12">
                            <div className="w-16 h-16 rounded-full bg-red-50 flex items-center justify-center mb-4">
                                <X className="w-8 h-8 text-red-500" />
                            </div>
                            <p className="text-sm text-slate-600">{error}</p>
                            <button
                                onClick={() => window.location.reload()}
                                className="mt-4 px-4 py-2 text-sm bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
                            >
                                重试
                            </button>
                        </div>
                    ) : isPaid ? (
                        <div className="flex flex-col items-center justify-center py-12">
                            <div className="w-16 h-16 rounded-full bg-green-50 flex items-center justify-center mb-4 animate-in zoom-in duration-300">
                                <Check className="w-8 h-8 text-green-500" />
                            </div>
                            <p className="text-lg font-medium text-slate-800">支付成功!</p>
                            <p className="text-sm text-slate-500 mt-1">正在为您准备下载...</p>
                        </div>
                    ) : (
                        <div className="flex flex-col items-center">
                            {/* Price */}
                            <div className="mb-6 text-center">
                                <span className="text-4xl font-bold text-slate-800">¥{price}</span>
                                <p className="text-sm text-slate-500 mt-1">AI 演示文稿下载</p>
                            </div>

                            {/* QR Code */}
                            {qrcodeUrl ? (
                                <div className="relative">
                                    <div className="w-48 h-48 bg-white border-2 border-slate-100 rounded-xl p-2 shadow-inner">
                                        {/* 使用第三方服务生成二维码图片 */}
                                        <img
                                            src={`https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(qrcodeUrl)}`}
                                            alt="Payment QR Code"
                                            className="w-full h-full"
                                        />
                                    </div>
                                    {/* WeChat logo overlay */}
                                    <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                                        <div className="w-10 h-10 bg-white rounded-lg shadow flex items-center justify-center">
                                            <svg viewBox="0 0 24 24" className="w-6 h-6 text-green-500" fill="currentColor">
                                                <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178A1.17 1.17 0 0 1 4.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178 1.17 1.17 0 0 1-1.162-1.178c0-.651.52-1.18 1.162-1.18zm5.34 2.867c-1.797-.052-3.746.512-5.28 1.786-1.72 1.428-2.687 3.72-1.78 6.22.942 2.453 3.666 4.229 6.884 4.229.826 0 1.622-.12 2.361-.336a.722.722 0 0 1 .598.082l1.584.926a.272.272 0 0 0 .14.047c.134 0 .24-.111.24-.247 0-.06-.023-.12-.038-.177l-.327-1.233a.582.582 0 0 1-.023-.156.49.49 0 0 1 .201-.398C23.024 18.48 24 16.82 24 14.98c0-3.21-2.931-5.837-6.656-6.088V8.89c-.135-.01-.27-.023-.407-.032zm-2.53 3.274c.535 0 .969.44.969.982a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.542.434-.982.97-.982zm4.844 0c.535 0 .969.44.969.982a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.542.434-.982.969-.982z" />
                                            </svg>
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <div className="w-48 h-48 bg-slate-100 rounded-xl flex items-center justify-center">
                                    <QrCode className="w-12 h-12 text-slate-300" />
                                </div>
                            )}

                            {/* Hint */}
                            <p className="mt-4 text-xs text-slate-400 text-center">
                                请使用微信扫描二维码完成支付<br />
                                支付成功后将自动开始下载
                            </p>

                            {/* Polling indicator */}
                            {polling && (
                                <div className="mt-4 flex items-center gap-2 text-xs text-slate-500">
                                    <Loader2 className="w-3 h-3 animate-spin" />
                                    <span>等待支付中...</span>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
