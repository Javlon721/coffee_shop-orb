from datetime import timedelta

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert


from auth.config import AuthConfig
from auth.utils import generate_verification_token, get_expiration_time, get_utc_time
from auth.verification.models import Verification, VerificationToken, VerificationsORM


class VerificationRepository:
  
  @staticmethod
  async def add(session: AsyncSession, user_id: int) -> VerificationToken | None:
    default_time_delta = timedelta(days=AuthConfig.VERIFICATION_TOKEN_EXPIRE_DAYS)

    expires_at = get_expiration_time(default_time_delta)
    token = generate_verification_token()

    stmt = (
      insert(VerificationsORM)
      .values(user_id=user_id, token=token, expires_at=expires_at)
      .returning(VerificationsORM.id)
    )

    result = await session.scalar(stmt)

    await session.commit()

    if result is None:
      return None

    return VerificationToken(token=token)

  @staticmethod
  async def get(session: AsyncSession, token: str) -> Verification | None:
    now = get_utc_time()

    query = select(VerificationsORM).filter(and_(VerificationsORM.token==token, VerificationsORM.expires_at >= now))

    data = await session.scalar(query)

    if data is None:
      return None

    return Verification.model_validate(data, from_attributes=True)