from contextlib import _AsyncGeneratorContextManager, asynccontextmanager
from typing import Annotated, Any, AsyncGenerator, Callable

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine, AsyncSession, AsyncConnection

from db.config import DBConfig
from db.models import  Base


class _ConnectionManager:
  """
  :param url: string db connection url
  
  :param echo: optional bool whether SQLAlchemy should log all executed SQL statements.
  
  :param pool_size: optional number of connections to keep in the connection pool.

  :param pool_size: optional number maximum number of connections that can be created above `pool_size`.
  
  Methods `get_session` and `get_connection` return AsyncSession for DI in endpoints.

  Otherwise `get_session_ctx` and `get_conn_ctx` can be used directly in context managers
  """  
  def __init__(
      self,
      url: str,
      echo: bool = False,
      pool_size: int = 5,
      max_overflow: int = 10
  ) -> None:
    self.engine: AsyncEngine = (
      create_async_engine(
            url=url,  
            echo=echo, 
            pool_size=pool_size, 
            max_overflow=max_overflow
      )
    )
    self.session_factory: async_sessionmaker[AsyncSession] = (
      async_sessionmaker(
        bind=self.engine, 
        expire_on_commit=False, 
        autocommit=False,
        autoflush=False
      )
    )


  async def dispose(self):
    await self.engine.dispose()


  async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
    async with self.session_factory() as session:
        yield session


  def get_session_ctx(self)->_AsyncGeneratorContextManager[AsyncSession, None]:
    return  self.get_ctx_manager_from(self.get_session)


  async def get_connection(self)->AsyncGenerator[AsyncConnection, None]:
    async with self.engine.begin() as conn:
      yield conn


  def get_conn_ctx(self) -> _AsyncGeneratorContextManager[AsyncConnection, None]:
    return self.get_ctx_manager_from(self.get_connection)


  def get_ctx_manager_from(self, generator: Callable[[], AsyncGenerator[Any, None]]):
    return asynccontextmanager(generator)()


ConnectionManager = _ConnectionManager(
  url=DBConfig.DNS,
  echo=DBConfig.ORM_ECHO,
  pool_size=DBConfig.CONNECTION_POOL_SIZE,
  max_overflow=DBConfig.CONNECTION_POOL_MAX_SIZE
)

AsyncSessionDepends = Annotated[AsyncSession, Depends(ConnectionManager.get_session)]


async def create_db_tables():
  async with ConnectionManager.get_conn_ctx() as conn:
    await conn.run_sync(Base.metadata.drop_all)
    await conn.run_sync(Base.metadata.create_all)