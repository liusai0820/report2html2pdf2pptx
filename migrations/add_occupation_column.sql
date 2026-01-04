-- 在 Supabase SQL 编辑器中执行
-- 为 profiles 表添加 occupation 列

ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS occupation TEXT DEFAULT NULL;

COMMENT ON COLUMN profiles.occupation IS '用户职业身份: student, teacher, researcher, employee, manager, consultant, freelancer, entrepreneur, government, other';
