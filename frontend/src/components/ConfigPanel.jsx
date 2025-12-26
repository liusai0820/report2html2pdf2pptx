import React, { useState } from 'react';
import { User, Layers, FileText, Check, Sparkles, ChevronDown, ChevronUp, Type, Image } from 'lucide-react';

export default function ConfigPanel({ config, onChange }) {
    const [showAdvanced, setShowAdvanced] = useState(true);  // 默认展开

    const handleChange = (key, value) => {
        onChange({ ...config, [key]: value });
    };

    return (
        <div className="space-y-3">
            {/* Organization */}
            <div className="space-y-1">
                <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1">
                    <User className="w-2.5 h-2.5" />
                    汇报单位
                </label>
                <input
                    type="text"
                    value={config.organization}
                    onChange={(e) => handleChange('organization', e.target.value)}
                    className="w-full bg-white border border-slate-200 rounded-md px-2.5 py-1.5 text-xs text-slate-900 focus:outline-none focus:border-slate-400 focus:ring-1 focus:ring-slate-100 transition-all placeholder:text-slate-400"
                    placeholder="输入单位名称..."
                />
            </div>

            <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                    <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1 group relative">
                        <Layers className="w-2.5 h-2.5" />
                        页数
                        <div className="absolute bottom-full left-0 mb-1 hidden group-hover:block w-32 p-1.5 bg-slate-800 text-white text-[9px] rounded shadow-lg z-50 normal-case font-normal leading-relaxed">
                            决定演示文稿的总跨度，包含封面、目录、章节页和总结。
                        </div>
                    </label>
                    <select
                        value={config.target_pages}
                        onChange={(e) => handleChange('target_pages', parseInt(e.target.value))}
                        className="w-full bg-white border border-slate-200 rounded-md px-2 py-1.5 text-xs text-slate-700 outline-none focus:border-slate-400"
                    >
                        <option value={15}>15 页</option>
                        <option value={20}>20 页</option>
                        <option value={25}>25 页</option>
                        <option value={35}>35 页</option>
                        <option value={50}>50 页 (深度报告)</option>
                        <option value={80}>80 页 (研究报告)</option>
                    </select>
                </div>

                <div className="space-y-1">
                    <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1 group relative">
                        <FileText className="w-2.5 h-2.5" />
                        深度
                        <div className="absolute bottom-full right-0 mb-1 hidden group-hover:block w-32 p-1.5 bg-slate-800 text-white text-[9px] rounded shadow-lg z-50 normal-case font-normal leading-relaxed">
                            <b>简洁</b>: 核心结论<br />
                            <b>标准</b>: 论据充分<br />
                            <b>深入</b>: 全面细节
                        </div>
                    </label>
                    <select
                        value={config.content_depth}
                        onChange={(e) => handleChange('content_depth', e.target.value)}
                        className="w-full bg-white border border-slate-200 rounded-md px-2 py-1.5 text-xs text-slate-700 outline-none focus:border-slate-400"
                    >
                        <option value="brief">简洁</option>
                        <option value="normal">标准</option>
                        <option value="detailed">深入</option>
                    </select>
                </div>
            </div>

            {/* 字体选择 */}
            <div className="space-y-1">
                <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1 group relative">
                    <Type className="w-2.5 h-2.5" />
                    字体风格
                    <div className="absolute bottom-full left-0 mb-1 hidden group-hover:block w-40 p-1.5 bg-slate-800 text-white text-[9px] rounded shadow-lg z-50 normal-case font-normal leading-relaxed">
                        <b>现代简约</b>: 黑体系，适合商务汇报<br />
                        <b>典雅庄重</b>: 楷体系，适合政务公文
                    </div>
                </label>
                <select
                    value={config.font_style || 'modern'}
                    onChange={(e) => handleChange('font_style', e.target.value)}
                    className="w-full bg-white border border-slate-200 rounded-md px-2 py-1.5 text-xs text-slate-700 outline-none focus:border-slate-400"
                >
                    <option value="modern">现代简约（黑体）</option>
                    <option value="classic">典雅庄重（楷体）</option>
                </select>
            </div>

            {/* 背景图来源 */}
            <div className="space-y-1">
                <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1 group relative">
                    <Image className="w-2.5 h-2.5" />
                    背景图（封面/章节）
                    <div className="absolute bottom-full left-0 mb-1 hidden group-hover:block w-48 p-1.5 bg-slate-800 text-white text-[9px] rounded shadow-lg z-50 normal-case font-normal leading-relaxed">
                        为封面、章节切换页、结尾页添加精美背景图<br />
                        <b>无</b>: 使用纯色背景<br />
                        <b>Unsplash</b>: 高质量免费图库
                    </div>
                </label>
                <select
                    value={config.bg_image_source || 'none'}
                    onChange={(e) => handleChange('bg_image_source', e.target.value)}
                    className="w-full bg-white border border-slate-200 rounded-md px-2 py-1.5 text-xs text-slate-700 outline-none focus:border-slate-400"
                >
                    <option value="none">无背景图 (纯色)</option>
                    <option value="unsplash">在线图库 (Unsplash)</option>
                    <option value="ai">AI 绘图 (ComfyUI)</option>
                </select>
            </div>

            {/* Flags - inline */}
            <div className="flex gap-4">
                <label className="flex items-center gap-1.5 cursor-pointer select-none">
                    <div className={`w-3.5 h-3.5 rounded border flex items-center justify-center transition-all ${!config.skip_pdf ? 'bg-slate-900 border-slate-900' : 'border-slate-300 bg-white'
                        }`} onClick={() => handleChange('skip_pdf', !config.skip_pdf)}>
                        {!config.skip_pdf && <Check className="w-2.5 h-2.5 text-white" />}
                    </div>
                    <span className="text-[11px] text-slate-600">生成 PDF</span>
                </label>
                <label className="flex items-center gap-1.5 cursor-pointer select-none">
                    <div className={`w-3.5 h-3.5 rounded border flex items-center justify-center transition-all ${!config.skip_pptx ? 'bg-slate-900 border-slate-900' : 'border-slate-300 bg-white'
                        }`} onClick={() => handleChange('skip_pptx', !config.skip_pptx)}>
                        {!config.skip_pptx && <Check className="w-2.5 h-2.5 text-white" />}
                    </div>
                    <span className="text-[11px] text-slate-600">生成 PPTX</span>
                </label>
            </div>

            {/* Custom Instructions - 标签样式与其他配置项一致 */}
            <div className="space-y-1">
                <button
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    className="w-full flex items-center justify-between text-[10px] font-semibold text-slate-500 uppercase tracking-wider"
                >
                    <span className="flex items-center gap-1">
                        <Sparkles className="w-2.5 h-2.5" />
                        自定义 AI 指令
                        {config.custom_instructions && <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full ml-1"></span>}
                    </span>
                    {showAdvanced ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                </button>

                {/* Custom Instructions - Collapsible */}
                {showAdvanced && (
                    <div className="animate-in fade-in slide-in-from-top-2 duration-200">
                        <textarea
                            value={config.custom_instructions || ''}
                            onChange={(e) => handleChange('custom_instructions', e.target.value)}
                            className="w-full bg-white border border-slate-200 rounded-md px-2.5 py-2 text-xs text-slate-900 focus:outline-none focus:border-indigo-300 focus:ring-2 focus:ring-indigo-50 transition-all placeholder:text-slate-400 resize-none"
                            placeholder={`输入您的特殊要求，AI 会尽量遵循：\n• 大纲：第一章重点讲市场分析\n• 风格：使用更正式的语言\n• 数据：突出 2024 年的数据\n• 布局：多用图表，少用文字`}
                            rows={4}
                        />
                        <p className="text-[9px] text-slate-400 leading-relaxed mt-1">
                            提示：自定义指令会与设计系统协同工作，AI 会在保持专业排版的前提下尽量满足您的要求。
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
