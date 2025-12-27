import React, { useState, useEffect } from 'react';
import { X, Gift, Zap, Clock, Shield, CheckCircle, Sparkles, TrendingUp, Users, Award, FileText, Presentation } from 'lucide-react';

/**
 * 加微信弹窗组件 - 商业化转化核心页面
 * 
 * 运用的心理学与营销学原理：
 * 1. 损失规避 (Loss Aversion) - 强调错过优惠的损失
 * 2. 锚定效应 (Anchoring) - 先展示高价锚点
 * 3. 社会证明 (Social Proof) - 展示用户数量和好评
 * 4. 稀缺性 (Scarcity) - 限时倒计时
 * 5. 互惠原则 (Reciprocity) - 已免费预览，付费获取完整版
 * 6. 沉没成本 (Sunk Cost) - 已投入时间等待生成
 * 7. 价值堆叠 (Value Stacking) - 展示包含的多项权益
 */
export default function ContactModal({
    isOpen,
    onClose,
    documentName = "演示文稿",
    price = 19.9
}) {
    // 倒计时效果（稀缺性原则）
    const [countdown, setCountdown] = useState({ minutes: 9, seconds: 59 });

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

    const wechatQrCodeUrl = "/wechat-qrcode.png";

    // 原价锚点（锚定效应：原价越高，现价越有吸引力）
    const originalPrice = 99;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/80 backdrop-blur-md"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="relative bg-white rounded-3xl shadow-2xl w-full max-w-[440px] overflow-hidden animate-in zoom-in-95 fade-in duration-300">

                {/* 顶部紧迫感横幅 */}
                <div className="bg-gradient-to-r from-red-500 via-rose-500 to-pink-500 px-4 py-2.5 flex items-center justify-center gap-2">
                    <div className="flex items-center gap-1.5 text-white">
                        <Clock className="w-4 h-4 animate-pulse" />
                        <span className="text-sm font-medium">限时特惠</span>
                    </div>
                    <div className="flex items-center gap-1 text-white font-bold">
                        <span className="bg-white/25 px-2 py-0.5 rounded text-sm tabular-nums min-w-[28px] text-center">
                            {String(countdown.minutes).padStart(2, '0')}
                        </span>
                        <span className="text-xs">:</span>
                        <span className="bg-white/25 px-2 py-0.5 rounded text-sm tabular-nums min-w-[28px] text-center">
                            {String(countdown.seconds).padStart(2, '0')}
                        </span>
                    </div>
                    <span className="text-white/90 text-xs">后恢复原价</span>
                </div>

                {/* 关闭按钮 */}
                <button
                    onClick={onClose}
                    className="absolute top-14 right-4 p-1.5 bg-slate-100 hover:bg-slate-200 rounded-full transition-colors z-10"
                >
                    <X className="w-4 h-4 text-slate-500" />
                </button>

                {/* 主内容区 */}
                <div className="p-6 pt-5">

                    {/* 标题区 - 强调已完成的工作（沉没成本） */}
                    <div className="text-center mb-4">
                        <div className="inline-flex items-center gap-1.5 bg-gradient-to-r from-emerald-50 to-teal-50 px-3 py-1 rounded-full mb-3 border border-emerald-100">
                            <CheckCircle className="w-3.5 h-3.5 text-emerald-500" />
                            <span className="text-emerald-700 text-xs font-medium">AI 已为您精心制作完成</span>
                        </div>
                        <h2 className="text-xl font-bold text-slate-800 mb-1">
                            获取您的专属演示文稿
                        </h2>
                        <p className="text-slate-500 text-sm">
                            高质量 PDF + 可编辑 PPTX 双格式
                        </p>
                    </div>

                    {/* 价格区 - 锚定效应 + 价值对比 */}
                    <div className="bg-gradient-to-br from-slate-50 to-slate-100 rounded-2xl p-4 mb-4 border border-slate-200">
                        <div className="flex items-center justify-between">
                            <div>
                                <div className="flex items-baseline gap-2">
                                    <span className="text-slate-400 text-base line-through">¥{originalPrice}</span>
                                    <span className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-rose-500 to-orange-500">
                                        ¥{price}
                                    </span>
                                </div>
                                <div className="flex items-center gap-2 mt-1">
                                    <span className="text-xs text-white bg-rose-500 px-1.5 py-0.5 rounded font-medium">
                                        省 ¥{(originalPrice - price).toFixed(0)}
                                    </span>
                                    <span className="text-xs text-slate-500">
                                        相当于 {Math.round((1 - price / originalPrice) * 100)}% OFF
                                    </span>
                                </div>
                            </div>
                            {/* 权益清单 */}
                            <div className="text-right space-y-1">
                                <div className="flex items-center gap-1.5 text-xs text-slate-600">
                                    <FileText className="w-3.5 h-3.5 text-blue-500" />
                                    <span>PDF 高清版</span>
                                </div>
                                <div className="flex items-center gap-1.5 text-xs text-slate-600">
                                    <Presentation className="w-3.5 h-3.5 text-orange-500" />
                                    <span>PPTX 可编辑</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* 二维码区域 */}
                    <div className="flex justify-center mb-4">
                        <div className="relative">
                            <div className="absolute inset-0 bg-gradient-to-r from-green-400 to-emerald-500 rounded-2xl blur-xl opacity-20"></div>
                            <div className="relative w-40 h-40 bg-white border-2 border-green-100 rounded-2xl p-2 shadow-lg">
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
                                        <div className="w-10 h-10 mx-auto mb-2 bg-green-100 rounded-full flex items-center justify-center">
                                            <svg viewBox="0 0 24 24" className="w-6 h-6 text-green-500" fill="currentColor">
                                                <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348z" />
                                            </svg>
                                        </div>
                                        <p className="text-xs text-slate-400">扫码添加</p>
                                    </div>
                                </div>
                            </div>
                            {/* 微信 Logo */}
                            <div className="absolute -bottom-2 -right-2 w-9 h-9 bg-green-500 rounded-full shadow-lg flex items-center justify-center border-2 border-white">
                                <svg viewBox="0 0 24 24" className="w-5 h-5 text-white" fill="currentColor">
                                    <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348z" />
                                </svg>
                            </div>
                        </div>
                    </div>

                    {/* 行动指引 - 清晰的 CTA */}
                    <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-3 mb-4 border border-green-100">
                        <p className="text-center text-sm text-slate-700">
                            扫码添加微信，发送「<span className="font-bold text-green-600">买</span>」立即获取
                        </p>
                    </div>

                    {/* 社会证明 */}
                    <div className="flex items-center justify-center gap-4 mb-4">
                        <div className="flex items-center gap-1.5 text-xs text-slate-500">
                            <Users className="w-3.5 h-3.5 text-blue-500" />
                            <span><strong className="text-slate-700">3,200+</strong> 用户选择</span>
                        </div>
                        <div className="w-px h-3 bg-slate-200"></div>
                        <div className="flex items-center gap-1.5 text-xs text-slate-500">
                            <Award className="w-3.5 h-3.5 text-amber-500" />
                            <span><strong className="text-slate-700">4.9</strong> 好评率</span>
                        </div>
                        <div className="w-px h-3 bg-slate-200"></div>
                        <div className="flex items-center gap-1.5 text-xs text-slate-500">
                            <TrendingUp className="w-3.5 h-3.5 text-green-500" />
                            <span><strong className="text-slate-700">秒发</strong></span>
                        </div>
                    </div>

                    {/* 额外价值堆叠 */}
                    <div className="grid grid-cols-2 gap-2 text-xs">
                        <div className="flex items-center gap-2 bg-amber-50 rounded-lg px-3 py-2 border border-amber-100">
                            <Gift className="w-4 h-4 text-amber-500 flex-shrink-0" />
                            <span className="text-slate-600">赠 <strong>3 次</strong>免费额度</span>
                        </div>
                        <div className="flex items-center gap-2 bg-purple-50 rounded-lg px-3 py-2 border border-purple-100">
                            <Sparkles className="w-4 h-4 text-purple-500 flex-shrink-0" />
                            <span className="text-slate-600">解锁 <strong>VIP</strong> 优惠</span>
                        </div>
                    </div>
                </div>

                {/* 底部信任保障 */}
                <div className="bg-slate-50 px-6 py-3 border-t border-slate-100">
                    <div className="flex items-center justify-center gap-4 text-[10px] text-slate-400">
                        <div className="flex items-center gap-1">
                            <Shield className="w-3 h-3" />
                            <span>隐私保护</span>
                        </div>
                        <div className="flex items-center gap-1">
                            <Zap className="w-3 h-3" />
                            <span>极速发送</span>
                        </div>
                        <div className="flex items-center gap-1">
                            <CheckCircle className="w-3 h-3" />
                            <span>不满意退款</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
