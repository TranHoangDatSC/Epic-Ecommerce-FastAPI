-- Migration: 004_add_moderator_features.sql
-- Description: Add trust_score to users, violation_logs table, and auto-ban function
-- Date: 2026-03-13

-- Add trust_score column to user table
ALTER TABLE "user" ADD COLUMN trust_score INTEGER DEFAULT 100 NOT NULL;

-- Create violation_logs table
CREATE TABLE violation_log (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(user_id),
    reason VARCHAR(500) NOT NULL,
    action_taken VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for violation_log
CREATE INDEX idx_violation_log_user ON violation_log(user_id);
CREATE INDEX idx_violation_log_created_at ON violation_log(created_at);

-- Create function to auto-ban users with trust_score <= 0
CREATE OR REPLACE FUNCTION auto_ban_low_trust_users()
RETURNS TRIGGER AS $$
BEGIN
    -- If trust_score drops to 0 or below, deactivate the user
    IF NEW.trust_score <= 0 AND OLD.trust_score > 0 THEN
        UPDATE "user" SET is_active = FALSE WHERE user_id = NEW.user_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to call the function when trust_score is updated
CREATE TRIGGER trigger_auto_ban_on_low_trust
    AFTER UPDATE OF trust_score ON "user"
    FOR EACH ROW
    EXECUTE FUNCTION auto_ban_low_trust_users();

-- Add comment to document the changes
COMMENT ON COLUMN "user".trust_score IS 'Trust score for user behavior monitoring (default 100)';
COMMENT ON TABLE violation_log IS 'Logs of user violations and moderator actions';