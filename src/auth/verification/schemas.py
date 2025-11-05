from datetime import datetime

from pydantic import BaseModel


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
