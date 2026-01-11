-- ============================================
-- SlideCraft 数据库优化迁移脚本
-- 执行位置: Supabase SQL Editor
-- 创建日期: 2026-01-11
-- ============================================

-- ============================================
-- Part 1: 数据完整性约束 (P0 - 立即执行)
-- ============================================

-- 1.1 profiles 表约束
-- 注意: 如果现有数据不符合约束会报错，需要先清理

-- plan_type 枚举约束
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'check_plan_type'
    ) THEN
        ALTER TABLE profiles
        ADD CONSTRAINT check_plan_type
        CHECK (plan_type IS NULL OR plan_type IN ('free', 'deadline', 'pass', 'team'));
    END IF;
END $$;

-- 额度非负约束
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'check_quota_positive'
    ) THEN
        ALTER TABLE profiles
        ADD CONSTRAINT check_quota_positive CHECK (generation_quota >= 0);
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'check_used_positive'
    ) THEN
        ALTER TABLE profiles
        ADD CONSTRAINT check_used_positive CHECK (generations_used >= 0);
    END IF;
END $$;

-- 1.2 feedback 表约束
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'check_rating_range'
    ) THEN
        ALTER TABLE feedback
        ADD CONSTRAINT check_rating_range CHECK (rating >= 1 AND rating <= 10);
    END IF;
END $$;

-- ============================================
-- Part 2: 索引优化 (P1)
-- ============================================

-- 日报查询优化索引
CREATE INDEX IF NOT EXISTS idx_profiles_created_at ON profiles(created_at);
CREATE INDEX IF NOT EXISTS idx_generations_created_at ON generations(created_at);
CREATE INDEX IF NOT EXISTS idx_feedback_created_at ON feedback(created_at);

-- 用户关联查询索引
CREATE INDEX IF NOT EXISTS idx_generations_user_id ON generations(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_user_id ON feedback(user_id);

-- 复合索引: 用户+时间 (常用查询模式)
CREATE INDEX IF NOT EXISTS idx_generations_user_created
    ON generations(user_id, created_at DESC);

-- ============================================
-- Part 3: 更新 admin_generations 视图
-- ============================================

-- 先删除旧视图（因为不能改变列的数据类型）
DROP VIEW IF EXISTS admin_generations;

-- 重新创建视图，包含更多字段（包括 custom_instructions）
CREATE VIEW admin_generations AS
SELECT
    g.id,
    p.email::VARCHAR(255) AS "用户邮箱",
    g.document_name AS "文档名",
    g.scenario,
    g.actual_pages AS "页数",
    g.created_at AS "生成时间(北京)",
    g.user_id,
    p.occupation,
    -- 新增字段
    g.theme_color,
    g.font_style,
    g.target_pages,
    g.content_depth,
    g.organization,
    g.custom_instructions,
    g.output_dir
FROM generations g
LEFT JOIN profiles p ON g.user_id = p.id
ORDER BY g.created_at DESC;

COMMENT ON VIEW admin_generations IS '管理后台生成记录视图（含配置详情）';

-- ============================================
-- Part 4: 运营分析视图 (P2)
-- ============================================

-- 4.1 用户增长趋势
CREATE OR REPLACE VIEW analytics_user_growth AS
SELECT
    DATE_TRUNC('day', created_at)::DATE AS date,
    COUNT(*) AS new_users,
    COUNT(*) FILTER (WHERE plan_type IS NOT NULL AND plan_type != 'free') AS paid_users,
    COUNT(*) FILTER (WHERE occupation IS NOT NULL) AS users_with_occupation
FROM profiles
WHERE created_at IS NOT NULL
GROUP BY 1
ORDER BY 1 DESC;

COMMENT ON VIEW analytics_user_growth IS '每日用户增长趋势';

-- 4.2 场景使用热度
CREATE OR REPLACE VIEW analytics_scenario_usage AS
SELECT
    COALESCE(scenario, 'unknown') AS scenario,
    COUNT(*) AS total_generations,
    COUNT(DISTINCT user_id) AS unique_users,
    ROUND(AVG(actual_pages), 1) AS avg_pages
FROM generations
GROUP BY scenario
ORDER BY total_generations DESC;

COMMENT ON VIEW analytics_scenario_usage IS '场景使用热度分析';

-- 4.3 用户活跃度概览
CREATE OR REPLACE VIEW analytics_user_activity AS
SELECT
    p.id AS user_id,
    p.email,
    p.plan_type,
    p.occupation,
    p.created_at AS registered_at,
    p.generation_quota,
    p.generations_used,
    COUNT(DISTINCT g.id) AS total_generations,
    MAX(g.created_at) AS last_generation_at,
    COUNT(DISTINCT ss.id) AS speech_scripts_count,
    EXTRACT(DAY FROM (NOW() - p.created_at)) AS days_since_registration
FROM profiles p
LEFT JOIN generations g ON g.user_id = p.id
LEFT JOIN speech_scripts ss ON ss.user_id = p.id
GROUP BY p.id, p.email, p.plan_type, p.occupation, p.created_at, p.generation_quota, p.generations_used;

COMMENT ON VIEW analytics_user_activity IS '用户活跃度综合视图';

-- 4.4 每日运营概览
CREATE OR REPLACE VIEW analytics_daily_overview AS
SELECT
    d.date,
    COALESCE(u.new_users, 0) AS new_users,
    COALESCE(g.generations, 0) AS generations,
    COALESCE(f.feedbacks, 0) AS feedbacks,
    COALESCE(f.avg_rating, 0) AS avg_rating,
    COALESCE(s.speech_scripts, 0) AS speech_scripts
FROM (
    SELECT generate_series(
        CURRENT_DATE - INTERVAL '30 days',
        CURRENT_DATE,
        INTERVAL '1 day'
    )::DATE AS date
) d
LEFT JOIN (
    SELECT DATE_TRUNC('day', created_at)::DATE AS date, COUNT(*) AS new_users
    FROM profiles GROUP BY 1
) u ON u.date = d.date
LEFT JOIN (
    SELECT DATE_TRUNC('day', created_at)::DATE AS date, COUNT(*) AS generations
    FROM generations GROUP BY 1
) g ON g.date = d.date
LEFT JOIN (
    SELECT DATE_TRUNC('day', created_at)::DATE AS date,
           COUNT(*) AS feedbacks,
           ROUND(AVG(rating), 2) AS avg_rating
    FROM feedback GROUP BY 1
) f ON f.date = d.date
LEFT JOIN (
    SELECT DATE_TRUNC('day', created_at)::DATE AS date, COUNT(*) AS speech_scripts
    FROM speech_scripts GROUP BY 1
) s ON s.date = d.date
ORDER BY d.date DESC;

COMMENT ON VIEW analytics_daily_overview IS '每日运营数据概览 (最近30天)';

-- 4.5 职业分布统计
CREATE OR REPLACE VIEW analytics_occupation_distribution AS
SELECT
    COALESCE(occupation, 'unknown') AS occupation,
    COUNT(*) AS user_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS percentage,
    COUNT(*) FILTER (WHERE plan_type != 'free' AND plan_type IS NOT NULL) AS paid_count
FROM profiles
GROUP BY occupation
ORDER BY user_count DESC;

COMMENT ON VIEW analytics_occupation_distribution IS '用户职业分布统计';

-- 4.6 Custom Instructions 使用统计
CREATE OR REPLACE VIEW analytics_custom_instructions AS
SELECT
    DATE_TRUNC('day', created_at)::DATE AS date,
    COUNT(*) AS total_generations,
    COUNT(*) FILTER (WHERE custom_instructions IS NOT NULL AND custom_instructions != '') AS with_instructions,
    ROUND(
        COUNT(*) FILTER (WHERE custom_instructions IS NOT NULL AND custom_instructions != '') * 100.0 /
        NULLIF(COUNT(*), 0),
        1
    ) AS usage_rate_percent
FROM generations
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY 1
ORDER BY 1 DESC;

COMMENT ON VIEW analytics_custom_instructions IS 'Custom Instructions 使用率统计';

-- ============================================
-- Part 5: 用户行为事件表 (P2 - 可选)
-- ============================================

-- 创建事件表
CREATE TABLE IF NOT EXISTS user_events (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    event_data JSONB DEFAULT '{}',
    session_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_user_events_user_id ON user_events(user_id);
CREATE INDEX IF NOT EXISTS idx_user_events_type ON user_events(event_type);
CREATE INDEX IF NOT EXISTS idx_user_events_created_at ON user_events(created_at);
CREATE INDEX IF NOT EXISTS idx_user_events_session ON user_events(session_id);

-- RLS
ALTER TABLE user_events ENABLE ROW LEVEL SECURITY;

-- 策略: 用户可以查看自己的事件
DROP POLICY IF EXISTS "Users can view own events" ON user_events;
CREATE POLICY "Users can view own events" ON user_events
    FOR SELECT USING (auth.uid() = user_id);

-- 策略: 允许 service_role 插入 (后端使用)
DROP POLICY IF EXISTS "Service can insert events" ON user_events;
CREATE POLICY "Service can insert events" ON user_events
    FOR INSERT WITH CHECK (true);

-- 注释
COMMENT ON TABLE user_events IS '用户行为事件追踪表';
COMMENT ON COLUMN user_events.event_type IS '事件类型: page_view, generate_start, generate_complete, download, generate_speech, share, feedback';
COMMENT ON COLUMN user_events.event_data IS 'JSON格式的事件详情';
COMMENT ON COLUMN user_events.session_id IS '会话ID，用于追踪用户单次访问';

-- 事件分析视图
CREATE OR REPLACE VIEW analytics_event_funnel AS
SELECT
    event_type,
    COUNT(*) AS event_count,
    COUNT(DISTINCT user_id) AS unique_users,
    COUNT(DISTINCT session_id) AS unique_sessions,
    DATE_TRUNC('day', created_at)::DATE AS date
FROM user_events
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY event_type, DATE_TRUNC('day', created_at)
ORDER BY date DESC, event_count DESC;

COMMENT ON VIEW analytics_event_funnel IS '事件漏斗分析 (最近30天)';

-- ============================================
-- 完成
-- ============================================
DO $$
BEGIN
    RAISE NOTICE '====================================';
    RAISE NOTICE 'SlideCraft 数据库优化迁移 - 全部完成!';
    RAISE NOTICE '====================================';
END $$;
