
from fastapi import APIRouter

# from auth.verification.models import VerificationsORM
# from auth.verification.repository import VerificationRepository
from src.auto_deletions.celery_app import delete_expired_users_task
# from db.connection import AsyncSessionDepends
# from users.models import  UsersORM
# from users.repository import UsersRepository
# from auto_deletions.raw_data import raw_verifications, raw_users


celery_router = APIRouter(prefix="/celery", tags=["celery"])


# @celery_router.get("/")
# async def task(session: AsyncSessionDepends):
#   """
#   Be aware of using this endpoint. It erases all DB data and inserts MOCK one
#   """  
#   await UsersRepository.truncate_table(session)
#   await VerificationRepository.truncate_table(session)
  
#   users = [UsersORM(**info) for info in raw_users]
  
#   session.add_all(users)
#   await session.commit()
  
#   verifications = []
#   for user in users:
#     verification = VerificationsORM(user_id=user.user_id, expires_at=raw_verifications[user.user_id], token="moch")
#     verifications.append(verification)
  
#   session.add_all(verifications)
#   await session.commit()


@celery_router.get("/expire")
async def delete_expired_users():
  """
  Manually removes from DB expired users by calling *celery* task `delete_expired_users_task`
  """  

  result = delete_expired_users_task.delay()
  
  return result.get()