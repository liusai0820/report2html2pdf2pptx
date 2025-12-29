/**
 * ResultView.jsx - 结果展示组件
 *
 * @input:  result (pages数组), downloads (PDF/PPTX路径), api.getOutputUrl
 * @output: ResultView组件（分栏预览、网格视图、全屏演示、下载功能）
 * @pos:    前端的核心展示组件，负责幻灯片预览和导出操作
 *
 * ⚠️ 一旦我被更新，务必更新：
 *    1. 我的头部注释
 *    2. /frontend/src/components/_FOLDER.md
 */

import React, { useState, useEffect, useRef } from 'react';
import { Download, MonitorPlay, LayoutGrid, PanelLeft, ChevronLeft, ChevronRight, X, Loader2, ZoomIn, ZoomOut, Sparkles, Zap } from 'lucide-react';
import { getOutputUrl } from '../api';
import { useAuth } from '../contexts/AuthContext';
import FeedbackModal from './FeedbackModal';

// Turbo 升级弹窗组件 - 瑞士杂志风格
const TurboUpgradeModal = ({ isOpen, onClose }) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ backgroundColor: 'rgba(0, 0, 0, 0.6)' }}>
            <div 
                className="relative bg-white rounded-none shadow-2xl max-w-md w-full overflow-hidden"
                style={{ fontFamily: '"Inter", "Noto Sans SC", sans-serif' }}
            >
                {/* 关闭按钮 */}
                <button 
                    onClick={onClose}
                    className="absolute top-4 right-4 text-slate-400 hover:text-slate-900 transition-colors z-10"
                >
                    <X className="w-5 h-5" />
                </button>

                {/* 头部 - 极简标题 */}
                <div className="px-8 pt-12 pb-6 border-b border-slate-100">
                    <div className="flex items-center gap-2 mb-3">
                        <Zap className="w-5 h-5 text-amber-500" />
                        <span className="text-xs font-medium tracking-widest uppercase text-slate-400">Premium Feature</span>
                    </div>
                    <h2 className="text-3xl font-light tracking-tight text-slate-900 mb-2" style={{ lineHeight: '1.2' }}>
                        解锁 Turbo
                    </h2>
                    <p className="text-sm text-slate-500 font-light leading-relaxed">
                        使用顶尖 AI 模型，生成更高质量的演示文稿
                    </p>
                </div>

                {/* 功能列表 */}
                <div className="px-8 py-6 space-y-4">
                    <div className="flex items-start gap-3">
                        <div className="w-1 h-1 bg-slate-900 rounded-full mt-2" />
                        <div>
                            <p className="text-sm font-medium text-slate-900">PPTX 格式导出</p>
                            <p className="text-xs text-slate-500 mt-0.5">原生 PowerPoint 格式，完美兼容</p>
                        </div>
                    </div>
                    <div className="flex items-start gap-3">
                        <div className="w-1 h-1 bg-slate-900 rounded-full mt-2" />
                        <div>
                            <p className="text-sm font-medium text-slate-900">顶尖 AI 模型</p>
                            <p className="text-xs text-slate-500 mt-0.5">更强的文本理解与创作能力，页面精美</p>
                        </div>
                    </div>
                    <div className="flex items-start gap-3">
                        <div className="w-1 h-1 bg-slate-900 rounded-full mt-2" />
                        <div>
                            <p className="text-sm font-medium text-slate-900">优先生成队列</p>
                            <p className="text-xs text-slate-500 mt-0.5">无需等待，即刻生成，额度管够</p>
                        </div>
                    </div>
                </div>

                {/* CTA 按钮 */}
                <div className="px-8 pb-8">
                    <div className="bg-slate-50 border border-slate-200 rounded-sm p-4 mb-3">
                        <div className="flex items-center gap-2 mb-2">
                            <span className="text-xs font-medium tracking-widest uppercase text-slate-400">联系方式</span>
                        </div>
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-green-500 rounded-sm flex items-center justify-center flex-shrink-0">
                                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                                    <path d="M8.691 2.188C3.891 2.188 0 5.476 0 9.53c0 2.212 1.17 4.203 3.002 5.55a.59.59 0 0 1 .213.665l-.39 1.48c-.019.07-.048.141-.048.213 0 .163.13.295.29.295a.326.326 0 0 0 .167-.054l1.903-1.114a.864.864 0 0 1 .717-.098 10.16 10.16 0 0 0 2.837.403c.276 0 .543-.027.811-.05-.857-2.578.157-4.972 1.932-6.446 1.703-1.415 3.882-1.98 5.853-1.838-.576-3.583-4.196-6.348-8.596-6.348zM5.785 5.991c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178A1.17 1.17 0 0 1 4.623 7.17c0-.651.52-1.18 1.162-1.18zm5.813 0c.642 0 1.162.529 1.162 1.18a1.17 1.17 0 0 1-1.162 1.178 1.17 1.17 0 0 1-1.162-1.178c0-.651.52-1.18 1.162-1.18zm5.34 2.867c-1.797-.052-3.746.512-5.28 1.786-1.72 1.428-2.687 3.72-1.78 6.22.942 2.453 3.666 4.229 6.884 4.229.826 0 1.622-.12 2.361-.336a.722.722 0 0 1 .598.082l1.584.926a.272.272 0 0 0 .14.047c.134 0 .24-.111.24-.247 0-.06-.023-.12-.038-.177l-.327-1.233a.582.582 0 0 1-.023-.156.49.49 0 0 1 .201-.398C23.024 18.48 24 16.82 24 14.98c0-3.21-2.931-5.837-6.656-6.088V8.89c-.135-.01-.27-.027-.407-.03zm-2.53 3.274c.535 0 .969.44.969.982a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.542.434-.982.969-.982zm4.844 0c.535 0 .969.44.969.982a.976.976 0 0 1-.969.983.976.976 0 0 1-.969-.983c0-.542.434-.982.969-.982z"/>
                                </svg>
                            </div>
                            <div className="flex-1">
                                <p className="text-sm font-medium text-slate-900">微信号</p>
                                <p className="text-base font-mono text-slate-700 tracking-wide">liusai0820</p>
                            </div>
                        </div>
                        <p className="text-xs text-slate-500 mt-3 leading-relaxed">
                            添加微信备注「Turbo」，了解升级详情
                        </p>
                    </div>
                    <button 
                        onClick={onClose}
                        className="block w-full py-3 text-slate-500 hover:text-slate-900 text-center text-xs font-light transition-colors"
                    >
                        暂不升级
                    </button>
                </div>

                {/* 底部装饰线 */}
                <div className="h-1 bg-gradient-to-r from-amber-400 via-amber-500 to-amber-600" />
            </div>
        </div>
    );
};

// 强制下载文件（避免浏览器打开文件导致页面跳转）
const forceDownload = async (url, filename) => {
    try {
        const response = await fetch(url);
        const blob = await response.blob();
        const blobUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = blobUrl;
        link.download = filename || url.split('/').pop() || 'download';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(blobUrl);
    } catch (error) {
        console.error('Download failed:', error);
        // 降级为直接打开（在新标签页）
        window.open(url, '_blank');
    }
};

export default function ResultView({ result, downloads, isProcessing, generationId, documentName }) {
    const { user } = useAuth();
    const [activeIndex, setActiveIndex] = useState(0);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [viewMode, setViewMode] = useState('split'); // 'split' | 'grid'
    const [downloadingPdf, setDownloadingPdf] = useState(false);
    const [downloadingPptx, setDownloadingPptx] = useState(false);
    const [gridColumns, setGridColumns] = useState(4); // 网格列数控制 (1-6)
    
    // 反馈弹窗状态
    const [showFeedbackModal, setShowFeedbackModal] = useState(false);
    const [feedbackGiven, setFeedbackGiven] = useState(false); // 本次生成是否已给过反馈
    const [pendingDownload, setPendingDownload] = useState(null); // 'pdf' | 'pptx' | null - 等待下载的文件类型
    
    // Turbo 升级弹窗状态
    const [showTurboModal, setShowTurboModal] = useState(false);

    // 如果正在处理中，模拟进度
    const [progress, setProgress] = useState(0);
    useEffect(() => {
        if (isProcessing) {
            const interval = setInterval(() => {
                setProgress(prev => (prev >= 90 ? 90 : prev + 10));
            }, 1000);
            return () => clearInterval(interval);
        } else {
            setProgress(100);
        }
    }, [isProcessing]);

    // PPTX 生成超时检测
    const [isPptxTimeout, setIsPptxTimeout] = useState(false);
    const prevPdfRef = React.useRef(downloads?.pdf);
    
    useEffect(() => {
        let timeoutTimer;
        
        // 检测是否切换了文档（PDF 路径变了）
        const pdfChanged = prevPdfRef.current !== downloads?.pdf;
        prevPdfRef.current = downloads?.pdf;
        
        if (downloads?.pptx) {
            // 如果 PPTX 有了，清除超时状态
            setIsPptxTimeout(false);
        } else {
            // 如果没有 PPTX
            if (pdfChanged) {
                // 切换文档时，根据当前状态决定：如果不在处理中，直接显示超时
                if (!isProcessing) {
                    setIsPptxTimeout(true);
                } else {
                    // 正在处理中的新任务，重置超时状态，开始新的计时
                    setIsPptxTimeout(false);
                }
            } else if (!isProcessing) {
                // 同一文档，不在处理中，直接显示超时（历史记录或已结束任务）
                setIsPptxTimeout(true);
            } else if (!isPptxTimeout) {
                // 正在处理中，且尚未超时，开始 2 分钟倒计时
                timeoutTimer = setTimeout(() => {
                    setIsPptxTimeout(true);
                }, 120000);
            }
        }
        return () => clearTimeout(timeoutTimer);
    }, [downloads?.pptx, downloads?.pdf, isProcessing, isPptxTimeout]);

    // 处理 PDF 下载
    const handlePdfDownload = async () => {
        if (!downloads?.pdf) return;
        
        // 如果还没给过反馈，先弹出反馈框（强制模式）
        if (!feedbackGiven) {
            setPendingDownload('pdf');
            setShowFeedbackModal(true);
            return;
        }
        
        // 已经给过反馈，直接下载
        await performPdfDownload();
    };
    
    // 实际执行 PDF 下载
    const performPdfDownload = async () => {
        if (!downloads?.pdf) return;
        setDownloadingPdf(true);
        const filename = downloads.pdf.split('/').pop();
        await forceDownload(getOutputUrl(downloads.pdf), filename);
        setDownloadingPdf(false);
    };
    
    // 反馈完成后的回调
    const handleFeedbackComplete = async () => {
        setFeedbackGiven(true);
        
        // 如果有等待下载，执行下载
        if (pendingDownload === 'pdf') {
            await performPdfDownload();
        } else if (pendingDownload === 'pptx') {
            await performPptxDownload();
        }
        setPendingDownload(null);
    };

    // 处理 PPTX 下载
    const handlePptxDownload = async () => {
        if (!downloads?.pptx) return;
        
        // 如果还没给过反馈，先弹出反馈框（强制模式）
        if (!feedbackGiven) {
            setPendingDownload('pptx');
            setShowFeedbackModal(true);
            return;
        }
        
        await performPptxDownload();
    };
    
    // 实际执行 PPTX 下载
    const performPptxDownload = async () => {
        if (!downloads?.pptx) return;
        setDownloadingPptx(true);
        const filename = downloads.pptx.split('/').pop();
        await forceDownload(getOutputUrl(downloads.pptx), filename);
        setDownloadingPptx(false);
    };

    // 键盘导航支持（分栏视图和演示播放模式都支持）
    useEffect(() => {
        const handleKeyDown = (e) => {
            const totalPages = result?.pages?.length || 0;
            if (totalPages === 0) return;

            // 网格视图下不处理键盘事件
            if (viewMode === 'grid' && !isFullscreen) return;

            switch (e.key) {
                case 'ArrowRight':
                case 'ArrowDown':
                case ' ':  // Space
                    e.preventDefault();
                    setActiveIndex(prev => Math.min(totalPages - 1, prev + 1));
                    break;
                case 'ArrowLeft':
                case 'ArrowUp':
                    e.preventDefault();
                    setActiveIndex(prev => Math.max(0, prev - 1));
                    break;
                case 'Escape':
                    if (isFullscreen) {
                        e.preventDefault();
                        setIsFullscreen(false);
                    }
                    break;
                case 'Home':
                    e.preventDefault();
                    setActiveIndex(0);
                    break;
                case 'End':
                    e.preventDefault();
                    setActiveIndex(totalPages - 1);
                    break;
                case 'Enter':
                    // Enter 只在全屏模式下翻页，分栏模式下可用于其他操作
                    if (isFullscreen) {
                        e.preventDefault();
                        setActiveIndex(prev => Math.min(totalPages - 1, prev + 1));
                    }
                    break;
                default:
                    break;
            }
        };

        // 全屏模式下的点击翻页（左半屏上一页，右半屏下一页）
        const handleClick = (e) => {
            if (!isFullscreen) return; // 分栏模式下在 Preview 区域单独处理

            const totalPages = result?.pages?.length || 0;
            if (totalPages === 0) return;

            // 忽略按钮点击
            if (e.target.tagName === 'BUTTON' || e.target.closest('button')) return;

            const x = e.clientX;
            const screenWidth = window.innerWidth;

            if (x < screenWidth / 3) {
                setActiveIndex(prev => Math.max(0, prev - 1));
            } else if (x > screenWidth * 2 / 3) {
                setActiveIndex(prev => Math.min(totalPages - 1, prev + 1));
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        if (isFullscreen) {
            window.addEventListener('click', handleClick);
        }

        return () => {
            window.removeEventListener('keydown', handleKeyDown);
            window.removeEventListener('click', handleClick);
        };
    }, [isFullscreen, viewMode, result?.pages?.length]);

    // 分栏视图预览区点击翻页
    const handlePreviewClick = (e) => {
        if (isFullscreen) return; // 全屏模式由全局事件处理

        const totalPages = result?.pages?.length || 0;
        if (totalPages === 0) return;

        // 忽略按钮点击
        if (e.target.tagName === 'BUTTON' || e.target.closest('button')) return;

        const rect = e.currentTarget.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const width = rect.width;

        if (x < width / 3) {
            // 左侧 1/3：上一页
            setActiveIndex(prev => Math.max(0, prev - 1));
        } else if (x > width * 2 / 3) {
            // 右侧 1/3：下一页
            setActiveIndex(prev => Math.min(totalPages - 1, prev + 1));
        }
        // 中间 1/3：不做操作（可用于未来的其他交互）
    };

    if (!result) return null;

    // 解析页面
    const pages = result.pages || [];

    // 如果没有 pages 数据，可能是在等待生成或数据结构不匹配
    if (pages.length === 0 && result.html) {
        // Fallback: 只显示主 HTML
        return (
            <div className="w-full h-full bg-slate-100 flex items-center justify-center">
                <iframe src={getOutputUrl(result.html)} className="w-full h-full border-0" title="Preview" />
            </div>
        );
    }

    const activePage = pages[activeIndex];
    const activeUrl = activePage ? getOutputUrl(activePage.url) : '';

    return (
        <div className={`flex flex-col h-full bg-slate-100 ${isFullscreen ? 'fixed inset-0 z-50' : 'relative w-full h-full'}`}>

            {/* Toolbar */}
            {/* Toolbar */}
            {!isFullscreen && (
                <div className="flex-shrink-0 h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 shadow-sm z-20">
                    <div className="flex items-center gap-6">
                        <div className="flex items-center gap-4">
                            <div className="w-10 h-10 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600 shadow-sm border border-indigo-100">
                                <LayoutGrid className="w-5 h-5" />
                            </div>
                            <div>
                                <h2 className="text-sm font-semibold text-slate-800 flex items-center gap-2 max-w-[300px] truncate" title={result.document_name || "演示文稿预览"}>
                                    {result.document_name || "演示文稿预览"}
                                    {isProcessing && <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-amber-50 text-amber-700 animate-pulse whitespace-nowrap border border-amber-100">生成中</span>}
                                </h2>
                                <p className="text-xs text-slate-500 font-medium">{pages.length} 页幻灯片</p>
                            </div>
                        </div>

                        {/* View Switcher */}
                        <div className="h-6 w-px bg-slate-200" />

                        <div className="flex bg-slate-100/80 p-1 rounded-lg border border-slate-200/60">
                            <button
                                onClick={() => setViewMode('split')}
                                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200 ${viewMode === 'split' ? 'bg-white shadow text-slate-800' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50'}`}
                            >
                                <PanelLeft className="w-3.5 h-3.5" />
                                <span>分栏视图</span>
                            </button>
                            <button
                                onClick={() => setViewMode('grid')}
                                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all duration-200 ${viewMode === 'grid' ? 'bg-white shadow text-slate-800' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-200/50'}`}
                            >
                                <LayoutGrid className="w-3.5 h-3.5" />
                                <span>网格预览</span>
                            </button>
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        {/* PDF Download */}
                        {downloads?.pdf ? (
                            <button onClick={handlePdfDownload} disabled={downloadingPdf} className="h-9 px-3 flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors border border-transparent hover:border-slate-200" title="下载 PDF 文档">
                                {downloadingPdf ? (
                                    <Loader2 className="w-4 h-4 animate-spin text-slate-400" />
                                ) : (
                                    <Download className="w-4 h-4" />
                                )}
                                <span>PDF</span>
                            </button>
                        ) : (
                            <button disabled className="h-9 px-3 flex items-center gap-2 text-sm font-medium text-slate-400 cursor-not-allowed">
                                <Loader2 className="w-4 h-4 animate-spin opacity-50" />
                                <span>准备中</span>
                            </button>
                        )}

                        {/* PPTX Download - 始终显示，点击弹出升级提示 */}
                        <button 
                            onClick={() => setShowTurboModal(true)} 
                            className="h-9 px-3 flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors border border-transparent hover:border-slate-200 relative group" 
                            title="升级 Turbo 解锁 PPTX 导出"
                        >
                            <Download className="w-4 h-4" />
                            <span>PPTX</span>
                            <Sparkles className="w-3 h-3 text-amber-500 opacity-0 group-hover:opacity-100 transition-opacity absolute -top-1 -right-1" />
                        </button>

                        <div className="h-6 w-px bg-slate-200 mx-2" />

                        <button
                            onClick={() => setIsFullscreen(true)}
                            className="h-9 pr-4 pl-3 flex items-center gap-2 bg-slate-900 hover:bg-slate-800 text-white text-sm font-medium rounded-lg transition-all shadow-sm hover:shadow hover:-translate-y-0.5"
                        >
                            <MonitorPlay className="w-4 h-4" />
                            <span>演示播放</span>
                        </button>
                    </div>
                </div>
            )}

            {/* Main Content Area */}
            {viewMode === 'grid' && !isFullscreen ? (
                /* Grid View Overview */
                <div className="flex-1 flex flex-col overflow-hidden bg-slate-100">
                    {/* Grid Zoom Controls */}
                    <div className="flex-shrink-0 px-8 py-3 bg-white/80 backdrop-blur-sm border-b border-slate-200 flex items-center justify-between">
                        <span className="text-xs text-slate-500">每行显示 {gridColumns} 列</span>
                        <div className="flex items-center gap-3">
                            <button
                                onClick={() => setGridColumns(Math.min(6, gridColumns + 1))}
                                disabled={gridColumns >= 6}
                                className="p-1.5 rounded-md hover:bg-slate-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                                title="缩小"
                            >
                                <ZoomOut className="w-4 h-4 text-slate-600" />
                            </button>
                            <input
                                type="range"
                                min="1"
                                max="6"
                                value={gridColumns}
                                onChange={(e) => setGridColumns(parseInt(e.target.value))}
                                className="w-32 h-1.5 bg-slate-200 rounded-full appearance-none cursor-pointer accent-indigo-600"
                                style={{ direction: 'rtl' }} // 反转滑块方向：左边大，右边小
                            />
                            <button
                                onClick={() => setGridColumns(Math.max(1, gridColumns - 1))}
                                disabled={gridColumns <= 1}
                                className="p-1.5 rounded-md hover:bg-slate-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                                title="放大"
                            >
                                <ZoomIn className="w-4 h-4 text-slate-600" />
                            </button>
                        </div>
                    </div>

                    {/* Grid Content */}
                    <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
                        <div className="max-w-[2000px] mx-auto">
                            <div
                                className="grid gap-6 transition-all duration-300"
                                style={{
                                    gridTemplateColumns: `repeat(${gridColumns}, minmax(0, 1fr))`
                                }}
                            >
                                {pages.map((page, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => {
                                            setActiveIndex(idx);
                                            setViewMode('split');
                                        }}
                                        className="group flex flex-col gap-2 outline-none animate-in fade-in zoom-in-95 duration-300"
                                        style={{ animationDelay: `${idx * 20}ms`, animationFillMode: 'backwards' }}
                                    >
                                        <div className="w-full aspect-video bg-white rounded-lg border border-slate-200 shadow-sm group-hover:shadow-xl group-hover:border-indigo-300 group-hover:-translate-y-1 transition-all duration-300 relative overflow-hidden">
                                            {/* 真实内容缩略图 - 使用缩小的 iframe */}
                                            <div className="absolute inset-0 pointer-events-none w-full h-full bg-slate-50">
                                                <AutoScaledIframe url={getOutputUrl(page.url)} isThumbnail={true} />
                                            </div>
                                            {/* Overlay to prevent iframe interaction & add hover effect */}
                                            <div className="absolute inset-0 bg-transparent group-hover:bg-indigo-500/5 transition-colors" />
                                        </div>
                                        <div className="flex justify-between items-center px-1 opacity-60 group-hover:opacity-100 transition-opacity">
                                            <span className="text-xs font-medium text-slate-500">Page {idx + 1}</span>
                                            <div className="h-px flex-1 bg-slate-200 mx-3 group-hover:bg-slate-300" />
                                            <span className="text-[10px] text-slate-400 uppercase tracking-wider">{page.type || 'SLIDE'}</span>
                                        </div>
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            ) : (
                /* Split View (Original) */
                <div className="flex-1 flex overflow-hidden">

                    {/* Thumbnails Sidebar */}
                    {!isFullscreen && (
                        <div className="w-64 bg-slate-50 border-r border-slate-200 flex flex-col overflow-y-auto p-4 gap-3 custom-scrollbar flex-shrink-0">
                            {pages.map((page, idx) => (
                                <button
                                    key={idx}
                                    onClick={() => setActiveIndex(idx)}
                                    className={`group flex gap-3 text-left w-full outline-none transition-all duration-200 ${activeIndex === idx ? 'opacity-100' : 'opacity-70 hover:opacity-100'}`}
                                >
                                    <span className="text-xs font-medium text-slate-400 w-4 pt-1 text-right tabular-nums flex-shrink-0">{idx + 1}</span>
                                    <div className={`flex-1 aspect-video bg-white rounded border-2 shadow-sm relative overflow-hidden transition-all
                                        ${activeIndex === idx ? 'border-indigo-500 ring-4 ring-indigo-50/50' : 'border-slate-200 group-hover:border-slate-300'}
                                    `}>
                                        <div className="absolute inset-0 pointer-events-none overflow-hidden bg-slate-50">
                                            <AutoScaledIframe url={getOutputUrl(page.url)} isThumbnail={true} />
                                        </div>
                                    </div>
                                </button>
                            ))}
                        </div>
                    )}

                    {/* Preview Canvas */}
                    <div
                        className={`flex-1 bg-slate-100/50 flex items-center justify-center relative overflow-hidden ${isFullscreen ? 'bg-black' : 'p-8'} ${!isFullscreen ? 'cursor-pointer' : ''}`}
                        onClick={!isFullscreen ? handlePreviewClick : undefined}
                    >

                        {/* Auto-scaling Container */}
                        <div className="w-full h-full flex items-center justify-center relative pointer-events-none">
                            <AutoScaledIframe url={activeUrl} />
                        </div>

                        {/* Page indicator for split view */}
                        {!isFullscreen && (
                            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex items-center gap-2 bg-black/60 text-white text-xs px-3 py-1.5 rounded-full backdrop-blur-sm">
                                <span>{activeIndex + 1} / {pages.length}</span>
                            </div>
                        )}

                        {/* Navigation Controls (Visible on Hover in Fullscreen) */}
                        {(isFullscreen) && (
                            <>
                                <div className="absolute top-4 right-4 z-50">
                                    <button onClick={() => setIsFullscreen(false)} className="p-2 bg-black/50 text-white rounded hover:bg-black/70 backdrop-blur">
                                        <X className="w-6 h-6" />
                                    </button>
                                </div>

                                <button
                                    onClick={() => setActiveIndex(Math.max(0, activeIndex - 1))}
                                    className={`absolute left-4 top-1/2 -translate-y-1/2 p-4 rounded-full text-white/50 hover:text-white hover:bg-white/10 transition-all ${activeIndex === 0 ? 'hidden' : ''}`}
                                >
                                    <ChevronLeft className="w-12 h-12" />
                                </button>

                                <button
                                    onClick={() => setActiveIndex(Math.min(pages.length - 1, activeIndex + 1))}
                                    className={`absolute right-4 top-1/2 -translate-y-1/2 p-4 rounded-full text-white/50 hover:text-white hover:bg-white/10 transition-all ${activeIndex === pages.length - 1 ? 'hidden' : ''}`}
                                >
                                    <ChevronRight className="w-12 h-12" />
                                </button>
                            </>
                        )}
                    </div>
                </div>
            )}

            <style jsx>{`
                .btn-primary {
                    @apply flex items-center bg-slate-900 text-white rounded-lg transition-all shadow-sm active:translate-y-0.5;
                }
                .btn-secondary {
                    @apply flex items-center bg-white border border-slate-200 text-slate-700 rounded-lg hover:border-slate-300 hover:bg-slate-50 transition-all shadow-sm active:translate-y-0.5;
                }
            `}</style>

            {/* 反馈弹窗 - 首次下载时强制填写 */}
            <FeedbackModal
                isOpen={showFeedbackModal}
                onClose={() => {
                    setShowFeedbackModal(false);
                    // 非强制模式关闭时也标记已给过反馈
                    if (!pendingDownload) {
                        setFeedbackGiven(true);
                    }
                }}
                generationId={generationId}
                userId={user?.id}
                userEmail={user?.email}
                documentName={documentName}
                mandatory={pendingDownload !== null}
                onFeedbackComplete={handleFeedbackComplete}
            />

            {/* Turbo 升级弹窗 */}
            <TurboUpgradeModal 
                isOpen={showTurboModal}
                onClose={() => setShowTurboModal(false)}
            />
        </div>
    );
}

// Helper component for auto-scaling iframe
function AutoScaledIframe({ url, isThumbnail = false }) {
    const containerRef = useRef(null);
    const [scale, setScale] = useState(1);

    useEffect(() => {
        const updateScale = () => {
            if (!containerRef.current) return;
            const { width, height } = containerRef.current.getBoundingClientRect();
            if (width === 0 || height === 0) return;

            // Target: 1280x720
            const scaleX = width / 1280;
            const scaleY = height / 720;
            // Use the smaller scale to fit entirely
            // Remove margin for thumbnails to fill space completely
            const marginFactor = isThumbnail ? 1 : 0.9;
            setScale(Math.min(scaleX, scaleY) * marginFactor);
        };

        const observer = new ResizeObserver(updateScale);
        if (containerRef.current) observer.observe(containerRef.current);

        // Initial calc
        updateScale();
        // Retry shortly after mount to ensure layout is stable
        setTimeout(updateScale, 100);

        return () => observer.disconnect();
    }, [isThumbnail]);

    if (!url) return null;

    // 计算缩放后的实际尺寸
    const scaledWidth = 1280 * scale;
    const scaledHeight = 720 * scale;

    return (
        <div ref={containerRef} className="w-full h-full flex items-center justify-center overflow-hidden">
            {/* 裁剪容器：精确尺寸 */}
            <div
                style={{
                    width: `${scaledWidth}px`,
                    height: `${scaledHeight}px`,
                    overflow: 'hidden',
                    borderRadius: isThumbnail ? '0' : '8px',
                    boxShadow: isThumbnail ? 'none' : '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
                    flexShrink: 0 // Prevent compression
                }}
            >
                {/* 内部缩放容器 */}
                <div
                    style={{
                        width: '1280px',
                        height: '720px',
                        transform: `scale(${scale})`,
                        transformOrigin: 'top left'
                    }}
                >
                    <iframe
                        src={url}
                        className="w-full h-full border-0 bg-white"
                        title="Slide content"
                        scrolling="no"
                        loading="lazy"
                    />
                </div>
            </div>
        </div>
    );
}
