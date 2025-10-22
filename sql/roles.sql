DROP table if EXISTS users CASCADE;

create table
  if not exists roles (
    role_id serial primary key,
    role varchar(50) not null unique
  )