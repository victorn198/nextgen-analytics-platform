create schema if not exists raw;

create table if not exists raw.github_repositories (
    repository_id bigint primary key,
    repository_name text not null,
    repository_full_name text not null,
    description text,
    language text,
    stars integer not null default 0,
    forks integer not null default 0,
    open_issues integer not null default 0,
    is_archived boolean not null default false,
    created_at timestamptz,
    updated_at timestamptz,
    collected_at timestamptz not null default now()
);
