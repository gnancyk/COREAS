from sqlalchemy import Column, String, DateTime
from datetime import datetime
from app.core.database import Base

class BlacklistedToken(Base):
    """
    Modèle pour stocker les tokens JWT révoqués (logout).
    """
    __tablename__ = "blacklisted_tokens"

    token = Column(String(500), primary_key=True, index=True)
    blacklisted_at = Column(DateTime, default=datetime.utcnow)
