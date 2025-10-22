
from abc import ABC, abstractmethod
from typing import Any


class DB(ABC):
  
  @abstractmethod
  def query(self, query: str, *args: Any) -> Any: 
    raise NotImplemented


  @abstractmethod
  def query_one(self, query: str, *args: Any) -> Any: 
    raise NotImplemented