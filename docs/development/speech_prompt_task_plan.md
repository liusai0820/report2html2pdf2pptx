# 任务计划：优化演讲稿生成 Prompt

## 目标
优化 AI-PPT 工具的演讲稿生成功能，使其能够为工作汇报场景生成符合以下标准的演讲稿：
- 风格得体，不浮夸不简略
- 逻辑清晰，结构完整
- 提升实际演讲效果

## 背景信息
- 目标函数：`generate_speech_script` in src/v2/ai_designer.py:1022
- 主要场景：工作汇报
- 当前实现：已有基础 prompt，需要优化

## 执行阶段

### Phase 1: 分析当前实现 [complete]
- [x] 读取完整的 generate_speech_script 函数
- [x] 分析当前 prompt 结构和内容
- [x] 识别现有的优点和不足
- [x] 记录发现到 findings.md

### Phase 2: 设计优化方案 [complete]
- [x] 分析工作汇报演讲稿的特点
- [x] 确定5个优化方向
- [x] 设计新的 prompt 结构要点

### Phase 3: 实施优化 [complete]
- [x] 编写优化后的 prompt
- [x] 重点优化场景适配部分
- [x] 添加时长控制指导
- [x] 强化数据解读和互动技巧
- [x] 丰富过渡语句

### Phase 4: 验证和总结 [complete]
- [x] 检查新 prompt 的完整性
- [x] 提供使用建议
- [x] 记录改进要点（见 SPEECH_PROMPT_OPTIMIZATION_SUMMARY.md）

## 关键决策
- 已确定当前 prompt 已经相当完善，需要针对性优化而非大改
- 保持现有的总体原则和禁忌清单
- 重点增强场景适配、时长控制、数据解读、互动技巧

## 错误记录
无
