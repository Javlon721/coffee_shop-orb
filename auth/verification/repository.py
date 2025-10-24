from datetime import timedelta
from auth.config import AuthConfig
from auth.utils import generate_verification_token, get_expiration_time
from auth.verification.models import Verification, VerificationToken
from db.connection import PsycopgDB
from db.models import DB



class _VerificationRepository:

  def __init__(self, db: DB):
    self.db = db


  def add(self, user_id: int) -> VerificationToken | None:
    default_time_delta = timedelta(days=AuthConfig.VERIFICATION_TOKEN_EXPIRE_DAYS)

    expires_at = get_expiration_time(default_time_delta)
    token = generate_verification_token()
    result = self.db.query_one(
      "insert into verifications(user_id, token, expires_at) values (%s, %s, %s) returning id", user_id, token, expires_at
    )

    if not result:
      return None

    return VerificationToken(token=token)


  def get(self, token: str) -> Verification | None:
    result = self.db.query_one("select * from verifications where token = %s and expires_at > now()", token)

    if not result:
      return None

    return Verification(id=result[0], user_id=result[1], token=result[2], expires_at=result[3])



VerificationRepository = _VerificationRepository(PsycopgDB)