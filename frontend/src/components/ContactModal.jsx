import React from 'react';
import { X, Gift, MessageCircle, Star, Sparkles } from 'lucide-react';

/**
 * 加微信弹窗组件
 * 展示微信二维码，引导用户添加客服微信获取下载
 */
export default function ContactModal({
    isOpen,
    onClose,
    documentName = "演示文稿"
}) {
    if (!isOpen) return null;

    // TODO: 替换为真实的微信二维码图片 URL
    const wechatQrCodeUrl = "/wechat-qrcode.png";
    const wechatId = "YOUR_WECHAT_ID"; // TODO: 替换为你的微信号

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="relative bg-white rounded-2xl shadow-2xl w-[400px] overflow-hidden animate-in zoom-in-95 fade-in duration-200">
                {/* Header with gradient */}
                <div className="relative bg-gradient-to-br from-green-400 via-green-500 to-emerald-600 px-6 py-5">
                    {/* Decorative elements */}
                    <div className="absolute top-2 right-2 opacity-20">
                        <Sparkles className="w-24 h-24 text-white" />
                    </div>

                    <button
                        onClick={onClose}
                        className="absolute top-3 right-3 p-1.5 bg-white/20 hover:bg-white/30 rounded-lg transition-colors"
                    >
                        <X className="w-4 h-4 text-white" />
                    </button>

                    <div className="relative z-10">
                        <div className="flex items-center gap-2 mb-2">
                            <Gift className="w-5 h-5 text-white" />
                            <span className="text-white/90 text-sm font-medium">限时福利</span>
                        </div>
                        <h3 className="text-xl font-bold text-white">添加微信，免费下载</h3>
                        <p className="text-white/80 text-sm mt-1">还可解锁专属优惠与 VIP 特权</p>
                    </div>
                </div>

                {/* Content */}
                <div className="p-6">
                    {/* QR Code */}
                    <div className="flex justify-center mb-5">
                        <div className="relative">
                            <div className="w-44 h-44 bg-slate-50 border-2 border-slate-100 rounded-xl p-2 shadow-inner">
                                <img
                                    src={wechatQrCodeUrl}
                                    alt="微信二维码"
                                    className="w-full h-full object-contain"
                                    onError={(e) => {
                                        // 如果图片加载失败，显示占位符
                                        e.target.style.display = 'none';
                                        e.target.nextSibling.style.display = 'flex';
                                    }}
                                />
                                {/* Placeholder when image fails */}
                                <div
                                    className="hidden w-full h-full items-center justify-center bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg"
                                    style={{ display: 'none' }}
                                >
                                    <div className="text-center">
                                        <MessageCircle className="w-12 h-12 text-green-400 mx-auto mb-2" />
                                        <p className="text-xs text-slate-400">二维码加载中...</p>
                                    </div>
                                </div>
                            </div>
                            {/* WeChat logo badge */}
                            <div className="absolute -bottom-2 -right-2 w-10 h-10 bg-white rounded-full shadow-lg flex items-center justify-center">
                                <svg viewBox="0 0 24 24" className="w-6 h-6 text-green-500" fill="currentColor">
                                    <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178A1.17 1.17 0 0 1 4.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178 1.17 1.17 0 0 1-1.162-1.178c0-.651.52-1.18 1.162-1.18zm5.34 2.867c-1.797-.052-3.746.512-5.28 1.786-1.72 1.428-2.687 3.72-1.78 6.22.942 2.453 3.666 4.229 6.884 4.229.826 0 1.622-.12 2.361-.336a.722.722 0 0 1 .598.082l1.584.926a.272.272 0 0 0 .14.047c.134 0 .24-.111.24-.247 0-.06-.023-.12-.038-.177l-.327-1.233a.582.582 0 0 1-.023-.156.49.49 0 0 1 .201-.398C23.024 18.48 24 16.82 24 14.98c0-3.21-2.931-5.837-6.656-6.088V8.89c-.135-.01-.27-.023-.407-.032zm-2.53 3.274c.535 0 .969.44.969.982a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.542.434-.982.97-.982zm4.844 0c.535 0 .969.44.969.982a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.542.434-.982.969-.982z" />
                                </svg>
                            </div>
                        </div>
                    </div>

                    {/* WeChat ID */}
                    <div className="text-center mb-5">
                        <p className="text-xs text-slate-400 mb-1">微信号</p>
                        <p className="text-sm font-medium text-slate-700 bg-slate-50 px-3 py-1.5 rounded-lg inline-block">
                            {wechatId}
                        </p>
                    </div>

                    {/* Benefits */}
                    <div className="space-y-2.5">
                        <div className="flex items-center gap-3 text-sm">
                            <div className="w-6 h-6 rounded-full bg-green-50 flex items-center justify-center flex-shrink-0">
                                <Gift className="w-3.5 h-3.5 text-green-500" />
                            </div>
                            <span className="text-slate-600">免费获取本次生成的 <strong className="text-slate-800">PDF</strong> 文件</span>
                        </div>
                        <div className="flex items-center gap-3 text-sm">
                            <div className="w-6 h-6 rounded-full bg-amber-50 flex items-center justify-center flex-shrink-0">
                                <Star className="w-3.5 h-3.5 text-amber-500" />
                            </div>
                            <span className="text-slate-600">解锁 <strong className="text-slate-800">VIP 会员</strong> 专属优惠价</span>
                        </div>
                        <div className="flex items-center gap-3 text-sm">
                            <div className="w-6 h-6 rounded-full bg-blue-50 flex items-center justify-center flex-shrink-0">
                                <Sparkles className="w-3.5 h-3.5 text-blue-500" />
                            </div>
                            <span className="text-slate-600">优先体验 <strong className="text-slate-800">新功能</strong> 与定制服务</span>
                        </div>
                    </div>

                    {/* Hint */}
                    <p className="mt-5 text-xs text-slate-400 text-center">
                        扫码添加后，请发送 "<strong className="text-green-600">下载</strong>" 获取文件
                    </p>
                </div>
            </div>
        </div>
    );
}
