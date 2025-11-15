-- Create problems table
CREATE TABLE IF NOT EXISTS problems (
    id BIGSERIAL PRIMARY KEY,
    number INTEGER NOT NULL,
    title TEXT NOT NULL,
    difficulty VARCHAR(10) NOT NULL CHECK (difficulty IN ('Easy', 'Medium', 'Hard')),
    topics JSONB NOT NULL,
    link TEXT NOT NULL,
    subtopic TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create user_progress table
CREATE TABLE IF NOT EXISTS user_progress (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    problem_id INTEGER NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
    solved BOOLEAN DEFAULT FALSE,
    solved_at DATE,
    in_revision BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, problem_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_problems_topics ON problems USING GIN (topics);
CREATE INDEX IF NOT EXISTS idx_problems_difficulty ON problems(difficulty);
CREATE INDEX IF NOT EXISTS idx_user_progress_user_id ON user_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_user_progress_problem_id ON user_progress(problem_id);
CREATE INDEX IF NOT EXISTS idx_user_progress_solved ON user_progress(solved);
CREATE INDEX IF NOT EXISTS idx_user_progress_solved_at ON user_progress(solved_at);

-- Enable Row Level Security (optional)
ALTER TABLE problems ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_progress ENABLE ROW LEVEL SECURITY;

-- Create policies (allow read for everyone, write for authenticated users)
DROP POLICY IF EXISTS "Problems are viewable by everyone" ON problems;
CREATE POLICY "Problems are viewable by everyone" ON problems
    FOR SELECT USING (true);

DROP POLICY IF EXISTS "User progress is viewable by everyone" ON user_progress;
CREATE POLICY "User progress is viewable by everyone" ON user_progress
    FOR SELECT USING (true);
    
DROP POLICY IF EXISTS "Users can update progress" ON user_progress;
CREATE POLICY "Users can update progress" ON user_progress
    FOR UPDATE USING (true);
    
DROP POLICY IF EXISTS "Users can insert progress" ON user_progress;
CREATE POLICY "Users can insert progress" ON user_progress
    FOR INSERT WITH CHECK (true);
    
DROP POLICY IF EXISTS "Users can delete progress" ON user_progress;
CREATE POLICY "Users can delete progress" ON user_progress
    FOR DELETE USING (true);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to update updated_at
DROP TRIGGER IF EXISTS update_problems_updated_at ON problems;
CREATE TRIGGER update_problems_updated_at
    BEFORE UPDATE ON problems
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_progress_updated_at ON user_progress;
CREATE TRIGGER update_user_progress_updated_at
    BEFORE UPDATE ON user_progress
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


DROP POLICY IF EXISTS "Users can delete progress" ON user_progress;
CREATE POLICY "Users can delete progress" ON user_progress
    FOR DELETE USING (true);

ALTER TABLE user_progress ADD COLUMN IF NOT EXISTS in_revision BOOLEAN DEFAULT FALSE;

SELECT setval('problems_id_seq', (SELECT MAX(id) FROM problems), true);

ALTER TABLE problems ADD COLUMN IF NOT EXISTS solution_text TEXT;

---=============Add company tags =====================


-- Company tags table
create table if not exists company_tags (
    id bigserial primary key,
    name text unique not null
);

-- Junction table between problems and company_tags
create table if not exists problem_company_tags (
    id bigserial primary key,
    problem_id integer not null references problems(id) on delete cascade,
    tag_id integer not null references company_tags(id) on delete cascade,
    unique(problem_id, tag_id)
);

-- Basic permissive policies (adjust in Supabase dashboard if using RLS)
alter table company_tags enable row level security;
alter table problem_company_tags enable row level security;

do $$ begin
    if not exists (
        select 1 from pg_policies where schemaname = 'public' and tablename = 'company_tags' and policyname = 'Allow all on company_tags'
    ) then
        create policy "Allow all on company_tags" on company_tags for all using (true) with check (true);
    end if;
    if not exists (
        select 1 from pg_policies where schemaname = 'public' and tablename = 'problem_company_tags' and policyname = 'Allow all on problem_company_tags'
    ) then
        create policy "Allow all on problem_company_tags" on problem_company_tags for all using (true) with check (true);
    end if;
end $$;


