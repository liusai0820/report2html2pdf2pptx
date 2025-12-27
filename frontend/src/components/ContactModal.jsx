import React, { useState, useEffect } from 'react';
import { X, Clock, Shield, CheckCircle, Sparkles, Users, Award, FileText, Presentation, Mail, Copy, Check } from 'lucide-react';

/**
 * 加微信弹窗组件 - 商业化转化核心页面
 * 
 * 运用的心理学与营销学原理：
 * 1. 损失规避 - 已完成的作品，不获取就浪费了
 * 2. 锚定效应 - 原价 vs 现价
 * 3. 社会证明 - 用户数量
 * 4. 稀缺性 - 限时倒计时
 * 5. 便捷性 - 一键复制邮箱，简化流程
 */
export default function ContactModal({
    isOpen,
    onClose,
    documentName = "演示文稿",
    price = 19.9
}) {
    // 倒计时（稀缺性）
    const [countdown, setCountdown] = useState({ minutes: 14, seconds: 59 });
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

    // 复制文档名称
    const handleCopyDocName = () => {
        navigator.clipboard.writeText(documentName);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    if (!isOpen) return null;

    const wechatQrCodeUrl = "/wechat-qrcode.png";

    // 原价锚点（锚定效应）
    const originalPrice = 59;
    const savings = originalPrice - price;
    const discountPercent = Math.round((1 - price / originalPrice) * 100);

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-gradient-to-br from-slate-900/90 to-slate-800/90 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-[400px] overflow-hidden animate-in zoom-in-95 fade-in duration-300">

                {/* 顶部限时横幅 */}
                <div className="bg-gradient-to-r from-violet-600 via-purple-600 to-indigo-600 px-4 py-2.5 flex items-center justify-center gap-3">
                    <Clock className="w-4 h-4 text-white/80" />
                    <span className="text-white text-sm font-medium">限时优惠</span>
                    <div className="flex items-center gap-1">
                        <span className="bg-white/20 text-white font-bold px-2 py-0.5 rounded text-sm tabular-nums">
                            {String(countdown.minutes).padStart(2, '0')}
                        </span>
                        <span className="text-white/70">:</span>
                        <span className="bg-white/20 text-white font-bold px-2 py-0.5 rounded text-sm tabular-nums">
                            {String(countdown.seconds).padStart(2, '0')}
                        </span>
                    </div>
                </div>

                {/* 关闭按钮 */}
                <button
                    onClick={onClose}
                    className="absolute top-14 right-3 p-1.5 bg-slate-100 hover:bg-slate-200 rounded-full transition-colors z-10"
                >
                    <X className="w-4 h-4 text-slate-400" />
                </button>

                {/* 主内容 */}
                <div className="p-5">

                    {/* 标题 */}
                    <div className="text-center mb-4">
                        <div className="inline-flex items-center gap-1.5 bg-green-50 text-green-700 px-3 py-1 rounded-full text-xs font-medium mb-2">
                            <CheckCircle className="w-3.5 h-3.5" />
                            您的演示文稿已生成完成
                        </div>
                        <h2 className="text-lg font-bold text-slate-800">
                            扫码获取高清源文件
                        </h2>
                    </div>

                    {/* 价格 + 权益 */}
                    <div className="bg-gradient-to-r from-orange-50 to-amber-50 rounded-xl p-4 mb-4 border border-orange-100">
                        <div className="flex items-center justify-between">
                            <div>
                                <div className="flex items-baseline gap-2 mb-1">
                                    <span className="text-slate-400 text-sm line-through">¥{originalPrice}</span>
                                    <span className="text-3xl font-black text-orange-600">¥{price}</span>
                                </div>
                                <span className="text-xs bg-orange-500 text-white px-2 py-0.5 rounded-full font-medium">
                                    省 ¥{savings} · {discountPercent}% OFF
                                </span>
                            </div>
                            <div className="text-right space-y-1.5">
                                <div className="flex items-center gap-1.5 text-xs text-slate-600">
                                    <FileText className="w-3.5 h-3.5 text-blue-500" />
                                    <span>高清 PDF</span>
                                </div>
                                <div className="flex items-center gap-1.5 text-xs text-slate-600">
                                    <Presentation className="w-3.5 h-3.5 text-orange-500" />
                                    <span>可编辑 PPTX</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* 二维码 */}
                    <div className="flex justify-center mb-4">
                        <div className="relative">
                            <div className="w-36 h-36 bg-white border-2 border-slate-100 rounded-xl p-1.5 shadow-sm">
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
                                    className="hidden w-full h-full items-center justify-center bg-slate-50 rounded-lg"
                                    style={{ display: 'none' }}
                                >
                                    <span className="text-xs text-slate-400">二维码</span>
                                </div>
                            </div>
                            {/* 微信角标 */}
                            <div className="absolute -bottom-1.5 -right-1.5 w-8 h-8 bg-green-500 rounded-full shadow flex items-center justify-center border-2 border-white">
                                <svg viewBox="0 0 24 24" className="w-4 h-4 text-white" fill="currentColor">
                                    <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348z" />
                                </svg>
                            </div>
                        </div>
                    </div>

                    {/* 操作指引 - 核心转化步骤 */}
                    <div className="bg-slate-50 rounded-xl p-4 mb-4 border border-slate-100">
                        <p className="text-sm text-slate-600 text-center mb-3">
                            添加微信后，发送以下文档名称：
                        </p>
                        <div className="flex items-center gap-2 bg-white rounded-lg border border-slate-200 p-2">
                            <div className="flex-1 text-sm font-medium text-slate-800 truncate px-2">
                                {documentName}
                            </div>
                            <button
                                onClick={handleCopyDocName}
                                className={`flex items-center gap-1 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${copied
                                        ? 'bg-green-100 text-green-700'
                                        : 'bg-violet-600 text-white hover:bg-violet-700'
                                    }`}
                            >
                                {copied ? (
                                    <>
                                        <Check className="w-3 h-3" />
                                        已复制
                                    </>
                                ) : (
                                    <>
                                        <Copy className="w-3 h-3" />
                                        复制
                                    </>
                                )}
                            </button>
                        </div>
                    </div>

                    {/* 社会证明 */}
                    <div className="flex items-center justify-center gap-6 text-xs text-slate-500">
                        <div className="flex items-center gap-1">
                            <Users className="w-3.5 h-3.5 text-blue-500" />
                            <span><strong className="text-slate-700">2,800+</strong> 用户</span>
                        </div>
                        <div className="flex items-center gap-1">
                            <Award className="w-3.5 h-3.5 text-amber-500" />
                            <span><strong className="text-slate-700">4.9</strong> 好评</span>
                        </div>
                        <div className="flex items-center gap-1">
                            <Sparkles className="w-3.5 h-3.5 text-purple-500" />
                            <span>秒发送</span>
                        </div>
                    </div>
                </div>

                {/* 底部信任 */}
                <div className="bg-slate-50 px-5 py-2.5 border-t border-slate-100 flex items-center justify-center gap-4 text-[10px] text-slate-400">
                    <span className="flex items-center gap-1">
                        <Shield className="w-3 h-3" />
                        安全支付
                    </span>
                    <span className="flex items-center gap-1">
                        <Mail className="w-3 h-3" />
                        即时发送
                    </span>
                    <span className="flex items-center gap-1">
                        <CheckCircle className="w-3 h-3" />
                        不满意退款
                    </span>
                </div>
            </div>
        </div>
    );
}
