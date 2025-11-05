from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from src.db.models import INT_PK, Base


class VerificationsORM(Base):
  
  __tablename__ = "verifications"
  
  id: Mapped[INT_PK]
  user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), unique=True)
  token: Mapped[str]
  expires_at: Mapped[datetime]