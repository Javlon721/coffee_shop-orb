
from fastapi import HTTPException, status
from sqlalchemy import delete, insert, text, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth.utils import hash_password
from users.models import OKResponce, RegisterUser, UpdateUser, User, UsersORM


class UsersRepository:

  @staticmethod
  async def create_user(session: AsyncSession, user: RegisterUser) -> OKResponce | None:
    if await UsersRepository.isUserExist(session, email=user.email):
      return None

    hashed_password = hash_password(user.password)
    user.set_hashed_password(hashed_password)

    stmt = insert(UsersORM).values(**user.model_dump()).returning(UsersORM.user_id)

    result = await session.execute(stmt)

    await session.commit()

    return OKResponce(ok=True, user_id=result.scalar_one())


  @staticmethod
  async def get_user(session: AsyncSession, **kwargs) -> User | None:
    query = select(UsersORM).filter_by(**kwargs)

    data = await session.scalar(query)

    if data is None:
      return None

    return User.model_validate(data, from_attributes=True)


  @staticmethod
  async def get_users(session: AsyncSession) -> list[User] | None:
    query = select(UsersORM)

    data = await session.scalars(query)

    if data is None:
      return None

    return [User.model_validate(el, from_attributes=True) for el in data]


  @staticmethod
  async def delete_user(session: AsyncSession, user_id: int) -> OKResponce | None:
    stmt = delete(UsersORM).filter_by(user_id=user_id).returning(UsersORM.user_id)

    result = await session.scalar(stmt)

    await session.commit()

    if result is None:
      return None

    return OKResponce(ok=True, user_id=result)


  @staticmethod
  async def update_user(session: AsyncSession, user_id: int, user: UpdateUser) -> OKResponce:
    user_in_db = await UsersRepository.get_user(session, user_id=user_id)
    
    if user_in_db is None:
      raise HTTPException(detail=f"user {user_id} not exists", status_code=status.HTTP_404_NOT_FOUND)

    if user.email:
      if user_in_db.email == user.email or await UsersRepository.isUserExist(session, email=user.email):
        raise HTTPException(detail=f"user {user.email} already exists", status_code=status.HTTP_400_BAD_REQUEST)

    stmt = (
      update(UsersORM)
        .values(**user.model_dump(exclude_none=True, exclude_defaults=True))
        .filter_by(user_id=user_id)
        .returning(UsersORM.user_id)
    )

    result = await session.scalar(stmt)

    await session.commit()

    assert result is not None

    return OKResponce(ok=True, user_id=result)


  @staticmethod
  async def verify_user(session: AsyncSession, user_id: int) -> OKResponce | None:
    stmt = (
      update(UsersORM)
      .values(is_verified=True)
      .filter_by(user_id=user_id, is_verified=False)
      .returning(UsersORM.user_id)
    )

    result = await session.scalar(stmt)

    await session.commit()

    if result is None:
      return None

    return OKResponce(ok=True, user_id=result)


  @staticmethod
  async def isUserExist(session: AsyncSession, **kwrgs) -> bool:
    query = select(UsersORM.user_id).filter_by(**kwrgs)

    result = await session.scalars(query)

    if result.first() is None:
      return False

    return True


  @staticmethod
  async def truncate_table(session: AsyncSession):
    await session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE"))
    await session.commit()