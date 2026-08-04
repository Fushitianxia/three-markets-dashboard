-- 三国演义 · 全球三市数据可视化系统
-- PostgreSQL Initialization Script

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create indexes for common queries
-- These are created automatically by SQLAlchemy, but we can add performance tweaks here

-- Set timezone
SET timezone = 'Asia/Shanghai';

-- Create a function for automatic updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

COMMENT ON DATABASE stockdb IS '三国演义 · 全球三市数据可视化系统 - 数据池';
