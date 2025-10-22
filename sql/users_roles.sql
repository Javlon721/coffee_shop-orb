create table
  if not exists users_roles (
    id serial primary key,
    user_id int references users (user_id),
    role_id int references roles (role_id)
  )