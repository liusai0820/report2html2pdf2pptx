# Supabase 数据库分析报告

> **数据来源**: 直接查询 Supabase 数据库 (2026-01-11)

---

## 1. 数据库现状

### 1.1 表与视图清单

| 名称 | 类型 | 行数 | 状态 |
|------|------|------|------|
| `profiles` | 表 | 162 | ✅ 正常 |
| `generations` | 表 | 219 | ✅ 新记录正常，老记录有 NULL |
| `feedback` | 表 | 22 | ✅ 正常 |
| `speech_scripts` | 表 | 0 | ✅ 已创建，待使用 |
| `plans` | 表 | 4 | ✅ 正常 |
| `user_events` | 表 | - | ❌ 不存在 |
| `admin_users` | 视图 | 162 | ✅ 正常 |
| `admin_generations` | 视图 | 219 | ✅ 正常 |
| `feedback_cn` | 视图 | 22 | ✅ 正常 |

---

## 2. 关键发现

### 2.1 generations 表 - 新记录正常 ✅

通过检查最新 5 条记录，确认大部分字段已正确写入：

| 字段 | 最新记录状态 | 说明 |
|------|-------------|------|
| `font_style` | ✅ modern | 正常 |
| `target_pages` | ✅ 35, 15 | 正常 |
| `content_depth` | ✅ detailed, normal | 正常 |
| `organization` | ✅ 有值 | 正常 |
| `actual_pages` | ✅ 43, 49, 17, 21 | 正常 |
| `output_dir` | ✅ 有值 | 正常 |
| `theme_color` | ⚠️ 部分有值 | 只在用户选择自定义颜色时有值 |
| `custom_instructions` | ❌ NULL | **已修复** (App.jsx:218) |

### 2.2 老记录 NULL 原因

之前分析显示 100% NULL 是因为：
- 随机抽样包含大量老记录（代码更新前创建）
- 新代码添加了这些字段的写入逻辑
- 老记录自然是 NULL，这是正常的历史数据

### 2.3 RLS 策略 ✅

generations 表 RLS 正常：
- SELECT: `auth.uid() = user_id`
- UPDATE: `auth.uid() = user_id`
- INSERT: `with_check = (auth.uid() = user_id)`

无字段级限制，不影响数据写入。

---

## 3. 已完成的修复

### 3.1 custom_instructions 传递 ✅

**文件**: `frontend/src/App.jsx:218`

```javascript
custom_instructions: config.custom_instructions || null,
```

---

## 4. 待执行事项

### 4.1 创建 user_events 表

执行 `migrations/optimize_database.sql` 中的 Part 5。

### 4.2 创建分析视图

执行 `migrations/optimize_database.sql` 中的 Part 4。

---

## 5. 数据价值评估

### 5.1 当前可分析 ✅

| 指标 | 数据源 | 状态 |
|------|--------|------|
| 用户增长 | profiles.created_at | ✅ |
| 场景使用分布 | generations.scenario | ✅ |
| 配置偏好 | generations.font_style, target_pages 等 | ✅ 新记录有值 |
| 用户反馈评分 | feedback.rating | ✅ |
| 职业分布 | profiles.occupation | ✅ 部分 |

### 5.2 待创建

| 指标 | 数据源 | 状态 |
|------|--------|------|
| 用户行为漏斗 | user_events | ❌ 表不存在 |
| custom_instructions 使用率 | generations | ✅ 已修复，将有数据 |

---

_生成时间: 2026-01-11_
_数据源: Supabase 直连查询_
