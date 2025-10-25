from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from roles.repository import RolesRepository
from users.repository import UsersRepository
from users.router import users_router
from auth.router import auth_router
from users_roles.router import users_roles_router
from roles.router import roles_router
from db.connection import ConnectionManager, create_db_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
  # await create_db_tables()

  async with ConnectionManager.get_session_ctx() as session:
    # await UsersRepositoryNew.truncate_table(session)
    # await RolesRepository.insert_default_roles(session)
    pass

  yield

  print("do clean up")


app = FastAPI(lifespan=lifespan)


app.include_router(auth_router)

app.include_router(users_router)

app.include_router(users_roles_router)
app.include_router(roles_router)


@app.get('/test')
async def test(session: Annotated[AsyncSession, Depends(ConnectionManager.get_session)]):
    result = await session.execute(text("select now()"))
    return result.scalar_one()