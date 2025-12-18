import React, { useState, useEffect } from 'react';
import { FolderOpen, Clock, FileText, ChevronDown, ChevronUp, Loader2 } from 'lucide-react';
import { fetchOutputs, loadOutput } from '../api';

export default function HistoryOutputSelector({ onLoad, isLoading }) {
    const [outputs, setOutputs] = useState([]);
    const [expanded, setExpanded] = useState(false);
    const [loading, setLoading] = useState(false);
    const [loadingItem, setLoadingItem] = useState(null);

    useEffect(() => {
        if (expanded && outputs.length === 0) {
            loadOutputs();
        }
    }, [expanded]);

    const loadOutputs = async () => {
        setLoading(true);
        try {
            const data = await fetchOutputs();
            setOutputs(data);
        } catch (e) {
            console.error('Failed to fetch outputs:', e);
        } finally {
            setLoading(false);
        }
    };

    const handleLoad = async (output) => {
        setLoadingItem(output.name);
        try {
            const result = await loadOutput(output.name);
            onLoad(result, output);
        } catch (e) {
            console.error('Failed to load output:', e);
        } finally {
            setLoadingItem(null);
        }
    };

    return (
        <div className="border border-dashed border-slate-200 rounded-lg overflow-hidden bg-slate-50/50">
            {/* Header - Toggle */}
            <button
                onClick={() => setExpanded(!expanded)}
                className="w-full flex items-center justify-between px-2.5 py-2 hover:bg-slate-100/50 transition-colors"
            >
                <div className="flex items-center gap-1.5 text-[11px] text-slate-600">
                    <FolderOpen className="w-3 h-3" />
                    <span className="font-medium">加载历史输出</span>
                    <span className="text-[9px] px-1 py-0.5 rounded bg-amber-100 text-amber-700 font-medium">
                        调试
                    </span>
                </div>
                {expanded ? (
                    <ChevronUp className="w-3.5 h-3.5 text-slate-400" />
                ) : (
                    <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                )}
            </button>

            {/* Expanded Content */}
            {expanded && (
                <div className="border-t border-slate-200 p-2 space-y-1.5 max-h-[180px] overflow-y-auto custom-scrollbar">
                    {loading ? (
                        <div className="flex items-center justify-center py-4 text-slate-400">
                            <Loader2 className="w-4 h-4 animate-spin mr-1.5" />
                            <span className="text-xs">加载中...</span>
                        </div>
                    ) : outputs.length === 0 ? (
                        <div className="text-center py-4 text-slate-400 text-xs">
                            暂无历史输出
                        </div>
                    ) : (
                        outputs.slice(0, 5).map((output) => (
                            <div
                                key={output.name}
                                className="flex items-center justify-between p-2 bg-white rounded-md border border-slate-100 hover:border-slate-300 transition-all group"
                            >
                                <div className="flex-1 min-w-0">
                                    <div className="font-medium text-[11px] text-slate-700 truncate" title={output.display_name}>
                                        {output.display_name}
                                    </div>
                                    <div className="flex items-center gap-2 mt-0.5 text-[9px] text-slate-400">
                                        <span className="flex items-center gap-0.5">
                                            <FileText className="w-2.5 h-2.5" />
                                            {output.pages_count}页
                                        </span>
                                        {output.has_pdf && (
                                            <span className="px-1 py-0.5 rounded bg-red-50 text-red-500">PDF</span>
                                        )}
                                        {output.has_pptx && (
                                            <span className="px-1 py-0.5 rounded bg-orange-50 text-orange-500">PPTX</span>
                                        )}
                                    </div>
                                </div>
                                <button
                                    onClick={() => handleLoad(output)}
                                    disabled={loadingItem === output.name || isLoading}
                                    className={`ml-2 px-2 py-1 rounded text-[10px] font-medium transition-all
                                        ${loadingItem === output.name || isLoading
                                            ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                                            : 'bg-slate-900 text-white hover:bg-slate-800 opacity-0 group-hover:opacity-100'
                                        }
                                    `}
                                >
                                    {loadingItem === output.name ? (
                                        <Loader2 className="w-2.5 h-2.5 animate-spin" />
                                    ) : (
                                        '加载'
                                    )}
                                </button>
                            </div>
                        ))
                    )}
                    
                    {/* Refresh Button */}
                    {outputs.length > 0 && (
                        <button
                            onClick={loadOutputs}
                            disabled={loading}
                            className="w-full py-1.5 text-[10px] text-slate-500 hover:text-slate-700 transition-colors"
                        >
                            刷新列表
                        </button>
                    )}
                </div>
            )}
        </div>
    );
}
