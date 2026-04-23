from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from app.core.database import Base

class VerificationConfigurations(Base):
    """
    Modèle pour stocker les snapshots des paramètres récupérés depuis CentralParam.
    """
    __tablename__ = "verification_configurations"

    id = Column(Integer, primary_key=True, index=True)
    wsdl_url = Column(String, index=True)
    param_name = Column(String, index=True)
    param_value = Column(String)
    parsed_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String) # Username de l'utilisateur ayant fait la requête
