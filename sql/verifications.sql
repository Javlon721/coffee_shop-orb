-- DROP table if EXISTS verifications;
create table
  if not exists verifications (
    id serial primary key,
    user_id int unique,
    token varchar not null,
    expires_at timestamptz not null,
    foreign key (user_id) references users (user_id) on delete cascade
  );