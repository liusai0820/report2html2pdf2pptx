# 用户管理系统优化指南

## 1. Supabase 数据库优化

### 1.1 更新 profiles 表（必须执行）

在 Supabase Dashboard > SQL Editor 中执行：

```sql
-- 添加新字段
ALTER TABLE profiles 
  ADD COLUMN IF NOT EXISTS quota_expires_at TIMESTAMPTZ,     -- 额度过期时间
  ADD COLUMN IF NOT EXISTS plan_type TEXT DEFAULT 'free',    -- 套餐类型
  ADD COLUMN IF NOT EXISTS plan_purchased_at TIMESTAMPTZ;    -- 套餐购买时间

-- 更新列注释
COMMENT ON COLUMN profiles.quota_expires_at IS '额度过期时间，NULL表示永久有效';
COMMENT ON COLUMN profiles.plan_type IS '套餐类型: free/deadline/pass/team';
```

### 1.2 创建管理视图（推荐）

```sql
-- 用户管理视图（带邮箱，方便查看）
CREATE OR REPLACE VIEW admin_users AS
SELECT 
  p.id,
  u.email,
  p.plan_type,
  p.generation_quota AS "总额度",
  p.generations_used AS "已使用",
  (p.generation_quota - COALESCE(p.generations_used, 0)) AS "剩余次数",
  p.quota_expires_at AS "过期时间",
  CASE 
    WHEN p.quota_expires_at IS NULL THEN '永久有效'
    WHEN p.quota_expires_at > NOW() THEN '有效 (' || (p.quota_expires_at::date - CURRENT_DATE) || '天)'
    ELSE '❌ 已过期'
  END AS "额度状态",
  p.created_at AS "注册时间",
  p.updated_at AS "最后活跃"
FROM profiles p
LEFT JOIN auth.users u ON p.id = u.id
ORDER BY p.updated_at DESC;

-- 生成记录视图（带邮箱）
CREATE OR REPLACE VIEW admin_generations AS
SELECT 
  g.id,
  u.email AS "用户邮箱",
  g.title AS "生成标题",
  g.status AS "状态",
  g.actual_pages AS "页数",
  g.theme_color AS "主题色",
  g.created_at AS "生成时间",
  g.user_id
FROM generations g
LEFT JOIN auth.users u ON g.user_id = u.id
ORDER BY g.created_at DESC;
```

### 1.3 套餐配置表（可选，方便管理）

```sql
-- 套餐配置表
CREATE TABLE IF NOT EXISTS plans (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  quota INTEGER NOT NULL,
  validity_days INTEGER,  -- NULL = 永久
  description TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 初始化套餐
INSERT INTO plans (id, name, price, quota, validity_days, description) VALUES
  ('free', '游客体验', 0, 1, NULL, '仅生成草稿预览'),
  ('deadline', 'Deadline急救包', 9.9, 1, NULL, '1份源文件，无水印'),
  ('pass', '汇报通关卡', 39, 10, 90, '10份深度生成，90天有效'),
  ('team', '季度共享卡', 79, 30, 90, '30份超大额度，支持多人共享')
ON CONFLICT (id) DO UPDATE SET
  name = EXCLUDED.name,
  price = EXCLUDED.price,
  quota = EXCLUDED.quota,
  validity_days = EXCLUDED.validity_days,
  description = EXCLUDED.description;
```

---

## 2. Retool 后台搭建指南

### 2.1 注册 Retool

1. 访问 https://retool.com/
2. 免费注册（5用户免费）
3. 创建一个新的 App

### 2.2 连接 Supabase

1. 在 Retool 左侧 → Resources → Create new
2. 选择 PostgreSQL
3. 填写连接信息（在 Supabase Dashboard > Settings > Database 获取）：
   - Host: `db.xxxx.supabase.co`
   - Port: `5432`
   - Database: `postgres`
   - Username: `postgres`
   - Password: 你的数据库密码

### 2.3 创建管理界面

#### 查询 1：用户列表

```sql
SELECT * FROM admin_users LIMIT 100;
```

#### 查询 2：设置用户套餐

```sql
UPDATE profiles SET
  plan_type = {{ plan_select.value }},
  generation_quota = {{ quota_input.value }},
  generations_used = 0,
  quota_expires_at = CASE 
    WHEN {{ validity_days.value }} IS NOT NULL 
    THEN NOW() + INTERVAL '1 day' * {{ validity_days.value }}
    ELSE NULL 
  END,
  plan_purchased_at = NOW(),
  updated_at = NOW()
WHERE id = {{ users_table.selectedRow.id }};
```

#### 查询 3：增加额度

```sql
UPDATE profiles SET
  generation_quota = generation_quota + {{ add_quota_input.value }},
  updated_at = NOW()
WHERE id = {{ users_table.selectedRow.id }};
```

#### 查询 4：延长有效期

```sql
UPDATE profiles SET
  quota_expires_at = CASE
    WHEN quota_expires_at IS NULL THEN NOW() + INTERVAL '1 day' * {{ extend_days.value }}
    WHEN quota_expires_at < NOW() THEN NOW() + INTERVAL '1 day' * {{ extend_days.value }}
    ELSE quota_expires_at + INTERVAL '1 day' * {{ extend_days.value }}
  END,
  updated_at = NOW()
WHERE id = {{ users_table.selectedRow.id }};
```

### 2.4 推荐的 Retool 界面布局

```
┌─────────────────────────────────────────────────────────────┐
│  🎛 PPT生成器 - 用户管理后台                                   │
├─────────────────────────────────────────────────────────────┤
│  [搜索用户邮箱: ____________]  [刷新]                          │
├─────────────────────────────────────────────────────────────┤
│  用户列表 (Table)                                             │
│  ┌────────┬──────────────────┬────────┬──────┬──────┬──────┐│
│  │ 邮箱   │ 套餐             │ 剩余   │ 状态 │ 注册 │ 活跃 ││
│  ├────────┼──────────────────┼────────┼──────┼──────┼──────┤│
│  │ a@...  │ 汇报通关卡       │ 8次    │ 有效 │ 1/1  │ 1/4  ││
│  │ b@...  │ 游客体验         │ 0次    │ --   │ 1/2  │ 1/3  ││
│  └────────┴──────────────────┴────────┴──────┴──────┴──────┘│
├─────────────────────────────────────────────────────────────┤
│  操作面板 (选中用户后显示)                                     │
│  ┌────────────────────┬────────────────────────────────────┐│
│  │ 设置套餐           │ 快捷操作                           ││
│  │ [套餐类型 ▼]       │ [+5次额度] [+30天有效期] [重置]   ││
│  │ [额度: 10]         │                                    ││
│  │ [有效期: 90天]     │                                    ││
│  │ [确认设置]         │                                    ││
│  └────────────────────┴────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 快速操作 SQL（直接在 Supabase 执行）

### 给用户设置39元套餐

```sql
UPDATE profiles SET
  plan_type = 'pass',
  generation_quota = 10,
  generations_used = 0,
  quota_expires_at = NOW() + INTERVAL '90 days',
  plan_purchased_at = NOW()
WHERE id = '用户ID';
```

### 按邮箱查找并设置

```sql
UPDATE profiles SET
  plan_type = 'pass',
  generation_quota = 10,
  generations_used = 0,
  quota_expires_at = NOW() + INTERVAL '90 days'
WHERE id = (SELECT id FROM auth.users WHERE email = 'user@example.com');
```

### 查看所有付费用户

```sql
SELECT * FROM admin_users WHERE plan_type != 'free';
```

---

## 4. 移动端使用

Retool 支持移动端浏览器访问，直接用手机打开你的 Retool App URL 即可。

建议：
- 保存书签到手机主屏幕
- 使用 Retool Mobile App（更流畅）

---

## 5. 后端代码已更新

`src/db.py` 新增了以下函数：

- `check_quota_valid(user_id)` - 检查额度是否有效（含有效期检查）
- `set_user_plan(user_id, plan_type, quota, validity_days)` - 设置用户套餐
- `get_all_users(limit)` - 获取用户列表

前端生成前应调用 `check_quota_valid()` 来验证用户额度。
