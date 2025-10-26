

from dataclasses import dataclass
from pydantic import BaseModel
import pytest
import pytest_asyncio
from sqlalchemy import text

from db.config import _DBConfig
from db.connection import _ConnectionManager
from db.models import Base

from roles import models #noqa
from users.models import OKResponce, RegisterUser
from users.repository import UsersRepository
from users_roles import models #noqa
from auth.verification import models #noqa


DBConfig = _DBConfig(_env_file=".env.test") #type: ignore


@pytest_asyncio.fixture(scope="session")
async def conn_manager():

  connectionManager = _ConnectionManager(
    url=DBConfig.DNS,
    echo=DBConfig.ORM_ECHO,
    pool_size=DBConfig.CONNECTION_POOL_SIZE,
    max_overflow=DBConfig.CONNECTION_POOL_MAX_SIZE
  )
  
  connectionManager.engine.echo = False
  async with connectionManager.get_conn_ctx() as conn:
    await conn.run_sync(Base.metadata.create_all)
  
  yield connectionManager
  
  async with connectionManager.get_conn_ctx() as conn:
    await conn.run_sync(Base.metadata.drop_all)
  
  connectionManager.engine.echo = True
  
  print("deleting database")


@pytest.mark.asyncio
async def test_db_connection(conn_manager: _ConnectionManager):
  async with conn_manager.get_session_ctx() as session:
    result = await session.execute(text("select now()"))
    
    assert result.scalar_one() is not None


@pytest.mark.asyncio
@pytest.mark.parametrize("name,user,want", [
    (
        "Test #1",
        {"email":"unique1@mail.com", "password":"qwerty"},
        dict(ok=True, user_id=1)
    ),
    (
        "Test #2",
        dict(email="unique2@mail.com", password="password123"),
        dict(ok=True, user_id=2)
    ),
    (
        "Test #3",
        dict(email="unique1@mail.com", password="qwerty"),
        None
    ),
])
async def test_create_user_parametrized(
    conn_manager: _ConnectionManager,
    name, user, want
):
    async with conn_manager.get_session_ctx() as session:
        new_user = RegisterUser(email=user["email"], password=user["password"])

        result = await UsersRepository.create_user(session, new_user)

        if want is None:
            assert result is None
        else:
            assert result is not None
            assert result.ok == want["ok"]


@pytest.mark.asyncio
@pytest.mark.parametrize("user_id,email", [
      (1, "unique1@mail.com"),
      (2, "unique2@mail.com")
])
async def test_get_user(
    conn_manager: _ConnectionManager,
    user_id, email
):
    async with conn_manager.get_session_ctx() as session:
      result = await UsersRepository.get_user(session, user_id=user_id)
      
      assert result is not None
      
      assert result.email == email


