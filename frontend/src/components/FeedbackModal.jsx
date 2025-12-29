/**
 * FeedbackModal - 用户反馈（轻量化单页设计 V3 Pro）
 * 
 * 设计理念：
 * - 极简交互：单页展示，减少点击层级
 * - 动态响应：评分后自动展开标签和输入框
 * - 情感化：根据分数高低展示不同文案和标签
 * - 瑞士设计：注重留白、极简排版、无多余装饰
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Send, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { supabase } from '../lib/supabase';
import { getApiUrl } from '../api';

// 标签配置
const TAGS_NEGATIVE = [
  { id: 'content_depth', label: '内容太浅' },
  { id: 'layout_issues', label: '排版混乱' },
  { id: 'speed_slow', label: '生成太慢' },
  { id: 'style_bad', label: '审美一般' },
  { id: 'ocr_error', label: '解析错误' },
];

const TAGS_POSITIVE = [
  { id: 'format_more', label: '想要更多格式' },
  { id: 'style_more', label: '想要更多风格' },
  { id: 'chart_auto', label: '自动生成图表' },
  { id: 'ppt_export', label: '支持导出PPTX' },
  { id: 'image_search', label: '自动配图' },
];

export default function FeedbackModal({ 
  isOpen, 
  onClose, 
  generationId, 
  userId, 
  userEmail, 
  documentName, 
  mandatory = false, 
  onFeedbackComplete = null 
}) {
  const [overallScore, setOverallScore] = useState(0);
  const [hoveredScore, setHoveredScore] = useState(0);
  const [selectedTags, setSelectedTags] = useState([]);
  const [comment, setComment] = useState('');
  
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  // 重置状态
  useEffect(() => {
    if (isOpen) {
      setOverallScore(0);
      setSelectedTags([]);
      setComment('');
      setSubmitted(false);
      setError('');
    }
  }, [isOpen]);

  const handleSubmit = async () => {
    if (overallScore === 0) {
      setError('请轻点星星打个分~');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      const feedbackData = {
        rating: overallScore,
        comment: comment.trim() || null,
        survey_data: {
          tags: selectedTags, // 简化的标签列表
          submitted_at: new Date().toISOString(),
          is_mandatory: mandatory
        }
      };
      
      if (userId) feedbackData.user_id = userId;
      if (generationId) feedbackData.generation_id = generationId;

      const { error: insertError } = await supabase
        .from('feedback')
        .insert(feedbackData);

      if (insertError) {
        console.error('Supabase insert error:', insertError);
        throw insertError;
      }

      // 异步发送通知
      try {
        const tagsDesc = selectedTags
          .map(id => [...TAGS_NEGATIVE, ...TAGS_POSITIVE].find(t => t.id === id)?.label)
          .filter(Boolean)
          .join(', ');

        await fetch(getApiUrl('/api/notify-feedback'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            rating: overallScore,
            comment: comment.trim() || null,
            user_email: userEmail,
            document_name: documentName,
            generation_id: generationId,
            user_id: userId,
            improvements: tagsDesc // 复用 improvements 字段传标签
          })
        });
      } catch (notifyErr) {
        // Ignore
      }

      setSubmitted(true);
      
      const delay = mandatory ? 1500 : 2000;
      setTimeout(() => {
        if (mandatory && onFeedbackComplete) onFeedbackComplete();
        onClose();
      }, delay);

    } catch (err) {
      setError('提交出错了，请重试');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSkip = () => {
    if (!mandatory) onClose();
  };

  const toggleTag = (id) => {
    setSelectedTags(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  // 根据分数决定显示的标签组和文案
  const currentTags = overallScore <= 6 ? TAGS_NEGATIVE : TAGS_POSITIVE;
  const promptText = overallScore === 0 ? "这一刻，您的真实感受？" :
                     overallScore <= 6 ? "抱歉没能让您满意，主要问题是？" :
                     "太棒了！您最期待加入什么新功能？";

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={mandatory ? undefined : handleSkip}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          className="w-full max-w-md bg-white rounded-2xl shadow-2xl overflow-hidden relative"
          onClick={(e) => e.stopPropagation()}
        >
          {/* 装饰背景 - 极简渐变条 */}
          <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-slate-200 via-slate-400 to-slate-200 opacity-50" />
          
          {!mandatory && (
            <button 
              onClick={handleSkip}
              className="absolute top-4 right-4 p-2 text-slate-300 hover:text-slate-600 rounded-full transition-colors z-10"
            >
              <X className="w-4 h-4" />
            </button>
          )}

          {submitted ? (
            <div className="p-12 flex flex-col items-center justify-center text-center">
              <motion.div 
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 200, damping: 10 }}
                className="w-16 h-16 bg-slate-50 text-slate-800 rounded-full flex items-center justify-center mb-6"
              >
                <CheckCircle className="w-6 h-6" />
              </motion.div>
              <h3 className="text-xl font-serif text-slate-800 mb-2 tracking-tight">Thank you.</h3>
              <p className="text-slate-400 text-xs tracking-wider uppercase">Your feedback matters.</p>
            </div>
          ) : (
            <div className="p-8">
              {/* 标题区 - 极简排版 */}
              <div className="text-center mb-10 px-4">
                <h3 className="text-2xl font-serif font-medium text-slate-800 mb-4 tracking-tight" style={{ textWrap: 'balance' }}>
                  {overallScore === 0 ? "这一刻，您的真实感受？" : promptText}
                </h3>
                <div className="text-xs text-slate-400 font-light tracking-wide leading-relaxed mx-auto max-w-sm">
                  {overallScore === 0 ? (
                    <>
                      <p>如您所见，我们离完美还有距离。</p>
                      <p className="mt-1">您的每一条建议，都在缩短这段路程。</p>
                    </>
                  ) : (
                    <span className="opacity-0 animate-fade-in transition-opacity duration-500 delay-200">
                      您的反馈是我们最珍贵的礼物
                    </span>
                  )}
                </div>
              </div>

              {/* 评分条 - 极简数字 */}
              <div className="flex justify-center items-center gap-1 mb-10">
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((score) => (
                  <button
                    key={score}
                    onClick={() => setOverallScore(score)}
                    onMouseEnter={() => setHoveredScore(score)}
                    onMouseLeave={() => setHoveredScore(0)}
                    className={`
                      w-9 h-12 flex items-center justify-center
                      font-serif text-lg transition-all duration-300 relative group
                    `}
                  >
                    {/* 背景色块 */}
                    <span className={`
                      absolute inset-0 rounded-lg transition-all duration-300 opacity-20
                      ${score <= (hoveredScore || overallScore)
                        ? score <= 6 ? 'bg-orange-500 scale-100' : 'bg-indigo-500 scale-100'
                        : 'bg-slate-200 scale-75 group-hover:scale-100'
                      }
                    `} />
                    
                    {/* 数字 */}
                    <span className={`
                      relative z-10 transition-colors duration-300
                      ${score <= (hoveredScore || overallScore)
                        ? score <= 6 ? 'text-orange-900 font-bold' : 'text-indigo-900 font-bold'
                        : 'text-slate-400 group-hover:text-slate-600'
                      }
                    `}>
                      {score}
                    </span>
                    
                    {/* 底部指示点 (仅选中时显示) */}
                    {score === overallScore && (
                      <motion.div 
                        layoutId="active-dot"
                        className={`absolute -bottom-2 w-1 h-1 rounded-full ${score <= 6 ? 'bg-orange-500' : 'bg-indigo-500'}`}
                      />
                    )}
                  </button>
                ))}
              </div>

              {/* 动态展开区域 */}
              <AnimatePresence>
                {overallScore > 0 && (
                  <motion.div
                    initial={{ opacity: 0, height: 0, y: 10 }}
                    animate={{ opacity: 1, height: 'auto', y: 0 }}
                    exit={{ opacity: 0, height: 0, y: 10 }}
                    transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }} 
                    className="overflow-hidden"
                  >
                    {/* 标签云 - 极简胶囊 */}
                    <div className="flex flex-wrap gap-2 justify-center mb-8 px-4">
                      {currentTags.map(tag => (
                        <button
                          key={tag.id}
                          onClick={() => toggleTag(tag.id)}
                          className={`
                            px-4 py-1.5 text-xs tracking-wider transition-all duration-300
                            ${selectedTags.includes(tag.id)
                              ? 'bg-slate-900 text-white shadow-lg shadow-slate-200'
                              : 'bg-transparent text-slate-500 border border-slate-200 hover:border-slate-400'
                            }
                          `}
                          style={{ borderRadius: '2px' }}
                        >
                          {tag.label}
                        </button>
                      ))}
                    </div>

                    {/* 文本框 - 极简线条 */}
                    <div className="relative mb-8 mx-4">
                      <textarea
                        value={comment}
                        onChange={(e) => setComment(e.target.value)}
                        placeholder="在这里写下您的想法..."
                        className="w-full p-0 bg-transparent border-0 border-b border-slate-200 text-sm focus:ring-0 focus:border-slate-800 transition-all resize-none placeholder:text-slate-300 placeholder:font-light leading-relaxed min-h-[80px]"
                      />
                    </div>

                    {/* 提交按钮 - 黑色方块 */}
                    <div className="px-4">
                      <button
                        onClick={handleSubmit}
                        disabled={submitting}
                        className="w-full py-4 bg-slate-900 text-white text-xs font-bold tracking-widest hover:bg-black transition-all flex items-center justify-center gap-2 uppercase"
                      >
                        {submitting ? (
                          <Loader2 className="w-3 h-3 animate-spin" />
                        ) : (
                          <>
                            <span className="mr-1">Submit Feedback</span>
                            <Send className="w-3 h-3" />
                          </>
                        )}
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* 隐私提示 */}
              {!overallScore && (
                <p className="text-center text-[10px] text-slate-300 mt-12 tracking-widest opacity-50 uppercase">
                  Feedback for Product Improvement
                </p>
              )}
            </div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
