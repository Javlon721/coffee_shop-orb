
from abc import ABC, abstractmethod
from typing import Any
from datetime import datetime
from typing import Annotated

from sqlalchemy.orm import mapped_column
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase


class DB(ABC):
  
  @abstractmethod
  def query(self, query: str, *args: Any) -> Any: 
    raise NotImplemented


  @abstractmethod
  def query_one(self, query: str, *args: Any) -> Any: 
    raise NotImplemented


  @abstractmethod
  def execute(self, query: str, *args: Any) -> Any: 
    raise NotImplemented


class Base(DeclarativeBase):
  pass


INT_PK = Annotated[int, mapped_column(primary_key=True)]
CREATED_AT = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]