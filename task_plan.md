# Supabase 数据库优化计划

> **基于真实数据库分析** (2026-01-11)

---

## 最终结论

经过深入分析，发现情况比预期好：

| 问题 | 原状态 | 实际情况 |
|------|--------|----------|
| generations 表字段 NULL | 🔴 P0 | ✅ **新记录正常**，老记录是历史数据 |
| custom_instructions 未传递 | 🟡 P1 | ✅ **已修复** |
| user_events 表不存在 | 🟡 P1 | 待执行迁移 |
| RLS 策略问题 | 待查 | ✅ 策略正常 |

---

## Phase 1: 诊断 [completed] ✅

### 1.1 RLS 策略检查 ✅

执行结果：策略正常，无字段级限制。

### 1.2 最新记录检查 ✅

通过 `scripts/check_latest_generations.py` 确认：
- `font_style`, `target_pages`, `content_depth` 等字段在新记录中正确填充
- 老记录 NULL 是因为在代码更新前创建

---

## Phase 2: 代码修复 [completed] ✅

### 2.1 custom_instructions 传递 ✅

**文件**: `frontend/src/App.jsx:218`

```javascript
custom_instructions: config.custom_instructions || null,
```

---

## Phase 3: 数据库优化 [pending]

### 3.1 创建 user_events 表

执行 `migrations/optimize_database.sql` 中的 Part 5。

### 3.2 创建分析视图

执行 `migrations/optimize_database.sql` 中的 Part 4：
- `analytics_user_growth`
- `analytics_scenario_usage`
- `analytics_user_activity`
- `analytics_daily_overview`
- `analytics_occupation_distribution`

### 3.3 Admin.jsx 更新 ✅

已添加「自定义指令」列到生成记录表格。

---

## 交付物

| 文件 | 状态 | 说明 |
|------|------|------|
| `findings.md` | ✅ | 详细分析报告 |
| `migrations/optimize_database.sql` | ✅ | 优化迁移脚本 |
| `scripts/analyze_database.py` | ✅ | 数据库分析工具 |
| `scripts/check_latest_generations.py` | ✅ | 最新记录检查工具 |
| `frontend/src/App.jsx` | ✅ | 已添加 custom_instructions |

---

## 下一步

1. 在 Supabase SQL Editor 执行 `migrations/optimize_database.sql`（可选，用于创建分析视图和 user_events 表）

---

_最后更新: 2026-01-11_
