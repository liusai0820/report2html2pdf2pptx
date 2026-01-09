# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### 演讲稿生成增强
- **智能时长控制**：根据演讲时长自动调整详略程度（精简/适中/详细）
  - 短汇报（<10分钟）：80-120字/页
  - 中等汇报（10-20分钟）：100-150字/页
  - 长汇报（>20分钟）：120-200字/页

- **场景智能适配**：根据场景类型提供差异化风格指导
  - 工作汇报/报告：成果导向、数据为主、问题与对策
  - 项目答辩/评审：可行性论证、技术细节、预判质疑
  - 述职报告：个人贡献、成长思考、问题反思
  - 一般性汇报：保持专业客观

- **数据解读增强**：提供 4 类专业数据表达模板
  - 增长趋势分析话术
  - 对比分析话术
  - 占比说明话术
  - 图表解读话术

- **互动技巧模块**：新增演讲互动指导
  - 引导注意力技巧
  - 强调重点技巧
  - 节奏把控技巧

- **丰富过渡语句**：从 3 个示例扩展到 4 大类 10+ 示例
  - 章节过渡
  - 内容过渡
  - 强调重点
  - 引导注意

#### 演讲稿阅读器组件
- **三套精致主题**：适应不同阅读环境
  - 日间模式（纯白背景，蓝色强调）
  - 护眼模式（暖米黄背景，棕色强调）
  - 夜间模式（深灰黑背景，浅蓝强调）

- **字号调节功能**：4 档可选（S/M/L/XL: 14-20px）

- **实用操作功能**
  - 一键复制全文（带成功反馈）
  - 下载为 Markdown 文件

- **增强的 Markdown 渲染**
  - 支持演讲专用标记：`[过渡]`、`[停顿]`
  - 自定义标题、段落、列表样式
  - 渐变分隔线渲染

- **精致的排版系统**
  - 标题：Inter / PingFang SC（无衬线，现代感）
  - 正文：Newsreader / Source Serif Pro / Noto Serif SC / Georgia（衬线，易读性强）
  - 两端对齐，动态行高
  - 自定义滚动条（主题匹配）

- **优雅的状态设计**
  - 精致的加载动画（旋转环绕麦克风 + 脉冲点）
  - 清晰的错误提示界面

### Changed

#### 演讲稿生成 Prompt
- 优化段落结构指导：引导注意 → 核心论点 → 数据支撑 → 承上启下
- 扩充禁忌清单：新增"不要只报数据不解读"和"不要过渡语单调重复"
- 优化开场白和结尾模板，使用动态变量
- 提升数据解读要求，强调必须说明意义和影响

#### UI/UX 改进
- 演讲稿模态框从基础设计升级为编辑杂志风格
- 提升视觉层次和设计精致度
- 优化内容呈现的可读性和舒适度
- 改进交互反馈（复制成功提示、悬浮效果、禁用状态）

### Technical Details

**Backend 改进** (`src/v2/ai_designer.py`)
- 新增时长控制逻辑（1043-1052 行）
- 新增场景适配逻辑（1054-1081 行）
- 优化 Prompt 模板，使用动态变量插值
- 改进 Markdown 格式指导

**Frontend 改进** (`frontend/src/components/ResultView.jsx`)
- 新增 `SpeechScriptModal` 组件（19-394 行）
- 实现主题系统（light/sepia/dark）
- 实现响应式字号控制
- 使用 styled-jsx 动态注入主题样式
- 增强 Markdown 解析器（支持自定义语法）
- 添加复制和下载功能

### Documentation

- 新增 `SPEECH_PROMPT_OPTIMIZATION_SUMMARY.md` - 演讲稿 Prompt 优化详细文档
- 新增 `SPEECH_MODAL_OPTIMIZATION.md` - 演讲稿模态框优化详细文档
- 新增 `OPTIMIZATION_SUMMARY.md` - 总体优化总结

---

## [Previous Versions]

### [1.0.0] - Earlier
- 基础演讲稿生成功能
- 基础演讲稿预览模态框
- PPT 生成核心功能
