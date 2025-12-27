import React, { useState, useEffect } from 'react';
import { X, Copy, Check, ShieldCheck, Zap, Crown, Palette, Briefcase, FileSignature, ChevronRight } from 'lucide-react';

/**
 * 加微信弹窗组件 - 高端商务版 Pro
 * 
 * 升级内容：
 * 1. 完善订单号逻辑：复制内容包含 ID + 文件名（双重保险）
 * 2. 增加高价值服务引导：定制开发、模板定制等
 * 3. 价格修正为 19.9
 */
export default function ContactModal({
    isOpen,
    onClose,
    documentName,
    price = 19.9,
    generationId
}) {
    // 订单号逻辑
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

    // 复制完整信息
    const handleCopyInfo = () => {
        const textToCopy = `订单号：${orderNo}\n文档：${documentName}`;
        navigator.clipboard.writeText(textToCopy);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    if (!isOpen) return null;

    const wechatQrCodeUrl = "/wechat-qrcode.png";
    const originalPrice = 59;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            <div
                className="absolute inset-0 bg-slate-900/60 backdrop-blur-md transition-opacity"
                onClick={onClose}
            />

            {/* 主卡片 */}
            <div className="relative bg-white w-full max-w-[400px] rounded-[24px] shadow-2xl overflow-hidden animate-in zoom-in-95 fade-in duration-300 ring-1 ring-black/5 flex flex-col max-h-[90vh]">

                {/* Header */}
                <div className="bg-slate-900 px-6 py-4 flex items-center justify-between flex-shrink-0">
                    <div className="flex items-center gap-2">
                        <Crown className="w-4 h-4 text-amber-400" />
                        <span className="text-amber-50 text-xs font-bold tracking-widest">PREMIUM MEMBER</span>
                    </div>
                    <div className="flex items-center gap-1.5 font-mono text-xs text-amber-400">
                        <span>{String(countdown.minutes).padStart(2, '0')}:{String(countdown.seconds).padStart(2, '0')}</span>
                    </div>
                </div>

                <button
                    onClick={onClose}
                    className="absolute top-3 right-3 p-2 text-slate-400 hover:text-white transition-colors z-20"
                >
                    <X className="w-5 h-5" />
                </button>

                <div className="px-6 py-6 overflow-y-auto custom-scrollbar">

                    {/* 价格与核心价值 */}
                    <div className="text-center mb-6">
                        <h2 className="text-xl font-bold text-slate-900 mb-1">获取完整源文件</h2>
                        <div className="flex items-center justify-center gap-2 text-xs text-slate-500 mb-4">
                            <span>PDF 高清导出</span>
                            <span className="w-1 h-1 rounded-full bg-slate-300"></span>
                            <span>PPTX 可编辑源码</span>
                        </div>

                        <div className="relative inline-flex flex-col items-center bg-slate-50 border border-slate-100 rounded-2xl p-4 w-full">
                            <div className="flex items-baseline gap-2">
                                <span className="text-slate-400 text-sm line-through">¥{originalPrice}</span>
                                <span className="text-4xl font-bold text-slate-900 tracking-tight">¥{price}</span>
                            </div>
                            <div className="mt-2 text-[10px] text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full font-medium border border-amber-100">
                                限时特惠 · 极速交付
                            </div>
                        </div>
                    </div>

                    {/* 扫码与复制区域 */}
                    <div className="flex gap-4 mb-6">
                        {/* 左侧：二维码 */}
                        <div className="flex-shrink-0 w-32 h-32 bg-white border border-slate-100 rounded-xl p-1.5 shadow-sm">
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
                                className="hidden w-full h-full items-center justify-center bg-slate-50 rounded-lg text-center p-2"
                                style={{ display: 'none' }}
                            >
                                <span className="text-[10px] text-slate-400">二维码加载失败</span>
                            </div>
                        </div>

                        {/* 右侧：操作指引 */}
                        <div className="flex-1 flex flex-col justify-center space-y-3">
                            <div>
                                <h3 className="text-sm font-bold text-slate-900 mb-1">第 1 步</h3>
                                <p className="text-xs text-slate-500">扫码添加客服微信</p>
                            </div>
                            <div>
                                <h3 className="text-sm font-bold text-slate-900 mb-1">第 2 步</h3>
                                <p className="text-xs text-slate-500 mb-2">点击复制订单信息并发送</p>
                                <button
                                    onClick={handleCopyInfo}
                                    className={`w-full flex items-center justify-center gap-1.5 py-1.5 rounded-lg text-xs font-medium transition-all ${copied
                                            ? 'bg-green-100 text-green-700 border border-green-200'
                                            : 'bg-slate-900 text-white hover:bg-slate-800 shadow-md hover:shadow-lg'
                                        }`}
                                >
                                    {copied ? (
                                        <>
                                            <Check className="w-3.5 h-3.5" />
                                            已复制
                                        </>
                                    ) : (
                                        <>
                                            <Copy className="w-3.5 h-3.5" />
                                            复制订单号
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* 文档名称确认 */}
                    <div className="bg-slate-50 rounded-lg px-3 py-2 mb-6 border border-slate-100">
                        <div className="flex justify-between items-center text-[10px] text-slate-500 mb-1">
                            <span>当前文档</span>
                            <span className="font-mono text-slate-400">{orderNo}</span>
                        </div>
                        <div className="text-xs font-medium text-slate-700 truncate" title={documentName}>
                            {documentName}
                        </div>
                    </div>

                    {/* 高级定制服务引导 */}
                    <div className="border-t border-slate-100 pt-5">
                        <div className="flex items-center justify-between mb-3">
                            <h3 className="text-xs font-bold text-slate-900">更多企业级服务</h3>
                            <span className="text-[10px] text-slate-400">联系客服咨询</span>
                        </div>
                        <div className="grid grid-cols-1 gap-2">
                            <div className="flex items-start gap-3 p-2 rounded-lg hover:bg-slate-50 transition-colors group cursor-default">
                                <div className="p-1.5 bg-blue-50 text-blue-600 rounded-md group-hover:bg-blue-100 transition-colors">
                                    <Palette className="w-3.5 h-3.5" />
                                </div>
                                <div>
                                    <div className="text-xs font-medium text-slate-700">PPT 深度美化定制</div>
                                    <div className="text-[10px] text-slate-400">专业设计师 1v1 排版优化</div>
                                </div>
                            </div>
                            <div className="flex items-start gap-3 p-2 rounded-lg hover:bg-slate-50 transition-colors group cursor-default">
                                <div className="p-1.5 bg-purple-50 text-purple-600 rounded-md group-hover:bg-purple-100 transition-colors">
                                    <Briefcase className="w-3.5 h-3.5" />
                                </div>
                                <div>
                                    <div className="text-xs font-medium text-slate-700">企业模版开发</div>
                                    <div className="text-[10px] text-slate-400">品牌 VI 植入与专属母版定制</div>
                                </div>
                            </div>
                            <div className="flex items-start gap-3 p-2 rounded-lg hover:bg-slate-50 transition-colors group cursor-default">
                                <div className="p-1.5 bg-emerald-50 text-emerald-600 rounded-md group-hover:bg-emerald-100 transition-colors">
                                    <FileSignature className="w-3.5 h-3.5" />
                                </div>
                                <div>
                                    <div className="text-xs font-medium text-slate-700">内容润色与撰写</div>
                                    <div className="text-[10px] text-slate-400">行业专家提供内容优化服务</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
