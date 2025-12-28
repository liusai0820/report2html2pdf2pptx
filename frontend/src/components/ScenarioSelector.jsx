import React from 'react';
import { Check, Palette } from 'lucide-react';

export default function ScenarioSelector({ scenarios, selected, onSelect, customColor, onColorChange }) {
  const selectedScenario = scenarios.find(s => s.id === selected);

  // 预设颜色
  const presetColors = [
    "#000000", "#003366", "#005EB8", "#2A9D8F",
    "#E63946", "#F4A261", "#4A4E69", "#6A4C93"
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
                relative h-10 flex items-center justify-between px-3.5 rounded-xl border transition-all duration-200
                ${isSelected
                  ? 'border-indigo-600 ring-1 ring-indigo-600 bg-indigo-50/30'
                  : 'border-slate-200 bg-white hover:border-indigo-200 hover:bg-slate-50/50'
                }
              `}
            >
              {/* 场景名称 - 统一字号 */}
              <span className={`text-[13px] font-medium leading-none ${isSelected ? 'text-indigo-950 font-semibold' : 'text-slate-600'}`}>
                {scenario.name}
              </span>

              {/* 右侧：颜色点 + 选中标记 */}
              <div className="flex items-center gap-2 flex-shrink-0">
                <div
                  className={`w-2 h-2 rounded-full transition-all ${isSelected ? 'scale-0 opacity-0 w-0' : 'scale-100 opacity-100'}`}
                  style={{ backgroundColor: scenario.color }}
                />
                {isSelected && (
                  <div className="w-5 h-5 bg-gradient-to-tr from-indigo-600 to-violet-600 rounded-full flex items-center justify-center shadow-sm animate-in zoom-in-50 duration-200">
                    <Check className="w-3 h-3 text-white" strokeWidth={3} />
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
                        ${!customColor ? 'ring-2 ring-indigo-600 ring-offset-1' : ''}
                    `}
              title="恢复默认"
            >
              <div className="w-full h-full rounded-full" style={{ backgroundColor: selectedScenario.color }} />
            </button>

            <div className="w-px h-4 bg-slate-200 mx-0.5" />

            {/* 预设色 */}
            {presetColors.map(color => (
              <button
                key={color}
                onClick={() => onColorChange(color)}
                className={`w-5 h-5 rounded-full border border-slate-200 transition-transform hover:scale-110
                            ${customColor === color ? 'ring-2 ring-indigo-600 ring-offset-1' : ''}
                        `}
                style={{ backgroundColor: color }}
              />
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
