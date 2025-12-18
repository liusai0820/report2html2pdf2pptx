import React from 'react';
import { User, Layers, FileText, Check } from 'lucide-react';

export default function ConfigPanel({ config, onChange }) {
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
                {/* Target Pages */}
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
                    </select>
                </div>

                {/* Content Depth */}
                <div className="space-y-1">
                    <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1 group relative">
                        <FileText className="w-2.5 h-2.5" />
                        深度
                        <div className="absolute bottom-full right-0 mb-1 hidden group-hover:block w-32 p-1.5 bg-slate-800 text-white text-[9px] rounded shadow-lg z-50 normal-case font-normal leading-relaxed">
                            <b>简洁</b>: 核心结论<br/>
                            <b>标准</b>: 论据充分<br/>
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

            {/* Flags - inline */}
            <div className="flex gap-4">
                <label className="flex items-center gap-1.5 cursor-pointer select-none">
                    <div className={`w-3.5 h-3.5 rounded border flex items-center justify-center transition-all ${
                        !config.skip_pdf ? 'bg-slate-900 border-slate-900' : 'border-slate-300 bg-white'
                    }`} onClick={() => handleChange('skip_pdf', !config.skip_pdf)}>
                        {!config.skip_pdf && <Check className="w-2.5 h-2.5 text-white" />}
                    </div>
                    <span className="text-[11px] text-slate-600">生成 PDF</span>
                </label>
                <label className="flex items-center gap-1.5 cursor-pointer select-none">
                    <div className={`w-3.5 h-3.5 rounded border flex items-center justify-center transition-all ${
                        !config.skip_pptx ? 'bg-slate-900 border-slate-900' : 'border-slate-300 bg-white'
                    }`} onClick={() => handleChange('skip_pptx', !config.skip_pptx)}>
                        {!config.skip_pptx && <Check className="w-2.5 h-2.5 text-white" />}
                    </div>
                    <span className="text-[11px] text-slate-600">生成 PPTX</span>
                </label>
            </div>
        </div>
    );
}
