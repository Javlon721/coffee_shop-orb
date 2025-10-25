from datetime import datetime

from pydantic import BaseModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from db.models import INT_PK, Base


class VerificationToken(BaseModel):
  token: str


class RegisterVerification(BaseModel):
  user_id: int
  token: str
  expires_at: datetime


class Verification(RegisterVerification):
  id: int


class OKResponce(BaseModel):
  ok: bool
  id: int
  token: str


class VerificationsORM(Base):
  
  __tablename__ = "verifications"
  
  id: Mapped[INT_PK]
  user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), unique=True)
  token: Mapped[str]
  expires_at: Mapped[datetime]