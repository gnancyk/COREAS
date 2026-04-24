from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.core.database import Base

class VerificationConfigurations(Base):
    """
    Ancien modèle gardé temporairement pour éviter les erreurs, à nettoyer si plus utile.
    """
    __tablename__ = "verification_configurations"

    id = Column(Integer, primary_key=True, index=True)
    wsdl_url = Column(String(500), index=True)
    param_name = Column(String(255), index=True)
    param_value = Column(String)
    parsed_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100))

class Module(Base):
    __tablename__ = "Module"
    
    module_id = Column(UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), nullable=False, unique=True)
    nom = Column(String(255))
    est_requis = Column(Boolean, default=True)

class Controle(Base):
    __tablename__ = "Controle"
    
    controle_id = Column(UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, default=uuid.uuid4)
    point_controle = Column(String(50), nullable=False, unique=True)
    description = Column(String)
    valeur_attendue = Column(String)
    chemin_endpoint = Column(String)
    delai_secondes = Column(Integer, default=30)
    module_id = Column(UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("Module.module_id"), nullable=False)
    
    module = relationship("Module")

class Verification(Base):
    __tablename__ = "Verification"
    
    verification_id = Column(UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, default=uuid.uuid4)
    environnement_id = Column(UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("Environnement.environnement_id"), nullable=False)
    utilisateur_id = Column(UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("Utilisateur.utilisateur_id"), nullable=False)
    date_debut = Column(DateTime, default=datetime.utcnow)
    date_fin = Column(DateTime)
    statut_global = Column(String(50))
    total_tests = Column(Integer, default=0)
    total_ok = Column(Integer, default=0)
    total_ko = Column(Integer, default=0)
    total_avertissements = Column(Integer, default=0)
    
    environnement = relationship("Environnement")
    utilisateur = relationship("Utilisateur")

class CaptureConfig(Base):
    __tablename__ = "CaptureConfig"
    
    capture_config_id = Column(UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verification_id = Column(UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("Verification.verification_id"), nullable=False, unique=True)
    params_json = Column(String) # NVARCHAR(MAX)
    capture_le = Column(DateTime, default=datetime.utcnow)
    
    verification = relationship("Verification")

class VerificationModule(Base):
    __tablename__ = "VerificationModule"
    
    verification_module_id = Column(UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verification_id = Column(UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("Verification.verification_id"), nullable=False)
    module_id = Column(UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("Module.module_id"), nullable=False)
    statut = Column(String(50))
    total_tests = Column(Integer, default=0)
    total_ok = Column(Integer, default=0)
    total_ko = Column(Integer, default=0)
    
    verification = relationship("Verification")
    module = relationship("Module")

class ResultatControle(Base):
    __tablename__ = "ResultatControle"
    
    resultat_controle_id = Column(UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verification_module_id = Column(UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("VerificationModule.verification_module_id"), nullable=False)
    controle_id = Column(UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("Controle.controle_id"), nullable=False)
    serveur_id = Column(UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("Serveur.serveur_id"), nullable=False)
    statut = Column(String(50))
    valeur_observee = Column(String)
    valeur_attendue = Column(String)
    message_erreur = Column(String)
    details = Column(String)
    duree_ms = Column(Integer)
    
    verification_module = relationship("VerificationModule")
    controle = relationship("Controle")
    serveur = relationship("Serveur")

class ResultatServeur(Base):
    __tablename__ = "ResultatServeur"
    
    resultat_serveur_id = Column(UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verification_id = Column(UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("Verification.verification_id"), nullable=False)
    serveur_id = Column(UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("Serveur.serveur_id"), nullable=False)
    statut = Column(String(50))
    details = Column(String)
    temps_reponse_ms = Column(Integer)
    
    verification = relationship("Verification")
    serveur = relationship("Serveur")
