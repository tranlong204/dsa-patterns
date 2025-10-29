-- Add solution_text column to problems table
ALTER TABLE problems ADD COLUMN IF NOT EXISTS solution_text TEXT;

