
import asyncio

from celery import Celery

from auth.verification.repository import VerificationRepository
from db.connection import ConnectionManager
from users.models import  OKResponce
from users.repository import UsersRepository
from auto_deletions.config import Config


app = Celery(broker=Config.URL, backend=Config.URL)


@app.on_after_configure.connect #type: ignore
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(5, delete_expired_users_task.s(), name='delete expired users')


@app.task
def delete_expired_users_task():
  try:
    result: list[OKResponce] | None = asyncio.run(expired_users())

    if result is None:
      return {'status': 'success', 'deleted_count': 0}

    return {
        'status': 'success',
        'deleted_count': len(result),
        'deleted_users': [el.model_dump() for el in result]
    }
  except Exception as e:
      print(f"Error deleting expired users: {str(e)}")
      return {
          'status': 'error',
          'message': str(e)
      }


async def expired_users() -> list[OKResponce] | None:
  async with ConnectionManager.get_session_ctx() as session:
    expired_users_id = await VerificationRepository.get_expired_users(session)

    if not expired_users_id:
      raise ValueError("expired users not found")

    deleted_users = await UsersRepository.delete_users(session, list(expired_users_id))
    
    return deleted_users