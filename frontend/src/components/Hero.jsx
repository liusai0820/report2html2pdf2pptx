import React from 'react';
import { motion } from 'framer-motion';
import { Zap } from 'lucide-react';

export default function Hero() {
  return (
    <div className="mb-6">
      <motion.div 
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
      >
        <div className="flex items-center gap-2 mb-3">
          <div className="flex items-center gap-1 px-2 py-0.5 bg-slate-900 rounded-full">
             <Zap className="w-2.5 h-2.5 text-yellow-400 fill-yellow-400" />
             <span className="text-[9px] font-bold tracking-wider text-white uppercase">企业级引擎</span>
          </div>
        </div>

        <h1 className="text-[1.75rem] font-extrabold text-slate-900 leading-tight tracking-tight mb-2">
          SlideCraft<span className="text-slate-400">.ai</span>
        </h1>
        
        <p className="text-base font-medium text-slate-700 mb-2">
          灵感即刻呈现，思想掷地有声。
        </p>

        <p className="text-[11px] text-slate-400 leading-relaxed">
          深度解析上下文，自动构建逻辑框架与视觉设计。<br/>
          让每一次演示，都成为专业的表达。
        </p>
      </motion.div>
    </div>
  );
}
