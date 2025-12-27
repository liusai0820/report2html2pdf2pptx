/**
 * FeedbackModal - 生成完成后的用户反馈弹窗
 * 
 * @input:  isOpen, onClose, generationId, userId, userEmail, documentName
 * @output: 用户评分和评论提交到 Supabase，并发送 Telegram 通知
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Star, X, Send, Loader2, MessageSquare, CheckCircle, Heart, Lightbulb } from 'lucide-react';
import { supabase } from '../lib/supabase';
import { getApiUrl } from '../api';

export default function FeedbackModal({ isOpen, onClose, generationId, userId, userEmail, documentName }) {
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    if (rating === 0) {
      setError('请先选择评分');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      // 1. 保存到 Supabase
      const { error: insertError } = await supabase
        .from('feedback')
        .insert({
          user_id: userId,
          generation_id: generationId,
          rating: rating,
          comment: comment.trim() || null,
        });

      if (insertError) throw insertError;

      // 2. 发送 Telegram 通知
      try {
        await fetch(getApiUrl('/api/notify-feedback'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            rating,
            comment: comment.trim() || null,
            user_email: userEmail,
            document_name: documentName,
            generation_id: generationId,
            user_id: userId
          })
        });
      } catch (notifyErr) {
        console.error('Telegram notification failed:', notifyErr);
        // 不影响主流程
      }

      setSubmitted(true);
      setTimeout(() => {
        onClose();
        // 重置状态
        setRating(0);
        setComment('');
        setSubmitted(false);
      }, 1500);
    } catch (err) {
      console.error('Feedback submission error:', err);
      setError('提交失败，请稍后重试');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSkip = () => {
    onClose();
    setRating(0);
    setComment('');
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={handleSkip}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          onClick={(e) => e.stopPropagation()}
          className="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden"
        >
          {/* Header */}
          <div className="px-6 pt-6 pb-4 bg-gradient-to-r from-amber-50 to-orange-50 border-b border-amber-100">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-amber-400 to-orange-500 rounded-xl flex items-center justify-center shadow-lg shadow-orange-200">
                  <Heart className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 text-lg">您觉得效果如何？</h3>
                  <p className="text-sm text-slate-600">您的反馈是产品进步的最大动力</p>
                </div>
              </div>
              <button
                onClick={handleSkip}
                className="p-2 text-slate-400 hover:text-slate-600 hover:bg-white/80 rounded-lg transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 space-y-5">
            {submitted ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex flex-col items-center py-8"
              >
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                  <CheckCircle className="w-8 h-8 text-green-600" />
                </div>
                <p className="text-lg font-medium text-slate-900">感谢您的宝贵反馈！</p>
                <p className="text-sm text-slate-500 mt-1">我们会认真倾听每一条建议 ❤️</p>
              </motion.div>
            ) : (
              <>
                {/* Star Rating */}
                <div className="flex flex-col items-center">
                  <div className="flex gap-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        onMouseEnter={() => setHoveredRating(star)}
                        onMouseLeave={() => setHoveredRating(0)}
                        onClick={() => setRating(star)}
                        className="p-1 transition-transform hover:scale-110 active:scale-95"
                      >
                        <Star
                          className={`w-11 h-11 transition-all duration-200 ${
                            star <= (hoveredRating || rating)
                              ? 'text-amber-400 fill-amber-400 drop-shadow-md'
                              : 'text-slate-200'
                          }`}
                        />
                      </button>
                    ))}
                  </div>
                  <p className="text-sm text-slate-500 mt-3 h-5">
                    {rating === 0 && '点击星星评分'}
                    {rating === 1 && '😞 很差 - 我们会努力改进'}
                    {rating === 2 && '😐 一般 - 还有提升空间'}
                    {rating === 3 && '🙂 还行 - 基本满足需求'}
                    {rating === 4 && '😊 不错 - 超出预期'}
                    {rating === 5 && '🤩 非常棒！感谢认可'}
                  </p>
                </div>

                {/* Encouragement Banner */}
                <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 flex items-start gap-3">
                  <Lightbulb className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-blue-900">您的建议对我们极为重要！</p>
                    <p className="text-xs text-blue-700 mt-1">
                      无论是功能改进、Bug 反馈还是使用体验，我们都会认真阅读并持续优化产品。
                    </p>
                  </div>
                </div>

                {/* Comment (Optional but Encouraged) */}
                <div className="space-y-2">
                  <label className="text-sm font-medium text-slate-700 flex items-center gap-2">
                    <MessageSquare className="w-4 h-4 text-slate-500" />
                    详细反馈
                    <span className="text-xs font-normal text-slate-400">（选填，但非常欢迎）</span>
                  </label>
                  <textarea
                    value={comment}
                    onChange={(e) => setComment(e.target.value)}
                    placeholder="例如：&#10;• 生成的内容是否符合预期？&#10;• 有什么功能希望我们添加？&#10;• 遇到了什么问题或困难？"
                    rows={4}
                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl text-sm resize-none focus:outline-none focus:border-blue-400 focus:ring-2 focus:ring-blue-100 transition-all placeholder:text-slate-400"
                  />
                </div>

                {/* Error */}
                {error && (
                  <p className="text-sm text-red-600 text-center bg-red-50 py-2 px-3 rounded-lg">{error}</p>
                )}
              </>
            )}
          </div>

          {/* Footer */}
          {!submitted && (
            <div className="px-6 pb-6 flex gap-3">
              <button
                onClick={handleSkip}
                className="flex-1 py-3 px-4 text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-xl text-sm font-medium transition-colors"
              >
                稍后再说
              </button>
              <button
                onClick={handleSubmit}
                disabled={submitting || rating === 0}
                className="flex-1 py-3 px-4 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl text-sm font-bold flex items-center justify-center gap-2 hover:from-amber-600 hover:to-orange-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-orange-200 disabled:shadow-none"
              >
                {submitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>提交中...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>提交反馈</span>
                  </>
                )}
              </button>
            </div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
