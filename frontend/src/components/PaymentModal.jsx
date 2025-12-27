import React, { useState, useEffect } from 'react';
import { X, Loader2, Check, ExternalLink, CreditCard } from 'lucide-react';

/**
 * 支付弹窗组件
 * 虎皮椒支付 - 跳转支付页面，轮询支付状态
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
    const [paymentUrl, setPaymentUrl] = useState(null);
    const [orderId, setOrderId] = useState(null);
    const [tradeOrderId, setTradeOrderId] = useState(null);
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
                    setPaymentUrl(data.payment_url);
                    setOrderId(data.order_id);
                    setTradeOrderId(data.trade_order_id);
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
        if (!polling || !tradeOrderId || !orderId) return;

        const checkPayment = async () => {
            try {
                const resp = await fetch('/api/payment/check', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        trade_order_id: tradeOrderId,
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
    }, [polling, tradeOrderId, orderId, onPaymentSuccess]);

    // 关闭时重置状态
    const handleClose = () => {
        setPolling(false);
        setPaymentUrl(null);
        setOrderId(null);
        setTradeOrderId(null);
        setIsPaid(false);
        setError(null);
        onClose?.();
    };

    // 跳转支付页面
    const handlePayNow = () => {
        if (paymentUrl) {
            window.open(paymentUrl, '_blank');
        }
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
                            <h3 className="font-semibold text-slate-800">在线支付</h3>
                            <p className="text-xs text-slate-500">支持微信、支付宝</p>
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

                            {/* Pay Button */}
                            {paymentUrl ? (
                                <button
                                    onClick={handlePayNow}
                                    className="w-full py-3 px-6 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-medium rounded-xl shadow-lg shadow-green-500/30 transition-all hover:-translate-y-0.5 flex items-center justify-center gap-2"
                                >
                                    <span>立即支付</span>
                                    <ExternalLink className="w-4 h-4" />
                                </button>
                            ) : (
                                <div className="w-full py-3 px-6 bg-slate-100 text-slate-400 font-medium rounded-xl text-center">
                                    准备中...
                                </div>
                            )}

                            {/* Hint */}
                            <p className="mt-4 text-xs text-slate-400 text-center">
                                点击按钮将跳转至支付页面<br />
                                支付成功后请返回此页等待自动下载
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
