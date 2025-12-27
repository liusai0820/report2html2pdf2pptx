import React, { useState, useEffect } from 'react';
import { X, Gift, Zap, Clock, Shield, CheckCircle, Sparkles } from 'lucide-react';

/**
 * 加微信弹窗组件 - 商业化关键转化页面
 * 运用营销心理学：稀缺性、社会证明、价值锚定、紧迫感
 */
export default function ContactModal({
    isOpen,
    onClose,
    documentName = "演示文稿",
    price = 9.9
}) {
    // 倒计时效果（制造紧迫感）
    const [countdown, setCountdown] = useState({ minutes: 14, seconds: 59 });

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

    if (!isOpen) return null;

    // TODO: 替换为真实的微信二维码图片 URL
    const wechatQrCodeUrl = "/wechat-qrcode.png";

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            {/* Backdrop with blur */}
            <div
                className="absolute inset-0 bg-black/70 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-[420px] overflow-hidden animate-in zoom-in-95 fade-in duration-300">

                {/* 顶部促销横幅 - 紧迫感 */}
                <div className="bg-gradient-to-r from-red-500 via-orange-500 to-amber-500 px-4 py-2 flex items-center justify-center gap-2">
                    <Clock className="w-4 h-4 text-white animate-pulse" />
                    <span className="text-white text-sm font-bold">
                        限时特惠倒计时：
                        <span className="bg-white/20 px-1.5 py-0.5 rounded mx-1 tabular-nums">
                            {String(countdown.minutes).padStart(2, '0')}
                        </span>
                        :
                        <span className="bg-white/20 px-1.5 py-0.5 rounded mx-1 tabular-nums">
                            {String(countdown.seconds).padStart(2, '0')}
                        </span>
                    </span>
                </div>

                {/* 关闭按钮 */}
                <button
                    onClick={onClose}
                    className="absolute top-12 right-3 p-1.5 bg-black/10 hover:bg-black/20 rounded-full transition-colors z-10"
                >
                    <X className="w-4 h-4 text-slate-500" />
                </button>

                {/* 主内容区 */}
                <div className="p-6">
                    {/* 价值锚定 - 划线价 vs 现价 */}
                    <div className="text-center mb-5">
                        <div className="inline-flex items-center gap-2 bg-amber-50 px-3 py-1 rounded-full mb-3">
                            <Sparkles className="w-4 h-4 text-amber-500" />
                            <span className="text-amber-700 text-xs font-semibold">新用户专享福利</span>
                        </div>
                        <h2 className="text-xl font-bold text-slate-800 mb-2">
                            获取您的专属 AI 演示文稿
                        </h2>
                        <div className="flex items-baseline justify-center gap-2">
                            <span className="text-slate-400 text-lg line-through">¥39.9</span>
                            <span className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-red-500 to-orange-500">
                                ¥{price}
                            </span>
                            <span className="text-slate-500 text-sm">/次</span>
                        </div>
                        <p className="text-green-600 text-xs font-medium mt-1">
                            比市场价节省 75%！
                        </p>
                    </div>

                    {/* 二维码区域 */}
                    <div className="flex justify-center mb-5">
                        <div className="relative group">
                            <div className="absolute inset-0 bg-gradient-to-r from-green-400 to-emerald-500 rounded-2xl blur-lg opacity-30 group-hover:opacity-50 transition-opacity"></div>
                            <div className="relative w-44 h-44 bg-white border-2 border-green-100 rounded-2xl p-2 shadow-lg">
                                <img
                                    src={wechatQrCodeUrl}
                                    alt="微信二维码"
                                    className="w-full h-full object-contain rounded-lg"
                                    onError={(e) => {
                                        e.target.style.display = 'none';
                                        e.target.nextSibling.style.display = 'flex';
                                    }}
                                />
                                <div
                                    className="hidden w-full h-full items-center justify-center bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg"
                                    style={{ display: 'none' }}
                                >
                                    <div className="text-center">
                                        <div className="w-12 h-12 mx-auto mb-2 bg-green-100 rounded-full flex items-center justify-center">
                                            <svg viewBox="0 0 24 24" className="w-7 h-7 text-green-500" fill="currentColor">
                                                <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348z" />
                                            </svg>
                                        </div>
                                        <p className="text-xs text-slate-400">扫码添加微信</p>
                                    </div>
                                </div>
                            </div>
                            {/* 微信 Logo 角标 */}
                            <div className="absolute -bottom-2 -right-2 w-10 h-10 bg-green-500 rounded-full shadow-lg flex items-center justify-center border-2 border-white">
                                <svg viewBox="0 0 24 24" className="w-5 h-5 text-white" fill="currentColor">
                                    <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348z" />
                                </svg>
                            </div>
                        </div>
                    </div>

                    {/* 行动指引 */}
                    <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-3 mb-4 border border-green-100">
                        <p className="text-center text-sm text-slate-700">
                            微信扫码添加后，发送 "<span className="font-bold text-green-600">领取</span>" 即可获取
                        </p>
                    </div>

                    {/* 信任徽章 - 社会证明 */}
                    <div className="grid grid-cols-3 gap-2 mb-4">
                        <div className="flex flex-col items-center p-2 bg-slate-50 rounded-lg">
                            <Zap className="w-4 h-4 text-amber-500 mb-1" />
                            <span className="text-[10px] text-slate-600 text-center">即刻获取</span>
                        </div>
                        <div className="flex flex-col items-center p-2 bg-slate-50 rounded-lg">
                            <Shield className="w-4 h-4 text-blue-500 mb-1" />
                            <span className="text-[10px] text-slate-600 text-center">安全支付</span>
                        </div>
                        <div className="flex flex-col items-center p-2 bg-slate-50 rounded-lg">
                            <CheckCircle className="w-4 h-4 text-green-500 mb-1" />
                            <span className="text-[10px] text-slate-600 text-center">已服务 2000+</span>
                        </div>
                    </div>

                    {/* 额外价值 */}
                    <div className="space-y-2">
                        <div className="flex items-center gap-2 text-sm">
                            <Gift className="w-4 h-4 text-pink-500 flex-shrink-0" />
                            <span className="text-slate-600">
                                <strong className="text-slate-800">赠送：</strong>加微信即送 3 次免费生成额度
                            </span>
                        </div>
                        <div className="flex items-center gap-2 text-sm">
                            <Sparkles className="w-4 h-4 text-purple-500 flex-shrink-0" />
                            <span className="text-slate-600">
                                <strong className="text-slate-800">专属：</strong>VIP 会员 5 折优惠通道
                            </span>
                        </div>
                    </div>
                </div>

                {/* 底部信任声明 */}
                <div className="bg-slate-50 px-6 py-3 border-t border-slate-100">
                    <p className="text-[10px] text-slate-400 text-center">
                        🔒 您的隐私受到保护 · 不满意随时退款 · 24小时在线服务
                    </p>
                </div>
            </div>
        </div>
    );
}
