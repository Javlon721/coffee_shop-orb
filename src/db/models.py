
from datetime import datetime
from typing import Annotated

from sqlalchemy.orm import mapped_column
from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):

  def __repr__(self):
    cols = []
    for col in self.__table__.columns.keys():
        cols.append(f"{col}={getattr(self, col)}")

    return f"<{self.__class__.__name__} {', '.join(cols)}>"


INT_PK = Annotated[int, mapped_column(primary_key=True)]
CREATED_AT = Annotated[datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]