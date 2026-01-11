-- 在 Supabase SQL 编辑器中执行
-- 创建演讲稿存储表

-- 1. 创建表
CREATE TABLE IF NOT EXISTS speech_scripts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    generation_id TEXT NOT NULL UNIQUE,     -- 对应 output_name (如 "20250111_abc123")
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,                  -- Markdown 内容
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 创建索引
CREATE INDEX IF NOT EXISTS idx_speech_scripts_generation_id ON speech_scripts(generation_id);
CREATE INDEX IF NOT EXISTS idx_speech_scripts_user_id ON speech_scripts(user_id);

-- 3. 启用 RLS
ALTER TABLE speech_scripts ENABLE ROW LEVEL SECURITY;

-- 4. RLS 策略: 用户只能访问自己的演讲稿
CREATE POLICY "Users can view own speech scripts" ON speech_scripts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own speech scripts" ON speech_scripts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own speech scripts" ON speech_scripts
    FOR UPDATE USING (auth.uid() = user_id);

-- 5. 添加注释
COMMENT ON TABLE speech_scripts IS '演讲稿存储表，与生成记录一对一关联';
COMMENT ON COLUMN speech_scripts.generation_id IS '关联的演示文稿生成ID (output_name)';
COMMENT ON COLUMN speech_scripts.content IS 'Markdown 格式的演讲稿内容';
