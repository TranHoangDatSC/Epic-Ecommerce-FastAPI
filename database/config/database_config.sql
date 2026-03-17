-- database_config.sql
-- Database configuration settings for OldShop PostgreSQL

-- Set timezone
SET timezone = 'Asia/Ho_Chi_Minh';

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text search

-- Database settings for better performance
ALTER DATABASE oldshop SET search_path TO public;
SET search_path TO public;

-- Connection and memory settings
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Logging settings
ALTER SYSTEM SET log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h ';
ALTER SYSTEM SET log_statement = 'ddl';
ALTER SYSTEM SET log_duration = on;

-- Autovacuum settings for better maintenance
ALTER SYSTEM SET autovacuum = on;
ALTER SYSTEM SET autovacuum_max_workers = 3;
ALTER SYSTEM SET autovacuum_naptime = '20s';
ALTER SYSTEM SET autovacuum_vacuum_threshold = 50;
ALTER SYSTEM SET autovacuum_analyze_threshold = 50;

-- Create indexes for better performance (these are now in individual schema files)
-- But we can add some global indexes here if needed

-- Note: Index for active products will be created after product table is created
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_active_search
-- ON product USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '')))
-- WHERE is_deleted = FALSE AND status = 1;