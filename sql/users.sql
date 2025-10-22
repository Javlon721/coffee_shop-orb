create table
  if not exists users (
    user_id serial primary key,
    email varchar(150) not null unique,
    password varchar(30) not null,
    first_name varchar(50),
    last_name varchar(50),
    is_verified boolean default FALSE
  )