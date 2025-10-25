from typing import Any
from psycopg_pool import ConnectionPool

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from db.config import DBConfig
from db.models import DB


class _PsycopgDB(DB):
  
  def __init__(self) -> None:
    self.pool = ConnectionPool(
      DBConfig.URI,
      max_size=DBConfig.CONNECTION_POOL_MAX_SIZE
    )


  def query(self, query: str, *args: Any) -> list[Any]:
    with self.pool.connection() as conn:
      result = conn.execute(query, args) # type: ignore
      
      return result.fetchall()


  def query_one(self, query: str, *args: Any) -> Any: 
    with self.pool.connection() as conn:
      result = conn.execute(query, args) # type: ignore
      
      return result.fetchone()


  def execute(self, query: str, *args: Any) -> Any: 
    return self.query_one(query, *args)


PsycopgDB = _PsycopgDB()

engine = create_async_engine(
  DBConfig.DNS,  
  echo=DBConfig.ORM_ECHO, 
  pool_size=DBConfig.CONNECTION_POOL_SIZE, 
  max_overflow=DBConfig.CONNECTION_POOL_MAX_SIZE
)

session_factory = async_sessionmaker(engine)