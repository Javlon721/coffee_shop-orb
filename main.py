from fastapi import FastAPI

from users.repository import UsersRepository
from users.router import users_router
from auth.router import auth_router
from users_roles.router import users_roles_router
from roles.router import roles_router


app = FastAPI()


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(users_roles_router)
app.include_router(roles_router)


@app.get('/test')
def test():
  return UsersRepository.get_user(1)