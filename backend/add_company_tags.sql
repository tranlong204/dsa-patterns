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


