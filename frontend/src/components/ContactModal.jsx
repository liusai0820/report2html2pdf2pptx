import React, { useState, useEffect } from 'react';
import { X, Copy, Check, Crown, Palette, Briefcase, FileSignature } from 'lucide-react';

/**
 * 加微信弹窗组件 - 高端商务版 Pro (Final)
 * 
 * 优化点：
 * 1. 彻底移除订单号 (Order Number)，解决 ID 不一致问题
 * 2. 简化流程：直接复制文档名称
 * 3. 复制内容优化：更自然的对话口吻
 * 4. 保持高端黑金设计
 */
export default function ContactModal({
    isOpen,
    onClose,
    documentName,
    price = 19.9
}) {
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

    // 简化复制逻辑：只复制文档名称
    const handleCopyInfo = () => {
        const textToCopy = `你好，我想获取文档：${documentName}`;
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

                {/* Header - 黑金风格 */}
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
                            <span>PPTX 可编辑版</span>
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

                    {/* 扫码与操作指引 */}
                    <div className="bg-slate-50/50 rounded-xl p-4 border border-slate-100/50 mb-6">
                        <div className="flex gap-4">
                            {/* 左侧：二维码 */}
                            <div className="flex-shrink-0 w-28 h-28 bg-white border border-slate-100 rounded-xl p-1.5 shadow-sm">
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

                            {/* 右侧：步骤指引 */}
                            <div className="flex-1 flex flex-col justify-center space-y-3">
                                <div className="space-y-1">
                                    <div className="flex items-center gap-1.5">
                                        <span className="flex items-center justify-center w-4 h-4 rounded-full bg-slate-900 text-white text-[10px] font-bold">1</span>
                                        <h3 className="text-xs font-bold text-slate-900">扫码添加客服</h3>
                                    </div>
                                    <p className="text-[10px] text-slate-500 pl-5.5">长按识别或截图扫码</p>
                                </div>
                                <div className="space-y-1">
                                    <div className="flex items-center gap-1.5">
                                        <span className="flex items-center justify-center w-4 h-4 rounded-full bg-slate-900 text-white text-[10px] font-bold">2</span>
                                        <h3 className="text-xs font-bold text-slate-900">发送文档名称</h3>
                                    </div>
                                    <p className="text-[10px] text-slate-500 pl-5.5">直接发送即刻获取</p>
                                </div>
                            </div>
                        </div>

                        {/* 复制按钮 */}
                        <div className="mt-4">
                            <button
                                onClick={handleCopyInfo}
                                className={`w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-xs font-medium transition-all ${copied
                                        ? 'bg-green-100 text-green-700 border border-green-200'
                                        : 'bg-slate-900 text-white hover:bg-slate-800 shadow-lg hover:shadow-xl hover:-translate-y-0.5'
                                    }`}
                            >
                                {copied ? (
                                    <>
                                        <Check className="w-4 h-4" />
                                        已复制文档名
                                    </>
                                ) : (
                                    <>
                                        <Copy className="w-4 h-4" />
                                        一键复制文档名称
                                    </>
                                )}
                            </button>
                        </div>
                    </div>

                    {/* 当前文档信息 */}
                    <div className="text-center mb-6 px-2">
                        <p className="text-[10px] text-slate-400 mb-1">当前文档</p>
                        <p className="text-xs font-medium text-slate-700 truncate select-all">{documentName}</p>
                    </div>

                    {/* 高级定制服务引导 - 底部附加价值 */}
                    <div className="border-t border-slate-100 pt-5">
                        <div className="flex items-center justify-between mb-3">
                            <h3 className="text-xs font-bold text-slate-900">更多企业级服务</h3>
                            <span className="text-[10px] text-slate-400 bg-slate-50 px-2 py-0.5 rounded-full">联系客服咨询</span>
                        </div>
                        <div className="grid grid-cols-1 gap-2">
                            <div className="flex items-start gap-3 p-2.5 rounded-xl bg-slate-50/50 hover:bg-slate-50 border border-transparent hover:border-slate-100 transition-all cursor-default group">
                                <div className="p-1.5 bg-white text-blue-600 rounded-lg shadow-sm group-hover:bg-blue-50 transition-colors">
                                    <Palette className="w-3.5 h-3.5" />
                                </div>
                                <div>
                                    <div className="text-xs font-medium text-slate-800">PPT 深度美化定制</div>
                                    <div className="text-[10px] text-slate-400 mt-0.5">专业设计师美化排版，提升质感</div>
                                </div>
                            </div>
                            <div className="flex items-start gap-3 p-2.5 rounded-xl bg-slate-50/50 hover:bg-slate-50 border border-transparent hover:border-slate-100 transition-all cursor-default group">
                                <div className="p-1.5 bg-white text-purple-600 rounded-lg shadow-sm group-hover:bg-purple-50 transition-colors">
                                    <Briefcase className="w-3.5 h-3.5" />
                                </div>
                                <div>
                                    <div className="text-xs font-medium text-slate-800">企业模版开发</div>
                                    <div className="text-[10px] text-slate-400 mt-0.5">品牌专属母版定制，规范视觉</div>
                                </div>
                            </div>
                            <div className="flex items-start gap-3 p-2.5 rounded-xl bg-slate-50/50 hover:bg-slate-50 border border-transparent hover:border-slate-100 transition-all cursor-default group">
                                <div className="p-1.5 bg-white text-emerald-600 rounded-lg shadow-sm group-hover:bg-emerald-50 transition-colors">
                                    <FileSignature className="w-3.5 h-3.5" />
                                </div>
                                <div>
                                    <div className="text-xs font-medium text-slate-800">内容润色与撰写</div>
                                    <div className="text-[10px] text-slate-400 mt-0.5">行业专家优化文案，逻辑更清晰</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
