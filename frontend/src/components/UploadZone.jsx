import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, X } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs) {
    return twMerge(clsx(inputs));
}

export default function UploadZone({ onFileSelect, selectedFile, onUpload }) {
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = async (e) => {
        e.preventDefault();
        setIsDragging(false);
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            await processFile(files[0]);
        }
    };

    const handleFileInput = async (e) => {
        if (e.target.files.length > 0) {
            await processFile(e.target.files[0]);
        }
    };

    const processFile = async (file) => {
        setIsUploading(true);
        try {
            if (onUpload) {
                await onUpload(file);
            }
            onFileSelect({ name: file.name, size: file.size });
        } catch (error) {
            console.error("Upload failed", error);
            alert("上传失败，请重试");
        } finally {
            setIsUploading(false);
        }
    };

    const clearFile = (e) => {
        e.stopPropagation();
        onFileSelect(null);
    };

    return (
        <div className="w-full">
            <AnimatePresence mode="wait">
                {!selectedFile ? (
                    <motion.div
                        key="dropzone"
                        initial={{ opacity: 0, scale: 0.98 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.98 }}
                        className={cn(
                            "group relative overflow-hidden rounded-lg border-2 border-dashed transition-all duration-200 cursor-pointer",
                            "h-20 flex flex-col items-center justify-center p-3 text-center",
                            isDragging
                                ? "border-blue-500 bg-blue-50"
                                : "border-slate-200 bg-slate-50 hover:bg-slate-100 hover:border-slate-300"
                        )}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                        onClick={() => document.getElementById('file-upload').click()}
                    >
                        <input
                            id="file-upload"
                            type="file"
                            className="hidden"
                            accept=".txt,.md,.json,.docx,.doc"
                            onChange={handleFileInput}
                        />

                        <div className="flex items-center gap-3">
                            <div className={cn(
                                "p-2 rounded-full transition-colors",
                                isUploading ? "bg-blue-100 animate-pulse" : "bg-white border border-slate-200 shadow-sm"
                            )}>
                                <Upload className={cn("w-4 h-4", isUploading ? "text-blue-600" : "text-slate-500")} />
                            </div>
                            <div className="text-left">
                                <p className="text-xs font-medium text-slate-700">
                                    {isUploading ? "正在上传..." : "点击或拖拽上传"}
                                </p>
                                <p className="text-[10px] text-slate-400">
                                    支持 word, md, txt, json
                                </p>
                            </div>
                        </div>
                    </motion.div>
                ) : (
                    <motion.div
                        key="file-card"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="w-full"
                    >
                        <div className="bg-white border border-slate-200 p-2.5 flex items-center gap-2.5 rounded-lg shadow-sm relative group hover:border-blue-300 transition-colors">
                             <div className="w-8 h-8 rounded-md bg-blue-50 flex items-center justify-center border border-blue-100">
                                <FileText className="w-4 h-4 text-blue-600" />
                            </div>
                            <div className="flex-1 min-w-0 text-left">
                                <h4 className="font-medium text-xs text-slate-900 truncate max-w-[200px]">{selectedFile.name}</h4>
                                <p className="text-[10px] text-slate-500">已准备就绪</p>
                            </div>

                            <button
                                onClick={clearFile}
                                className="p-1 rounded hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
                            >
                                <X className="w-3.5 h-3.5" />
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
