DROP table if EXISTS verifications;

create table
  if not exists verifications (
    id serial primary key,
    user_id int references users(user_id) unique,
    token varchar not null,
    expires_at timestamptz not null
  );

