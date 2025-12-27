import React, { useState, useEffect } from 'react';
import { X, Copy, Check, ShieldCheck, Zap, Crown } from 'lucide-react';

/**
 * 加微信弹窗组件 - 高端商务版
 * 
 * 设计理念：Premium / Minimalist / Professional
 * 核心元素：黑金配色、订单号机制、极简布局
 */
export default function ContactModal({
    isOpen,
    onClose,
    documentName,
    price = 19.9,
    generationId
}) {
    // 生成伪订单号：取 UUID 前8位转大写
    const orderNo = generationId
        ? `ORDER-${generationId.slice(0, 8).toUpperCase()}`
        : `ORDER-${Math.random().toString(36).substring(2, 10).toUpperCase()}`;

    const [countdown, setCountdown] = useState({ minutes: 9, seconds: 59 });
    const [copied, setCopied] = useState(false);

    useEffect(() => {
        if (!isOpen) return;

        const timer = setInterval(() => {
            setCountdown(prev => {
                if (prev.seconds > 0) {
                    return { ...prev, seconds: prev.seconds - 1 };
                } else if (prev.minutes > 0) {
                    return { minutes: prev.minutes - 1, seconds: 59 };
                }
                return prev;
            });
        }, 1000);

        return () => clearInterval(timer);
    }, [isOpen]);

    const handleCopyOrderNo = () => {
        navigator.clipboard.writeText(orderNo);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    if (!isOpen) return null;

    const wechatQrCodeUrl = "/wechat-qrcode.png";
    const originalPrice = 59; // 锚点价格

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            {/* 沉浸式深色背景 */}
            <div
                className="absolute inset-0 bg-slate-900/40 backdrop-blur-md transition-opacity"
                onClick={onClose}
            />

            {/* 卡片主体 */}
            <div className="relative bg-white w-full max-w-[380px] rounded-[24px] shadow-2xl overflow-hidden animate-in zoom-in-95 fade-in duration-300 ring-1 ring-black/5">

                {/* 顶部金色进度条/倒计时 */}
                <div className="bg-slate-900 px-6 py-3 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Crown className="w-4 h-4 text-amber-400" />
                        <span className="text-amber-50 text-xs font-medium tracking-wide">PREMIUM ACCESS</span>
                    </div>
                    <div className="flex items-center gap-1.5 font-mono text-xs text-amber-400/90">
                        <span>{String(countdown.minutes).padStart(2, '0')}:{String(countdown.seconds).padStart(2, '0')}</span>
                    </div>
                </div>

                {/* 关闭按钮 */}
                <button
                    onClick={onClose}
                    className="absolute top-14 right-4 p-2 text-slate-400 hover:text-slate-600 transition-colors z-10"
                >
                    <X className="w-5 h-5" />
                </button>

                <div className="px-8 pt-8 pb-6">
                    {/* 标题区 */}
                    <div className="text-center mb-8">
                        <h2 className="text-xl font-bold text-slate-900 mb-2">获取完整演示文稿</h2>
                        <p className="text-sm text-slate-500">解锁 PDF 高清版 + PPTX 可编辑源码</p>
                    </div>

                    {/* 价格展示卡片 */}
                    <div className="bg-slate-50 rounded-2xl p-5 mb-8 border border-slate-100 relative group overflow-hidden">
                        {/* 光效装饰 */}
                        <div className="absolute top-0 right-0 -mr-4 -mt-4 w-20 h-20 bg-amber-100/50 rounded-full blur-2xl group-hover:bg-amber-200/50 transition-colors"></div>

                        <div className="flex items-baseline justify-center gap-3 relative z-10">
                            <span className="text-slate-400 text-sm line-through decorating-slate-900">¥{originalPrice}</span>
                            <div className="flex items-baseline">
                                <span className="text-base font-semibold text-slate-900 mr-0.5">¥</span>
                                <span className="text-4xl font-bold text-slate-900 tracking-tight">{price}</span>
                            </div>
                        </div>
                        <div className="text-center mt-2">
                            <span className="inline-block px-2.5 py-0.5 bg-slate-900 text-amber-400 text-[10px] font-bold uppercase tracking-wider rounded-full">
                                Limited Offer
                            </span>
                        </div>
                    </div>

                    {/* 二维码区域 */}
                    <div className="flex justify-center mb-8">
                        <div className="p-1.5 rounded-xl border border-slate-100 shadow-sm bg-white">
                            <img
                                src={wechatQrCodeUrl}
                                alt="微信二维码"
                                className="w-32 h-32 object-contain rounded-lg"
                                onError={(e) => {
                                    e.target.style.display = 'none';
                                    e.target.nextSibling.style.display = 'flex';
                                }}
                            />
                            {/* Fallback */}
                            <div
                                className="hidden w-32 h-32 items-center justify-center bg-slate-50 rounded-lg"
                                style={{ display: 'none' }}
                            >
                                <span className="text-xs text-slate-400">二维码加载失败</span>
                            </div>
                        </div>
                    </div>

                    {/* 核心转化动作：复制订单号 */}
                    <div className="space-y-3">
                        <p className="text-center text-xs text-slate-500 font-medium">
                            添加微信，发送以下订单号立即获取
                        </p>

                        <div
                            onClick={handleCopyOrderNo}
                            className="flex items-center justify-between bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-xl px-4 py-3 cursor-pointer group transition-all active:scale-[0.98]"
                        >
                            <div className="flex flex-col">
                                <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Order Number</span>
                                <span className="text-sm font-mono font-medium text-slate-700 group-hover:text-slate-900">
                                    {orderNo}
                                </span>
                            </div>
                            <div className={`p-2 rounded-lg transition-colors ${copied ? 'bg-green-100 text-green-600' : 'bg-white text-slate-400 group-hover:text-slate-600 shadow-sm'}`}>
                                {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                            </div>
                        </div>
                    </div>
                </div>

                {/* 底部信任栏 */}
                <div className="bg-slate-50/50 px-6 py-4 border-t border-slate-100/50 flex justify-between items-center text-[10px] text-slate-400">
                    <div className="flex items-center gap-1.5">
                        <ShieldCheck className="w-3 h-3" />
                        <span>Secure Payment</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                        <Zap className="w-3 h-3" />
                        <span>Instant Delivery</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
