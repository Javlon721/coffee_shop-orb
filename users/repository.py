
from fastapi import HTTPException, status
from auth.utils import hash_password
from db.connection import PsycopgDB
from db.models import DB
from users.models import OKResponce, RegisterUser, User


class _UsersRepository:

  table = "users"
  return_id = "user_id"


  def __init__(self, db: DB):
    self.db = db


  def create(self, user: RegisterUser) -> OKResponce:
    if self.isUserExist(user.email):
      raise HTTPException(detail=f"user {user.email} already exists", status_code=status.HTTP_400_BAD_REQUEST)

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


  def get_user(self, user_id: int) -> User:
    result = self.db.query_one(f"SELECT * FROM {self.table} WHERE user_id = %s", user_id)

    if not result:
      raise HTTPException(detail=f"user {user_id} does not exists", status_code=status.HTTP_404_NOT_FOUND)

    return User(
      user_id=result[0],
      email=result[1],
      password=result[2],
      first_name=result[3],
      last_name=result[4],
      is_verified=result[5],
      created_at=result[6],
    ) # type: ignore


  def delete_user(self, user_id: int) -> OKResponce:
    result = self.db.query_one(f"DELETE FROM {self.table} WHERE user_id = %s RETURNING {self.return_id}", user_id)

    if not result:
      raise HTTPException(detail=f"user {user_id} does not exists", status_code=status.HTTP_400_BAD_REQUEST)

    return OKResponce(ok=True, user_id=result[0])


  def isUserExist(self, email: str) -> bool:
    result = self.db.query_one(f"SELECT user_id FROM {self.table} WHERE email = %s", email)

    return bool(result)


UsersRepository = _UsersRepository(PsycopgDB)