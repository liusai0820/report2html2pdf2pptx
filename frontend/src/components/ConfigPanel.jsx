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
            <div className="space-y-1.5">
                <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5 ml-0.5">
                    <User className="w-3 h-3" />
                    汇报单位
                </label>
                <input
                    type="text"
                    value={config.organization}
                    onChange={(e) => handleChange('organization', e.target.value)}
                    className="w-full bg-slate-50 hover:bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/10 transition-all placeholder:text-slate-400"
                    placeholder="输入单位名称..."
                />
            </div>

            <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                    <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5 group relative ml-0.5">
                        <Layers className="w-3 h-3" />
                        页数
                        <div className="absolute bottom-full left-0 mb-2 hidden group-hover:block w-40 p-2 bg-slate-900/90 backdrop-blur text-white text-[10px] rounded-lg shadow-xl z-50 normal-case font-normal leading-relaxed border border-white/10">
                            决定演示文稿的总跨度，包含封面、目录、章节页和总结。
                        </div>
                    </label>
                    <select
                        value={config.target_pages}
                        onChange={(e) => handleChange('target_pages', parseInt(e.target.value))}
                        className="w-full bg-slate-50 hover:bg-white border border-slate-200 rounded-lg px-2.5 py-2 text-xs text-slate-700 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/10 transition-all cursor-pointer"
                    >
                        <option value={15}>15 页</option>
                        <option value={20}>20 页</option>
                        <option value={25}>25 页</option>
                        <option value={35}>35 页</option>
                        <option value={50}>50 页 (深度报告)</option>
                        <option value={80}>80 页 (研究报告)</option>
                    </select>
                </div>

                <div className="space-y-1.5">
                    <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5 group relative ml-0.5">
                        <FileText className="w-3 h-3" />
                        深度
                        <div className="absolute bottom-full right-0 mb-2 hidden group-hover:block w-32 p-2 bg-slate-900/90 backdrop-blur text-white text-[10px] rounded-lg shadow-xl z-50 normal-case font-normal leading-relaxed border border-white/10">
                            <b>简洁</b>: 核心结论<br />
                            <b>标准</b>: 论据充分<br />
                            <b>深入</b>: 全面细节
                        </div>
                    </label>
                    <select
                        value={config.content_depth}
                        onChange={(e) => handleChange('content_depth', e.target.value)}
                        className="w-full bg-slate-50 hover:bg-white border border-slate-200 rounded-lg px-2.5 py-2 text-xs text-slate-700 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/10 transition-all cursor-pointer"
                    >
                        <option value="brief">简洁</option>
                        <option value="normal">标准</option>
                        <option value="detailed">深入</option>
                    </select>
                </div>
            </div>

            {/* 字体选择 */}
            <div className="space-y-1.5">
                <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5 group relative ml-0.5">
                    <Type className="w-3 h-3" />
                    字体风格
                    <div className="absolute bottom-full left-0 mb-2 hidden group-hover:block w-40 p-2 bg-slate-900/90 backdrop-blur text-white text-[10px] rounded-lg shadow-xl z-50 normal-case font-normal leading-relaxed border border-white/10">
                        <b>现代简约</b>: 黑体系，适合商务汇报<br />
                        <b>典雅庄重</b>: 楷体系，适合政务公文
                    </div>
                </label>
                <select
                    value={config.font_style || 'modern'}
                    onChange={(e) => handleChange('font_style', e.target.value)}
                    className="w-full bg-slate-50 hover:bg-white border border-slate-200 rounded-lg px-2.5 py-2 text-xs text-slate-700 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/10 transition-all cursor-pointer"
                >
                    <option value="modern">现代简约（黑体）</option>
                    <option value="classic">典雅庄重（楷体）</option>
                </select>
            </div>

            {/* 背景图来源 */}
            <div className="space-y-1.5">
                <label className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5 group relative ml-0.5">
                    <Image className="w-3 h-3" />
                    背景图（封面/章节）
                    <div className="absolute bottom-full left-0 mb-2 hidden group-hover:block w-48 p-2 bg-slate-900/90 backdrop-blur text-white text-[10px] rounded-lg shadow-xl z-50 normal-case font-normal leading-relaxed border border-white/10">
                        为封面、章节切换页、结尾页添加精美背景图<br />
                        <b>无</b>: 使用纯色背景<br />
                        <b>Unsplash</b>: 高质量免费图库
                    </div>
                </label>
                <select
                    value={config.bg_image_source || 'none'}
                    onChange={(e) => handleChange('bg_image_source', e.target.value)}
                    className="w-full bg-slate-50 hover:bg-white border border-slate-200 rounded-lg px-2.5 py-2 text-xs text-slate-700 outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/10 transition-all cursor-pointer"
                >
                    <option value="none">无背景图 (纯色)</option>
                    <option value="unsplash">在线图库 (Unsplash)</option>
                </select>
            </div>

            {/* Flags - inline */}
            <div className="flex gap-6 pt-1">
                <label className="flex items-center gap-2 cursor-pointer select-none group">
                    <div className={`w-4 h-4 rounded-md border flex items-center justify-center transition-all ${!config.skip_pdf ? 'bg-indigo-600 border-indigo-600 shadow-sm shadow-indigo-600/30' : 'border-slate-300 bg-white group-hover:border-indigo-300'
                        }`} onClick={() => handleChange('skip_pdf', !config.skip_pdf)}>
                        {!config.skip_pdf && <Check className="w-3 h-3 text-white" strokeWidth={3} />}
                    </div>
                    <span className="text-xs font-medium text-slate-600 group-hover:text-indigo-900 transition-colors">生成 PDF</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer select-none group">
                    <div className={`w-4 h-4 rounded-md border flex items-center justify-center transition-all ${!config.skip_pptx ? 'bg-indigo-600 border-indigo-600 shadow-sm shadow-indigo-600/30' : 'border-slate-300 bg-white group-hover:border-indigo-300'
                        }`} onClick={() => handleChange('skip_pptx', !config.skip_pptx)}>
                        {!config.skip_pptx && <Check className="w-3 h-3 text-white" strokeWidth={3} />}
                    </div>
                    <span className="text-xs font-medium text-slate-600 group-hover:text-indigo-900 transition-colors">生成 PPTX</span>
                </label>
            </div>

            {/* Custom Instructions - 标签样式与其他配置项一致 */}
            <div className="space-y-1.5 pt-2 border-t border-dashed border-slate-200">
                <button
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    className="w-full flex items-center justify-between text-[11px] font-bold text-slate-400 uppercase tracking-wider hover:text-indigo-500 transition-colors ml-0.5 group"
                >
                    <span className="flex items-center gap-1.5">
                        <Sparkles className="w-3 h-3 group-hover:text-amber-500 transition-colors" />
                        自定义 AI 指令
                        {config.custom_instructions && <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full ml-1"></span>}
                    </span>
                    {showAdvanced ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                </button>

                {/* Custom Instructions - Collapsible */}
                {showAdvanced && (
                    <div className="animate-in fade-in slide-in-from-top-2 duration-300">
                        <textarea
                            value={config.custom_instructions || ''}
                            onChange={(e) => handleChange('custom_instructions', e.target.value)}
                            className="w-full bg-slate-50 hover:bg-white border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/10 transition-all placeholder:text-slate-400 resize-none"
                            placeholder={`输入您的特殊要求，AI 会尽量遵循：\n• 大纲：第一章重点讲市场分析\n• 风格：使用更正式的语言\n• 数据：突出 2024 年的数据\n• 布局：多用图表，少用文字`}
                            rows={4}
                        />
                        <p className="text-[10px] text-slate-400 leading-relaxed mt-1.5 px-0.5">
                            提示：自定义指令会与设计系统协同工作，AI 会在保持专业排版的前提下尽量满足您的要求。
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
