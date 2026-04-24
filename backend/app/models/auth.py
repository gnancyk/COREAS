from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from datetime import datetime
import uuid
from app.core.database import Base

class BlacklistedToken(Base):
    """
    Modèle pour stocker les tokens JWT révoqués (logout).
    """
    __tablename__ = "blacklisted_tokens"

    token = Column(String(500), primary_key=True, index=True)
    blacklisted_at = Column(DateTime, default=datetime.utcnow)

class Utilisateur(Base):
    __tablename__ = "Utilisateur"

    utilisateur_id = Column(UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom_utilisateur = Column(String(255), nullable=False, unique=True)
    nom_complet = Column(String(255))
    email = Column(String(255), nullable=False, unique=True)
