/**
 * App.jsx - 应用主入口
 *
 * @input:  components/, contexts/AuthContext, api.js
 * @output: App组件, MainApp组件（包含完整的用户界面和状态管理）
 * @pos:    前端应用的根组件，协调所有子组件和全局状态
 *
 * ⚠️ 一旦我被更新，务必更新：
 *    1. 我的头部注释
 *    2. /frontend/src/_FOLDER.md
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Loader2, AlertCircle, Layout, ChevronLeft, ChevronRight, LogOut, User, ChevronDown } from 'lucide-react';
import Hero from './components/Hero';
import UploadZone from './components/UploadZone';
import ScenarioSelector from './components/ScenarioSelector';
import ConfigPanel from './components/ConfigPanel';
import ResultView from './components/ResultView';
import HistoryOutputSelector from './components/HistoryOutputSelector';
import UserHistoryPanel from './components/UserHistoryPanel';
import AuthPage from './components/AuthPage';
import { useAuth } from './contexts/AuthContext';
import { fetchScenarios, uploadFile, generatePresentationStream, checkAdminStatus } from './api';

function App() {
  const { user, profile, loading: authLoading, logout, isAuthenticated, canGenerate, quotaRemaining, trackGeneration, refreshProfile } = useAuth();
  
  // 如果正在检查认证状态，显示加载
  if (authLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-slate-400" />
          <span className="text-slate-500">加载中...</span>
        </div>
      </div>
    );
  }

  // 如果未登录，显示登录页
  if (!isAuthenticated) {
    return <AuthPage />;
  }

  // 已登录，显示主应用
  return <MainApp user={user} profile={profile} onLogout={logout} canGenerate={canGenerate} quotaRemaining={quotaRemaining} trackGeneration={trackGeneration} />;
}

function MainApp({ user, profile, onLogout, canGenerate, quotaRemaining, trackGeneration }) {
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState('consulting');
  const [selectedFile, setSelectedFile] = useState(null);
  const [showUserMenu, setShowUserMenu] = useState(false);

  const [config, setConfig] = useState({
    organization: "",
    target_pages: 20,
    content_depth: "normal",
    font_style: "modern",  // 'modern' (黑体) 或 'classic' (楷体)
    skip_pdf: false,
    skip_pptx: false
  });

  // App State
  const [customColor, setCustomColor] = useState(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false); // 侧边栏折叠状态

  // Real-time Data
  const [status, setStatus] = useState('idle'); // idle, generating, preview
  const [errorMsg, setErrorMsg] = useState('');
  const [progress, setProgress] = useState(0);
  const [progressStage, setProgressStage] = useState('');
  const [progressMessage, setProgressMessage] = useState('');
  const [outlineData, setOutlineData] = useState([]);
  const [previewData, setPreviewData] = useState(null);
  const [downloads, setDownloads] = useState({ html: null, pdf: null, pptx: null });
  const [currentGenerationId, setCurrentGenerationId] = useState(null); // 当前生成记录的 ID，用于反馈关联

  // 🔐 管理员状态
  const [isAdmin, setIsAdmin] = useState(false);
  const [adminModels, setAdminModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState(null); // null = 使用默认模型

  useEffect(() => {
    loadData();
  }, []);

  // 🔐 检查管理员权限
  useEffect(() => {
    const checkAdmin = async () => {
      if (user?.email) {
        console.log('🔐 Checking admin status for:', user.email);
        const adminData = await checkAdminStatus(user.email);
        console.log('🔐 Admin check result:', adminData);
        setIsAdmin(adminData.is_admin);
        setAdminModels(adminData.models || []);
        if (!adminData.is_admin) {
          setSelectedModel(null); // 非管理员重置模型选择
        }
      } else {
        console.log('🔐 No user email, skipping admin check');
        setIsAdmin(false);
        setAdminModels([]);
        setSelectedModel(null);
      }
    };
    checkAdmin();
  }, [user?.email]);

  const loadData = async () => {
    try {
      const data = await fetchScenarios();
      setScenarios(data);
      // Ensure we select the first one with full data if needed
      if (data.length > 0 && !selectedScenario) setSelectedScenario(data[0].id);
    } catch (e) {
      console.error(e);
      setScenarios([
        { "id": "consulting", "name": "咨询研究/Consulting", "color": "#003366" },
        { "id": "annual_review", "name": "年终总结/Annual Review", "color": "#8B0000" },
      ]);
    }
  };

  const activeScenarioData = scenarios.find(s => s.id === selectedScenario);

  const handleUpload = async (file) => {
    await uploadFile(file, user?.email, user?.id);
  };

  // 加载历史输出
  const handleLoadHistory = (result, output) => {
    console.log('Loading history output:', output.name);
    setPreviewData(result);
    setDownloads(result.downloads || { html: null, pdf: null, pptx: null });
    setStatus('preview');
    setProgress(100);
    setProgressMessage(`已加载: ${output.display_name}`);
  };

  const handleGenerate = async () => {
    if (!selectedFile) return;
    
    // Check quota
    if (!canGenerate) {
      setErrorMsg('您的免费额度已用完，请联系管理员升级账户');
      return;
    }

    // Reset State
    setStatus('generating');
    setErrorMsg('');
    setProgress(0);
    setProgressStage('context');
    setOutlineData([]);
    setPreviewData(null);
    setDownloads({ html: null, pdf: null, pptx: null });

    try {
      await generatePresentationStream(
        {
          document_name: selectedFile.name,
          scenario: selectedScenario,
          theme_color: customColor, // Pass custom color if set
          ...config,
          // 🔐 管理员专用：自定义模型
          model: isAdmin ? selectedModel : null,
          user_email: user?.email
        },
        async (event) => {
          console.log('Event:', event);
          setProgress(event.progress);
          setProgressStage(event.stage);
          setProgressMessage(event.message);

          if (event.stage === 'outline' && event.result?.outline) {
            setOutlineData(event.result.outline);
          }

          if (event.stage === 'preview_ready') {
            setPreviewData(event.result);
            setDownloads(prev => ({ ...prev, html: event.result.html }));
            setStatus('preview');
          }

          if (event.stage === 'pdf_ready') {
            setDownloads(prev => ({ ...prev, pdf: event.result.pdf }));
          }

          if (event.stage === 'pptx_ready') {
            setDownloads(prev => ({ ...prev, pptx: event.result.pptx }));
          }

          if (event.stage === 'done') {
            setDownloads(event.result.downloads);
            // Track successful generation with output path
            // 优先使用 output_dir（纯目录名），否则回退到 html 路径
            const outputPath = event.result.output_dir || event.result.downloads?.html;
            const genId = await trackGeneration({
              scenario: selectedScenario,
              document_name: selectedFile.name,
              output_path: outputPath,
              // 配置信息
              theme_color: customColor || activeScenarioData?.color || null,
              font_style: config.font_style,
              target_pages: config.target_pages,
              content_depth: config.content_depth,
              organization: config.organization || null,
              // 实际生成结果
              output_dir: event.result.output_dir || null,
              actual_pages: event.result.pages_count || event.result.pages?.length || 0
            });
            setCurrentGenerationId(genId); // 保存生成记录 ID，用于反馈
          }
        }
      );
    } catch (e) {
      console.error(e);
      if (status !== 'preview') {
        setStatus('idle');
        setErrorMsg(e.message || "生成失败，请检查服务");
      }
    }
  };

  return (
    <div className="flex h-screen w-full bg-slate-50 text-slate-900 font-sans overflow-hidden">

      {/* LEFT SIDEBAR */}
      <div
        className={`flex-shrink-0 bg-white border-r border-slate-200 h-full flex flex-col z-20 shadow-sm transition-all duration-300 ease-in-out relative ${sidebarCollapsed ? 'w-0 opacity-0 overflow-hidden' : 'w-[380px]'
          }`}
      >
        <div className="px-6 py-4 flex-1 overflow-y-auto custom-scrollbar">
          {/* User Info Bar */}
          <div className="relative mb-4 pb-3 border-b border-slate-100">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="w-full flex items-center justify-between p-2 rounded-lg hover:bg-slate-50 transition-colors"
            >
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-slate-900 flex items-center justify-center">
                  <User className="w-4 h-4 text-white" />
                </div>
                <div className="flex flex-col items-start">
                  <span className="text-xs font-medium text-slate-700 truncate max-w-[160px]">
                    {user?.email || '用户'}
                  </span>
                  {profile ? (
                    <span className={`text-[10px] ${canGenerate ? 'text-emerald-500' : 'text-red-500'}`}>
                      剩余 {quotaRemaining}/{profile.generation_quota} 次
                    </span>
                  ) : (
                    <span className="text-[10px] text-slate-400">加载中...</span>
                  )}
                </div>
              </div>
              <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${showUserMenu ? 'rotate-180' : ''}`} />
            </button>
            
            {/* User Dropdown Menu */}
            {showUserMenu && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 rounded-lg shadow-lg z-50 overflow-hidden animate-in fade-in zoom-in-95 duration-200 origin-top">
                {/* Contact for Upgrade */}
                <div className="px-4 py-3 border-b border-slate-100 bg-slate-50/80">
                  <div className="flex items-center gap-2 mb-2.5">
                    <span className="text-xs font-bold text-slate-800">🚀 升级额度 / 技术支持</span>
                  </div>
                  <div className="space-y-2">
                    {/* WeChat */}
                    <div className="flex items-center justify-between p-2.5 bg-white rounded-lg border border-slate-200 shadow-sm group hover:border-blue-400 hover:shadow-md transition-all">
                      <div className="flex items-center gap-2.5">
                        <span className="w-5 h-5 flex items-center justify-center bg-[#07C160]/10 text-[#07C160] rounded-sm">
                          <svg viewBox="0 0 24 24" fill="currentColor" className="w-3.5 h-3.5"><path d="M8.7 15.3l-.4 2.1 1.7-1.1c.5.2 1 .2 1.5.2 3.6 0 6.5-2.6 6.5-5.8 0-3.2-2.9-5.8-6.5-5.8-3.6 0-6.5 2.6-6.5 5.8 0 1.9 1 3.6 2.6 4.7 0 .1-.1.4-.9 1.6 1.4-.2 2.7-.8 2.7-.8zM20.2 12c.5 0 .9 0 1.4.1.2-2.5-1.7-4.6-4.9-4.6-4.1 0-7.3 3-7.3 6.9 0 .5.1.9.2 1.4 1.1-.9 2.5-1.4 4.1-1.4 3.6 0 6.5 2.7 6.5 6 0 1-.3 2-.8 2.8 1.9-.3 3.6-1.5 3.6-3.8 0-1.2-.5-2.3-1.4-3.1.5-.7 1.5-2.6 1.5-2.6-1.9.3-3.1 1.1-3.1 1.1.1-.3.2-.5.2-.8z"/></svg>
                        </span>
                        <div>
                          <div className="text-[10px] text-slate-400 leading-none mb-0.5">微信 (点击复制)</div>
                          <div className="text-xs font-mono font-medium text-slate-700 select-all cursor-text hover:text-blue-600">liusai0820</div>
                        </div>
                      </div>
                    </div>
                    
                    {/* Email */}
                    <div className="flex items-center justify-between p-2.5 bg-white rounded-lg border border-slate-200 shadow-sm group hover:border-blue-400 hover:shadow-md transition-all">
                      <div className="flex items-center gap-2.5">
                         <span className="w-5 h-5 flex items-center justify-center bg-blue-50 text-blue-500 rounded-sm">
                           <span className="text-xs font-bold">@</span>
                         </span>
                        <div>
                          <div className="text-[10px] text-slate-400 leading-none mb-0.5">邮箱</div>
                          <div className="text-xs font-mono font-medium text-slate-700 select-all cursor-text hover:text-blue-600">liusai64@gmail.com</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="p-1.5">
                  <button
                    onClick={() => {
                      setShowUserMenu(false);
                      onLogout();
                    }}
                    className="w-full flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-md transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    <span>退出登录</span>
                  </button>
                </div>
              </div>
            )}
          </div>

          <Hero />

          <div className="space-y-5">
            {/* 用户历史记录 */}
            <UserHistoryPanel
              userId={user?.id}
              onLoad={handleLoadHistory}
              isLoading={status === 'generating'}
            />

            <Section title="上传文档" step="1">
              <UploadZone
                selectedFile={selectedFile}
                onFileSelect={setSelectedFile}
                onUpload={handleUpload}
              />
              {/* 历史输出选择器 - 仅开发模式显示 */}
              {import.meta.env.DEV && (
                <div className="mt-2">
                  <HistoryOutputSelector
                    onLoad={handleLoadHistory}
                    isLoading={status === 'generating'}
                  />
                </div>
              )}
            </Section>

            <Section title="选择场景" step="2">
              <ScenarioSelector
                scenarios={scenarios}
                selected={selectedScenario}
                onSelect={setSelectedScenario}
                customColor={customColor}
                onColorChange={setCustomColor}
              />
            </Section>

            <Section title="生成设置" step="3">
              <ConfigPanel config={config} onChange={setConfig} />
            </Section>

            {/* 🔐 管理员面板 - 仅对管理员可见 */}
            {isAdmin && (
              <Section title="🔐 管理员" step="★">
                <div className="bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-lg p-3">
                  <label className="block text-xs font-medium text-purple-700 mb-2">
                    AI 模型选择
                  </label>
                  <select
                    value={selectedModel || ''}
                    onChange={(e) => setSelectedModel(e.target.value || null)}
                    className="w-full px-3 py-2 text-sm border border-purple-200 rounded-md bg-white focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                  >
                    <option value="">默认 (使用配置文件模型)</option>
                    {adminModels.map(model => (
                      <option key={model.id} value={model.id}>
                        {model.name}
                      </option>
                    ))}
                  </select>
                  <p className="text-[10px] text-purple-500 mt-1.5">
                    ⚡ Pro 模型生成质量更高，但速度较慢
                  </p>
                </div>
              </Section>
            )}
          </div>
        </div>

        {/* Generate Button */}
        <div className="px-5 py-3 border-t border-slate-100 bg-white/90 backdrop-blur-md z-10">
          {!canGenerate && (
            <div className="mb-3 p-3 bg-amber-50 border border-amber-200 rounded-lg">
              <p className="text-xs text-amber-700 font-medium">🔒 免费额度已用完</p>
              <p className="text-[10px] text-amber-600 mt-1">请联系管理员升级账户以继续使用</p>
            </div>
          )}
          <button
            onClick={handleGenerate}
            disabled={!selectedFile || !canGenerate || (status === 'generating' && !previewData)}
            className={`
              w-full py-3 px-5 rounded-lg font-bold text-sm flex items-center justify-center gap-2 transition-all duration-300
              ${!selectedFile || !canGenerate || (status === 'generating' && !previewData)
                ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                : 'bg-slate-900 text-white hover:bg-slate-800 hover:shadow-lg hover:-translate-y-0.5 active:translate-y-0 shadow-md'}
            `}
          >
            {status === 'generating' && !previewData ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>AI 正在思考...</span>
              </>
            ) : status === 'preview' ? (
              <>
                <Sparkles className="w-4 h-4" />
                <span>重新生成</span>
              </>
            ) : !canGenerate ? (
              <span>额度已用完</span>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>开始生成</span>
              </>
            )}
          </button>

          {errorMsg && (
            <div className="mt-3 flex items-start gap-2 text-xs text-red-600 bg-red-50 p-2.5 rounded-lg border border-red-100">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
              <span className="leading-tight">{errorMsg}</span>
            </div>
          )}
        </div>
      </div>

      {/* Sidebar Toggle Button */}
      <button
        onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
        className={`
          absolute top-1/2 -translate-y-1/2 z-30 w-6 h-16 bg-white border border-slate-200 
          rounded-r-lg shadow-md flex items-center justify-center hover:bg-slate-50 
          transition-all duration-300 group
          ${sidebarCollapsed ? 'left-0' : 'left-[376px]'}
        `}
        title={sidebarCollapsed ? '展开侧边栏' : '折叠侧边栏'}
      >
        {sidebarCollapsed ? (
          <ChevronRight className="w-4 h-4 text-slate-400 group-hover:text-slate-600" />
        ) : (
          <ChevronLeft className="w-4 h-4 text-slate-400 group-hover:text-slate-600" />
        )}
      </button>

      {/* RIGHT MAIN AREA */}
      <div className="flex-1 h-full bg-slate-100 relative overflow-hidden">
        <AnimatePresence mode="wait">

          {/* IDLE: Dynamic Theme Preview */}
          {status === 'idle' && (
            <motion.div
              key="idle"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="w-full h-full flex flex-col items-center justify-center p-12 bg-slate-50 relative overflow-hidden"
            >
              <div className="absolute inset-0 bg-dot-pattern opacity-[0.05]" />

              {activeScenarioData && (
                <div className="relative z-10 flex flex-col items-center gap-8 w-full max-w-4xl">
                  <div className="text-center space-y-2">
                    <h3 className="text-2xl font-bold text-slate-900 tracking-tight">预览您的演示风格</h3>
                    <p className="text-slate-500">
                      AI 将基于「{activeScenarioData.name.split('/')[0]}」场景为您定制内容
                    </p>
                  </div>

                  {/* CSS-based Theme Preview Card */}
                  <ThemePreviewCard
                    color={customColor || activeScenarioData.color || '#000'}
                    scenario={activeScenarioData}
                  />
                </div>
              )}
            </motion.div>
          )}

          {/* GENERATING */}
          {status === 'generating' && !previewData && (
            <motion.div
              key="generating"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0, x: -50 }}
              className="w-full h-full flex flex-col items-center justify-center p-8 relative"
            >
              <div className="w-full max-w-2xl space-y-12 text-center z-10">
                <div className="space-y-4">
                  <div className="text-7xl font-bold text-slate-900 tracking-tighter tabular-nums">
                    {Math.round(progress)}%
                  </div>
                  <div className="text-lg text-slate-500 font-medium animate-pulse flex items-center justify-center gap-2">
                    {progressMessage}
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="h-1.5 w-full bg-slate-200 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-slate-900"
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ ease: "easeOut" }}
                  />
                </div>

                {/* Outline Preview Grid (If Ready) */}
                {outlineData.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-12 w-full text-left"
                  >
                    <div className="flex items-center justify-between mb-4 px-1">
                      <span className="text-sm font-semibold text-slate-500 uppercase tracking-widest">
                        生成大纲 ({outlineData.length}页)
                      </span>
                      <span className="text-xs text-slate-400 bg-white px-2 py-1 rounded-full border border-slate-100 shadow-sm">
                        正在细化内容...
                      </span>
                    </div>

                    <div className="grid grid-cols-4 gap-4 max-h-[400px] overflow-y-auto custom-scrollbar p-1">
                      {outlineData.map((page, i) => (
                        <div
                          key={i}
                          className="aspect-video bg-white rounded-lg border border-slate-200 p-3 shadow-sm flex flex-col justify-between group hover:border-blue-400 transition-colors"
                        >
                          <div className="space-y-1.5 opacity-40">
                            <div className="h-2 w-2/3 bg-slate-200 rounded-sm" />
                            <div className="space-y-1">
                              <div className="h-1 w-full bg-slate-100 rounded-sm" />
                              <div className="h-1 w-full bg-slate-100 rounded-sm" />
                              <div className="h-1 w-5/6 bg-slate-100 rounded-sm" />
                            </div>
                          </div>
                          <div className="flex items-end justify-between gap-2">
                            <span className="font-medium text-[10px] leading-tight text-slate-700 line-clamp-2">
                              {page.title}
                            </span>
                            <span className="text-[10px] font-mono text-slate-300 shrink-0">
                              {i + 1}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </div>
            </motion.div>
          )}

          {/* PREVIEW */}
          {status === 'preview' && previewData && (
            <motion.div
              key="preview"
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              className="w-full h-full"
            >
              <ResultView
                result={previewData}
                downloads={downloads}
                isProcessing={progress < 100}
                generationId={currentGenerationId}
                documentName={selectedFile?.name}
              />
            </motion.div>
          )}

        </AnimatePresence>
      </div>
    </div>
  );
}

function Section({ title, step, children }) {
  return (
    <section>
      <div className="flex items-center gap-2 mb-2">
        <div className="flex items-center justify-center w-5 h-5 rounded bg-slate-100 text-slate-600 text-[10px] font-bold font-mono border border-slate-200">{step}</div>
        <h3 className="font-semibold text-sm text-slate-800">{title}</h3>
      </div>
      {children}
    </section>
  )
}

// Custom Component to render style guide metadata nicely
function StyleGuideInfo({ data }) {
  if (!data) return null;
  const { description, tags, colors } = data;

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl p-6 shadow-sm border border-slate-100 w-full flex flex-col md:flex-row gap-8 items-start"
    >
      <div className="flex-1 space-y-4">
        <div>
          <h4 className="font-semibold text-slate-900 mb-2">风格简介</h4>
          <p className="text-sm text-slate-500 leading-relaxed">{description || "暂无描述"}</p>
        </div>

        {tags && tags.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {tags.map((tag, i) => (
              <span key={i} className="px-2.5 py-1 bg-slate-50 text-slate-600 text-xs rounded-md border border-slate-100 font-medium">
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {colors && colors.length > 0 && (
        <div className="min-w-[200px] space-y-3">
          <h4 className="font-semibold text-slate-900 text-sm">主题配色</h4>
          <div className="flex flex-wrap gap-3">
            {colors.map((c, i) => (
              <div key={i} className="flex flex-col items-center gap-1.5 group cursor-pointer relative">
                <div
                  className="w-10 h-10 rounded-lg shadow-sm border border-slate-100 ring-2 ring-transparent group-hover:ring-slate-200 transition-all"
                  style={{ background: c.color }}
                />
                <span className="text-[10px] text-slate-400 font-mono uppercase">{c.label}</span>

                {/* Tooltip */}
                <div className="absolute -top-8 left-1/2 -translate-x-1/2 bg-slate-800 text-white text-[10px] py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                  {c.color}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}

// Dynamic Theme Preview loading actual HTML templates
function ThemePreviewCard({ color, scenario }) {
  const [htmlContent, setHtmlContent] = useState('');
  const [metaData, setMetaData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(0);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    const fetchTemplate = async () => {
      setLoading(true);
      try {
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8005/api';
        const baseUrl = apiUrl.replace('/api', '');

        // Add timestamp to prevent caching of preview templates
        const res = await fetch(`${baseUrl}/previews/${scenario.id}.html?t=${new Date().getTime()}`);
        if (res.ok) {
          const text = await res.text();

          const parser = new DOMParser();
          const doc = parser.parseFromString(text, 'text/html');
          const styles = doc.head.innerHTML;

          // --- Metadata Extraction ---
          let extracted = { description: '', tags: [], colors: [] };
          const header = doc.querySelector('.preview-header, .style-guide-container, header, .intro-section');

          if (header) {
            // Describe
            const pTags = header.querySelectorAll('p');
            pTags.forEach(p => {
              const t = p.textContent;
              if (t.includes('分类') || t.includes('标签')) {
                // Extract tags
                // Format: 分类: xx | 标签: a, b, c
                const tagPart = t.split('标签:')[1] || t.split('Tags:')[1];
                if (tagPart) {
                  extracted.tags = tagPart.split(/,|，/).map(s => s.trim()).filter(Boolean);
                }
              } else {
                // Assume description (if long enough)
                if (t.length > 10) extracted.description = t;
              }
            });

            // Colors
            const swatches = header.querySelectorAll('.color-swatch');
            swatches.forEach(s => {
              extracted.colors.push({
                label: s.innerText.trim(),
                color: s.style.backgroundColor || s.style.background
              });
            });
          }

          // Fallback for description if not found in header
          if (!extracted.description && scenario.description) {
            extracted.description = scenario.description;
          }

          setMetaData(extracted);

          // --- Slide Extraction ---
          const slides = doc.querySelectorAll('.slide-container');
          const slidesHTML = Array.from(slides).map(s => s.outerHTML).join('\n');

          if (slides.length > 0) {
            setTotalPages(slides.length);
            setPage(0);

            // Inject script for auto-scaling
            const autoScaleScript = `
                            <script>
                                function resize() {
                                    const width = window.innerWidth;
                                    const scale = width / 1280;
                                    document.body.style.transform = 'scale(' + scale + ')';
                                    document.body.style.transformOrigin = 'top left';
                                    document.body.style.height = (720 * scale) + 'px';
                                }
                                window.addEventListener('resize', resize);
                                window.addEventListener('DOMContentLoaded', resize);
                                setTimeout(resize, 0);
                            </script>
                        `;

            const cleanHtml = `
                            <!DOCTYPE html>
                            <html>
                            <head>${styles}</head>
                            <body>
                                ${slidesHTML}
                                ${autoScaleScript}
                            </body>
                            </html>
                        `;
            setHtmlContent(cleanHtml);
          } else {
            setHtmlContent(text);
            setTotalPages(1);
          }
        } else {
          console.error("Preview template not found for:", scenario.id);
          setHtmlContent('');
        }
      } catch (e) {
        console.error("Failed to fetch preview:", e);
      } finally {
        setLoading(false);
      }
    };
    fetchTemplate();
  }, [scenario.id]);

  const srcDoc = React.useMemo(() => {
    if (!htmlContent) return null;

    const injectedStyle = `
            <style>
                :root {
                    --primary: ${color} !important;
                    --primary-color: ${color} !important;
                    --theme-color: ${color} !important;
                    --brand: ${color} !important;
                    --accent: ${color} !important;
                }
                body { 
                    overflow: hidden; 
                    margin: 0;
                    padding: 0;
                    width: 1280px;
                    height: 720px;
                    position: relative;
                }
                
                /* Reset slide positioning to ensure they stack perfectly at 0,0 */
                .slide-container { 
                    display: none !important; 
                    position: absolute !important;
                    top: 0 !important;
                    left: 0 !important;
                    margin: 0 !important;
                    transform: none !important; /* Remove any internal transforms */
                }
                
                .slide-container:nth-of-type(${page + 1}) { display: flex !important; }
            </style>
        `;
    return htmlContent.replace('</head>', `${injectedStyle}</head>`);
  }, [htmlContent, color, page]);

  const handlePrev = (e) => {
    e.stopPropagation();
    setPage(p => Math.max(0, p - 1));
  };

  const handleNext = (e) => {
    e.stopPropagation();
    setPage(p => Math.min(totalPages - 1, p + 1));
  };

  return (
    <div className="w-full flex flex-col gap-6">
      <StyleGuideInfo data={metaData} />

      {/* Preview Card */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        key={scenario.id}
        className="w-full aspect-video bg-white rounded-xl shadow-2xl overflow-hidden relative border border-slate-200 flex items-center justify-center group"
      >
        {loading ? (
          <div className="flex flex-col items-center gap-3 text-slate-400">
            <Loader2 className="w-8 h-8 animate-spin" />
            <span className="text-sm">正在加载真实模版...</span>
          </div>
        ) : srcDoc ? (
          <div className="w-full h-full relative">
            <div className="absolute inset-0 z-20 flex items-center justify-between px-4 pointer-events-none group-hover:pointer-events-auto opacity-0 group-hover:opacity-100 transition-opacity">
              <button
                onClick={handlePrev}
                disabled={page === 0}
                className="p-2 rounded-full bg-slate-900/10 hover:bg-slate-900/80 hover:text-white backdrop-blur-sm text-slate-700 transition-all disabled:opacity-0 pointer-events-auto"
              >
                <ChevronLeft className="w-6 h-6" />
              </button>

              <button
                onClick={handleNext}
                disabled={page === totalPages - 1}
                className="p-2 rounded-full bg-slate-900/10 hover:bg-slate-900/80 hover:text-white backdrop-blur-sm text-slate-700 transition-all disabled:opacity-0 pointer-events-auto"
              >
                <ChevronRight className="w-6 h-6" />
              </button>
            </div>

            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-20 px-3 py-1 bg-black/50 backdrop-blur-md rounded-full text-white text-[10px] font-mono opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
              {page + 1} / {totalPages}
            </div>

            <iframe
              srcDoc={srcDoc}
              className="w-full h-full border-0 pointer-events-none"
              title="Theme Output Preview"
            />
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2 text-slate-400 p-8 text-center bg-slate-50 w-full h-full justify-center">
            <Layout className="w-10 h-10 mb-2 opacity-50" />
            <p>暂无该场景的实时预览</p>
          </div>
        )}
      </motion.div>
    </div>
  );
}

export default App;
