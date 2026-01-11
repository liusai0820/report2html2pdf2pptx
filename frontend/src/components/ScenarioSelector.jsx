import React from 'react';
import { Check, Palette } from 'lucide-react';

export default function ScenarioSelector({ scenarios, selected, onSelect, customColor, onColorChange }) {
  const selectedScenario = scenarios.find(s => s.id === selected);
  
  // 预设颜色 (带名称用于 tooltip)
  const presetColors = [
    { hex: "#000000", name: "经典黑" },
    { hex: "#003366", name: "深海蓝" },
    { hex: "#005EB8", name: "商务蓝" },
    { hex: "#2A9D8F", name: "青竹绿" },
    { hex: "#E63946", name: "中国红" },
    { hex: "#F4A261", name: "活力橙" },
    { hex: "#4A4E69", name: "雅致灰" },
    { hex: "#6A4C93", name: "典雅紫" }
  ];

  return (
    <div className="space-y-3">
      {/* 场景网格 - 3行2列，统一高度 */}
      <div className="grid grid-cols-2 gap-2">
        {scenarios.map((scenario) => {
          const isSelected = selected === scenario.id;
          
          return (
            <button
              key={scenario.id}
              onClick={() => {
                  onSelect(scenario.id);
                  if (onColorChange) onColorChange(null);
              }}
              className={`
                relative h-9 flex items-center justify-between px-3 rounded-lg border transition-all duration-150 overflow-hidden
                ${isSelected
                  ? 'border-slate-300 bg-slate-50 shadow-sm'
                  : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'
                }
              `}
            >
              {/* 左侧选中色条 */}
              <div
                className={`absolute left-0 top-0 bottom-0 w-1 transition-all duration-200 ${isSelected ? 'opacity-100' : 'opacity-0'}`}
                style={{ backgroundColor: customColor || scenario.color }}
              />
              {/* 场景名称 - 统一字号 */}
              <span className={`text-[13px] font-medium leading-none ${isSelected ? 'text-slate-900' : 'text-slate-600'}`}>
                {scenario.name}
              </span>
              
              {/* 右侧：颜色点 + 选中标记 */}
              <div className="flex items-center gap-1.5 flex-shrink-0">
                <div 
                  className="w-2 h-2 rounded-full ring-1 ring-black/10"
                  style={{ backgroundColor: isSelected ? (customColor || scenario.color) : scenario.color }}
                />
                {isSelected && (
                  <div className="w-4 h-4 bg-slate-900 rounded-full flex items-center justify-center">
                      <Check className="w-2.5 h-2.5 text-white" strokeWidth={3} />
                  </div>
                )}
              </div>
            </button>
          );
        })}
      </div>

      {/* 主题色定制区域 */}
      {selectedScenario && (
        <div className="pt-2 border-t border-slate-100">
            <div className="flex items-center justify-between mb-2">
                <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wide flex items-center gap-1">
                    <Palette className="w-3 h-3" /> 主题色定制
                </span>
                <span className="text-[9px] font-mono text-slate-400 uppercase tracking-wide">
                    {customColor || selectedScenario.color}
                </span>
            </div>
            
            <div className="flex items-center gap-1.5 flex-wrap">
                {/* 默认色 */}
                <button
                    onClick={() => onColorChange(null)}
                    className={`w-5 h-5 rounded-full border border-slate-200 flex items-center justify-center transition-transform hover:scale-110
                        ${!customColor ? 'ring-2 ring-slate-900 ring-offset-1' : ''}
                    `}
                    title="恢复默认"
                >
                    <div className="w-full h-full rounded-full" style={{ backgroundColor: selectedScenario.color }} />
                </button>
                
                <div className="w-px h-4 bg-slate-200 mx-0.5" />

                {/* 预设色 */}
                {presetColors.map(({ hex, name }) => (
                     <button
                        key={hex}
                        onClick={() => onColorChange(hex)}
                        className={`w-5 h-5 rounded-full border border-slate-200 transition-all duration-150 hover:scale-125 hover:shadow-md relative group
                            ${customColor === hex ? 'ring-2 ring-slate-900 ring-offset-1' : ''}
                        `}
                        style={{ backgroundColor: hex }}
                        title={`${name} ${hex}`}
                    >
                      {/* Tooltip */}
                      <span className="absolute -top-8 left-1/2 -translate-x-1/2 bg-slate-800 text-white text-[10px] py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10">
                        {name}
                      </span>
                    </button>
                ))}
                
                {/* 自定义颜色选择器 */}
                <div className="relative group">
                    <input 
                        type="color" 
                        value={customColor || selectedScenario.color}
                        onChange={(e) => onColorChange(e.target.value)}
                        className="w-5 h-5 opacity-0 absolute inset-0 cursor-pointer"
                    />
                    <div className="w-5 h-5 rounded-full bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 border border-slate-200 flex items-center justify-center">
                        <span className="text-[7px] text-white font-bold">+</span>
                    </div>
                </div>
            </div>
        </div>
      )}
    </div>
  );
}
