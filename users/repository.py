
from typing import Any
from fastapi import HTTPException, status
from auth.utils import hash_password
from db.connection import PsycopgDB
from db.models import DB
from users.models import OKResponce, RegisterUser, UpdateUser, User


# todo: should go when switch to sqlalchemy
def costyil(data: list[Any]) -> User:
  return User(
      user_id=data[0],
      email=data[1],
      password=data[2],
      first_name=data[3],
      last_name=data[4],
      is_verified=data[5],
      created_at=data[6],
    ) # type: ignore


class _UsersRepository:

  table = "users"
  return_id = "user_id"


  def __init__(self, db: DB):
    self.db = db


  def create(self, user: RegisterUser) -> OKResponce | None:
    if self.isUserExist(user.email):
      return None

    hashed_password = hash_password(user.password)
    user.set_hashed_password(hashed_password)

    user_info = user.model_dump(exclude_none=True, exclude_defaults=True)
    columns = ", ".join(user_info.keys())
    values = ", ".join(["%s" for _ in user_info.values()])

    result = self.db.execute(
        f"INSERT INTO {self.table}({columns}) VALUES ({values}) RETURNING {self.return_id}", 
        *user_info.values(),
    )

    return OKResponce(ok=True, user_id=result[0])


  def get_user(self, user_id: int) -> User | None:
    result = self.db.query_one(f"SELECT * FROM {self.table} WHERE user_id = %s", user_id)

    if not result:
      return None

    return costyil(result)


  def get_all_users(self) -> list[User] | None:
    result = self.db.query(f"SELECT * FROM {self.table}")

    if not result:
      return None

    return [costyil(item) for item in result]


  def delete_user(self, user_id: int) -> OKResponce | None:
    result = self.db.query_one(f"DELETE FROM {self.table} WHERE user_id = %s RETURNING {self.return_id}", user_id)

    if result is None:
      return None

    return OKResponce(ok=True, user_id=result[0])


  def update_user(self, user_id: int, user: UpdateUser) -> OKResponce:
    db_user = self.get_user(user_id)

    if db_user is None:
      raise HTTPException(detail=f"user {user_id} not exists", status_code=status.HTTP_404_NOT_FOUND)

    if user.email:
      if self.isUserExist(user.email):
        raise HTTPException(detail=f"user {user.email} already exists", status_code=status.HTTP_400_BAD_REQUEST)

    raw_values = user.model_dump(exclude_none=True, exclude_defaults=True)
    columns = ", ".join([f"{column} = %s" for column in raw_values.keys()])

    result = self.db.query_one(
        f"UPDATE {self.table} SET {columns} WHERE user_id = %s RETURNING {self.return_id}", 
        *raw_values.values(), 
        user_id,
    )

    return OKResponce(ok=True, user_id=result[0])


  def verify_user(self, user_id: int) -> OKResponce | None:
    result = self.db.query_one(
      f"UPDATE {self.table} SET is_verified = TRUE WHERE user_id = %s AND NOT is_verified RETURNING user_id", user_id
    )

    if result is None:
      return None

    return OKResponce(ok=True, user_id=user_id)


  def isUserExist(self, email: str) -> bool:
    result = self.db.query_one(f"SELECT user_id FROM {self.table} WHERE email = %s", email)

    return bool(result)


  def get_login_user(self, email: str) -> User | None:
    result = self.db.query_one(f"SELECT * FROM {self.table} WHERE email = %s", email)

    if not result:
      return None

    return costyil(result)


UsersRepository = _UsersRepository(PsycopgDB)


def get_user_credentials(email: str) -> User | None:
  return UsersRepository.get_login_user(email)