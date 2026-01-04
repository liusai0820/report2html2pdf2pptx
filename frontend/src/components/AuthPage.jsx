import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Mail, Lock, Loader2, AlertCircle, Sparkles, ArrowRight, User } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [occupation, setOccupation] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const { login, register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      if (isLogin) {
        await login(email, password);
      } else {
        if (password !== confirmPassword) {
          throw new Error('两次输入的密码不一致');
        }
        if (password.length < 6) {
          throw new Error('密码至少需要 6 个字符');
        }
        if (!occupation) {
          throw new Error('请选择您的职业身份');
        }
        await register(email, password, occupation);
        setSuccess('注册成功！请检查邮箱确认链接（如果启用了邮箱验证）');
        setIsLogin(true);
      }
    } catch (err) {
      console.error('Auth error:', err);
      setError(err.message || '操作失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center p-4">
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-dot-pattern opacity-[0.03]" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md relative z-10"
      >
        {/* Logo & Title */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-slate-900 rounded-2xl mb-4 shadow-lg">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">SlideCraft.ai</h1>
          <p className="text-slate-500 mt-1">AI 驱动的演示文稿生成器</p>
        </div>

        {/* Auth Card */}
        <div className="bg-white rounded-2xl shadow-xl border border-slate-200 overflow-hidden">
          {/* Tabs */}
          <div className="flex border-b border-slate-100">
            <button
              onClick={() => { setIsLogin(true); setError(''); setSuccess(''); }}
              className={`flex-1 py-4 text-sm font-medium transition-colors ${isLogin
                  ? 'text-slate-900 border-b-2 border-slate-900'
                  : 'text-slate-400 hover:text-slate-600'
                }`}
            >
              登录
            </button>
            <button
              onClick={() => { setIsLogin(false); setError(''); setSuccess(''); }}
              className={`flex-1 py-4 text-sm font-medium transition-colors ${!isLogin
                  ? 'text-slate-900 border-b-2 border-slate-900'
                  : 'text-slate-400 hover:text-slate-600'
                }`}
            >
              注册
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {/* Email */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-600 flex items-center gap-1">
                <Mail className="w-3 h-3" />
                邮箱地址
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="your@email.com"
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-100 transition-all"
              />
            </div>

            {/* Password */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-slate-600 flex items-center gap-1">
                <Lock className="w-3 h-3" />
                密码
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="••••••••"
                minLength={6}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-100 transition-all"
              />
            </div>

            {/* Confirm Password (Register only) */}
            {!isLogin && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-1.5"
              >
                <label className="text-xs font-medium text-slate-600 flex items-center gap-1">
                  <Lock className="w-3 h-3" />
                  确认密码
                </label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required={!isLogin}
                  placeholder="••••••••"
                  minLength={6}
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-100 transition-all"
                />
              </motion.div>
            )}

            {/* 职业身份 (Register only) */}
            {!isLogin && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="space-y-1.5"
              >
                <label className="text-xs font-medium text-slate-600 flex items-center gap-1">
                  <User className="w-3 h-3" />
                  您的身份
                  <span className="text-slate-400 font-normal">(仅用于优化产品体验)</span>
                </label>
                <select
                  value={occupation}
                  onChange={(e) => setOccupation(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:border-slate-400 focus:ring-2 focus:ring-slate-100 transition-all"
                >
                  <option value="">请选择...</option>
                  <option value="student">大学生 / 研究生</option>
                  <option value="teacher">教师 / 讲师</option>
                  <option value="researcher">研究员 / 学者</option>
                  <option value="employee">企业员工</option>
                  <option value="manager">管理层 / 高管</option>
                  <option value="consultant">咨询顾问</option>
                  <option value="freelancer">自由职业</option>
                  <option value="entrepreneur">创业者</option>
                  <option value="government">政府 / 事业单位</option>
                  <option value="other">其他</option>
                </select>
              </motion.div>
            )}

            {/* Error Message */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-start gap-2 text-sm text-red-600 bg-red-50 p-3 rounded-lg border border-red-100"
              >
                <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                <span>{error}</span>
              </motion.div>
            )}

            {/* Success Message */}
            {success && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-start gap-2 text-sm text-green-600 bg-green-50 p-3 rounded-lg border border-green-100"
              >
                <Sparkles className="w-4 h-4 flex-shrink-0 mt-0.5" />
                <span>{success}</span>
              </motion.div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 bg-slate-900 text-white rounded-lg font-medium text-sm flex items-center justify-center gap-2 hover:bg-slate-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>处理中...</span>
                </>
              ) : (
                <>
                  <span>{isLogin ? '登录' : '注册'}</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Footer */}
          <div className="px-6 pb-6 text-center">
            <p className="text-xs text-slate-400">
              {isLogin ? '还没有账号？' : '已有账号？'}
              <button
                type="button"
                onClick={() => { setIsLogin(!isLogin); setError(''); setSuccess(''); }}
                className="text-slate-600 hover:text-slate-900 font-medium ml-1"
              >
                {isLogin ? '立即注册' : '立即登录'}
              </button>
            </p>
          </div>
        </div>

        {/* Footer Info */}
        <p className="text-center text-xs text-slate-400 mt-6">
          登录即表示您同意我们的服务条款和隐私政策
        </p>
      </motion.div>
    </div>
  );
}
