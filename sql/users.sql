DROP table if EXISTS users CASCADE;

create table
  if not exists users (
    user_id serial primary key,
    email varchar(150) not null unique,
    password varchar(150) not null,
    first_name varchar(50),
    last_name varchar(50),
    is_verified boolean default FALSE,
    created_at timestamptz not null DEFAULT now ()
  )