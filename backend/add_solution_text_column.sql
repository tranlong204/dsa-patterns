-- Add solution_text column to problems table
ALTER TABLE IF NOT EXISTS problems ADD COLUMN IF NOT EXISTS solution_text TEXT;

