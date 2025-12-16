import React, { useState, useEffect, useRef } from 'react';
import { Download, MonitorPlay, LayoutGrid, ChevronLeft, ChevronRight, X, Loader2 } from 'lucide-react';
import { getOutputUrl } from '../api';

export default function ResultView({ result, downloads, isProcessing }) {
    const [activeIndex, setActiveIndex] = useState(0);
    const [isFullscreen, setIsFullscreen] = useState(false);
    
    const pages = result.pages || [];
    
    // Merge result downloads with progressive downloads state
    const currentDownloads = { ...result.downloads, ...downloads };

    const activePage = pages[activeIndex];
    const activeUrl = activePage ? getOutputUrl(activePage.url) : '';

    useEffect(() => {
        const handleKeyDown = (e) => {
            // 支持普通预览和全屏模式的键盘导航
            if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') {
                e.preventDefault();
                setActiveIndex(prev => Math.min(prev + 1, pages.length - 1));
            } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
                e.preventDefault();
                setActiveIndex(prev => Math.max(prev - 1, 0));
            } else if (e.key === 'Escape' && isFullscreen) {
                setIsFullscreen(false);
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [pages.length, isFullscreen]);

    return (
        <div className={`flex flex-col h-full bg-slate-100 ${isFullscreen ? 'fixed inset-0 z-50' : 'relative w-full h-full'}`}>
            
            {/* Toolbar */}
            {!isFullscreen && (
                <div className="flex-shrink-0 h-16 bg-white border-b border-slate-200 flex items-center justify-between px-6 shadow-sm z-20">
                    <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-indigo-50 flex items-center justify-center text-indigo-600">
                           <LayoutGrid className="w-5 h-5" />
                        </div>
                        <div>
                            <h2 className="text-base font-semibold text-slate-800">
                                演示文稿预览
                                {isProcessing && <span className="ml-2 text-xs font-normal text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-100">后台处理中...</span>}
                            </h2>
                            <p className="text-xs text-slate-500">{pages.length} 页幻灯片</p>
                        </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                        {/* PDF Download */}
                        {currentDownloads.pdf ? (
                            <a href={getOutputUrl(currentDownloads.pdf)} download className="btn-secondary group">
                                <Download className="w-4 h-4 text-slate-500 group-hover:text-slate-700" /> 
                                <span>PDF</span>
                            </a>
                        ) : (
                            <button disabled className="btn-secondary opacity-60 cursor-not-allowed">
                                <Loader2 className="w-4 h-4 animate-spin text-slate-400" />
                                <span>PDF 生成中</span>
                            </button>
                        )}

                        {/* PPTX Download */}
                        {currentDownloads.pptx ? (
                            <a href={getOutputUrl(currentDownloads.pptx)} download className="btn-primary">
                                <Download className="w-4 h-4" /> 
                                <span>PPTX</span>
                            </a>
                        ) : (
                            <button disabled className="btn-primary opacity-60 cursor-not-allowed">
                                <Loader2 className="w-4 h-4 animate-spin" />
                                <span>PPTX 转换中</span>
                            </button>
                        )}
                        
                        <div className="w-px h-8 bg-slate-200 mx-1" />
                        
                        <button onClick={() => setIsFullscreen(true)} className="btn-secondary text-slate-700 hover:bg-slate-50">
                            <MonitorPlay className="w-4 h-4" />
                            <span>演示</span>
                        </button>
                    </div>
                </div>
            )}

            {/* Main Area */}
            <div className="flex-1 flex overflow-hidden">
                
                {/* Thumbnails Sidebar */}
                {!isFullscreen && (
                    <div className="w-64 bg-slate-50 border-r border-slate-200 flex flex-col overflow-y-auto p-4 gap-3 custom-scrollbar">
                        {pages.map((page, idx) => (
                            <button
                                key={idx}
                                onClick={() => setActiveIndex(idx)}
                                className={`group flex gap-3 text-left w-full outline-none transition-all duration-200 ${activeIndex === idx ? 'opacity-100' : 'opacity-70 hover:opacity-100'}`}
                            >
                                <span className="text-xs font-medium text-slate-400 w-4 pt-1 text-right tabular-nums">{idx + 1}</span>
                                <div className={`flex-1 aspect-video bg-white rounded border-2 shadow-sm relative overflow-hidden transition-all
                                    ${activeIndex === idx ? 'border-indigo-500 ring-4 ring-indigo-50/50' : 'border-slate-200 group-hover:border-slate-300'}
                                `}>
                                    {/* 真实内容缩略图 - 使用缩小的 iframe */}
                                    <div 
                                        className="absolute inset-0 pointer-events-none"
                                        style={{
                                            width: '1280px',
                                            height: '720px',
                                            transform: 'scale(0.15)',
                                            transformOrigin: 'top left',
                                        }}
                                    >
                                        <iframe
                                            src={getOutputUrl(page.url)}
                                            className="w-full h-full border-0"
                                            title={`Thumbnail ${idx + 1}`}
                                            loading="lazy"
                                            scrolling="no"
                                        />
                                    </div>
                                </div>
                            </button>
                        ))}
                    </div>
                )}

                {/* Preview Canvas */}
                <div className={`flex-1 bg-slate-100/50 flex items-center justify-center relative overflow-hidden ${isFullscreen ? 'bg-black' : 'p-8'}`}>
                    
                    {/* Auto-scaling Container */}
                    <div className="w-full h-full flex items-center justify-center relative">
                        <AutoScaledIframe url={activeUrl} />
                    </div>

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

            <style jsx>{`
                .btn-primary {
                    @apply flex items-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-lg text-sm font-medium hover:bg-slate-800 transition-all shadow-sm active:translate-y-0.5;
                }
                .btn-secondary {
                    @apply flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg text-sm font-medium hover:border-slate-300 hover:bg-slate-50 transition-all shadow-sm active:translate-y-0.5;
                }
            `}</style>
        </div>
    );
}

// Helper component for auto-scaling iframe
function AutoScaledIframe({ url }) {
    const containerRef = useRef(null);
    const [scale, setScale] = useState(1);

    useEffect(() => {
        const updateScale = () => {
            if (!containerRef.current) return;
            const { width, height } = containerRef.current.getBoundingClientRect();
            // Target: 1280x720
            const scaleX = width / 1280;
            const scaleY = height / 720;
            // Use the smaller scale to fit entirely, with margin
            setScale(Math.min(scaleX, scaleY) * 0.9);
        };

        const observer = new ResizeObserver(updateScale);
        if (containerRef.current) observer.observe(containerRef.current);
        
        // Initial calc
        updateScale();

        return () => observer.disconnect();
    }, []);

    if (!url) return null;

    // 计算缩放后的实际尺寸
    const scaledWidth = 1280 * scale;
    const scaledHeight = 720 * scale;

    return (
        <div ref={containerRef} className="w-full h-full flex items-center justify-center">
            {/* 裁剪容器：精确尺寸，确保溢出被裁剪 */}
            <div 
                style={{ 
                    width: `${scaledWidth}px`, 
                    height: `${scaledHeight}px`,
                    overflow: 'hidden',
                    borderRadius: '8px',
                    boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
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
                    />
                </div>
            </div>
        </div>
    );
}
