DROP table if EXISTS users_roles;

create table
  if not exists users_roles (
    id serial primary key,
    user_id int,
    role_id int,
    created_at timestamptz not null DEFAULT now (),
    UNIQUE (user_id, role_id),
    foreign key (user_id) references users (user_id) on delete cascade,
    foreign key (role_id) references roles (role_id) on delete cascade
  )