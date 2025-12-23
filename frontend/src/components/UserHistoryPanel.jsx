import React, { useState, useEffect } from 'react';
import { History, FileText, Loader2, RefreshCw, Clock, ChevronDown, ChevronUp } from 'lucide-react';
import { getUserGenerations } from '../lib/supabase';
import { loadOutput } from '../api';

export default function UserHistoryPanel({ userId, onLoad, isLoading }) {
  const [generations, setGenerations] = useState([]);
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingItem, setLoadingItem] = useState(null);

  useEffect(() => {
    if (expanded && userId) {
      fetchHistory();
    }
  }, [expanded, userId]);

  const fetchHistory = async () => {
    if (!userId) return;
    setLoading(true);
    try {
      const data = await getUserGenerations(userId, 10);
      setGenerations(data);
    } catch (e) {
      console.error('Failed to fetch history:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleLoad = async (gen) => {
    if (!gen.output_path) {
      console.error('No output path for this generation');
      return;
    }
    
    setLoadingItem(gen.id);
    try {
      // output_path 可能是:
      // 1. output/xxx_v2/presentation.html (相对路径)
      // 2. /output/xxx_v2/presentation.html (绝对路径)
      // 3. /app/output/xxx_v2/presentation.html (Docker 完整路径)
      // 4. xxx_v2 (纯文件夹名)
      let folderName = gen.output_path;
      
      console.log('Original output_path:', folderName);
      
      // 移除可能的 /app 前缀 (Docker 路径)
      if (folderName.includes('/app/output/')) {
        folderName = folderName.replace('/app/output/', '');
      }
      // 移除 /output/ 前缀 (绝对路径)
      else if (folderName.startsWith('/output/')) {
        folderName = folderName.replace('/output/', '');
      }
      // 移除 output/ 前缀 (相对路径)
      else if (folderName.startsWith('output/')) {
        folderName = folderName.replace('output/', '');
      }
      
      // 如果还包含路径分隔符，提取第一个目录段（文件夹名）
      if (folderName.includes('/')) {
        folderName = folderName.split('/')[0];
      }
      
      console.log('Extracted folder name:', folderName);
      const result = await loadOutput(folderName);
      onLoad(result, {
        name: folderName,
        display_name: gen.document_name || folderName
      });
    } catch (e) {
      console.error('Failed to load output:', e);
    } finally {
      setLoadingItem(null);
    }
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return '刚刚';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`;
    
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
  };

  return (
    <div className="border border-slate-200 rounded-lg overflow-hidden bg-white">
      {/* Header */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between px-3 py-2.5 hover:bg-slate-50 transition-colors"
      >
        <div className="flex items-center gap-2 text-xs text-slate-700">
          <History className="w-3.5 h-3.5" />
          <span className="font-medium">我的生成记录</span>
          {generations.length > 0 && (
            <span className="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-500">
              {generations.length}
            </span>
          )}
        </div>
        {expanded ? (
          <ChevronUp className="w-4 h-4 text-slate-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-slate-400" />
        )}
      </button>

      {/* Content */}
      {expanded && (
        <div className="border-t border-slate-100">
          {loading ? (
            <div className="flex items-center justify-center py-6 text-slate-400">
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
              <span className="text-xs">加载中...</span>
            </div>
          ) : generations.length === 0 ? (
            <div className="text-center py-6 text-slate-400">
              <FileText className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-xs">暂无生成记录</p>
              <p className="text-[10px] mt-1">生成的演示文稿将显示在这里</p>
            </div>
          ) : (
            <div className="max-h-[240px] overflow-y-auto custom-scrollbar">
              {generations.map((gen) => (
                <div
                  key={gen.id}
                  className="flex items-center justify-between px-3 py-2.5 border-b border-slate-50 last:border-0 hover:bg-slate-50 transition-colors group"
                >
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-xs text-slate-700 truncate">
                      {gen.document_name || '未命名文档'}
                    </div>
                    <div className="flex items-center gap-2 mt-1 text-[10px] text-slate-400">
                      <span className="flex items-center gap-0.5">
                        <Clock className="w-2.5 h-2.5" />
                        {formatDate(gen.created_at)}
                      </span>
                      {gen.scenario && (
                        <span className="px-1.5 py-0.5 rounded bg-blue-50 text-blue-600">
                          {gen.scenario}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  {gen.output_path ? (
                    <button
                      onClick={() => handleLoad(gen)}
                      disabled={loadingItem === gen.id || isLoading}
                      className={`ml-2 px-2.5 py-1 rounded text-[10px] font-medium transition-all
                        ${loadingItem === gen.id || isLoading
                          ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                          : 'bg-slate-900 text-white hover:bg-slate-700 opacity-0 group-hover:opacity-100'
                        }
                      `}
                    >
                      {loadingItem === gen.id ? (
                        <Loader2 className="w-3 h-3 animate-spin" />
                      ) : (
                        '查看'
                      )}
                    </button>
                  ) : (
                    <span className="text-[10px] text-slate-300 ml-2">无预览</span>
                  )}
                </div>
              ))}
            </div>
          )}
          
          {/* Refresh */}
          <div className="px-3 py-2 border-t border-slate-100 bg-slate-50/50">
            <button
              onClick={fetchHistory}
              disabled={loading}
              className="flex items-center justify-center gap-1.5 w-full py-1.5 text-[10px] text-slate-500 hover:text-slate-700 transition-colors"
            >
              <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
              刷新
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
