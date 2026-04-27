from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class Categorie(Base):
    __tablename__ = "Categorie"
    
    categorie_id = Column(UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String(255), nullable=False, unique=True)

class Role(Base):
    __tablename__ = "Role"
    
    role_id = Column(UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String(255), nullable=False, unique=True)

class Environnement(Base):
    __tablename__ = "Environnement"
    
    environnement_id = Column(UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String(255), nullable=False, unique=True)
    url_central_param = Column(String)  # NVARCHAR(MAX)
    categorie_id = Column(UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("Categorie.categorie_id"), nullable=False)
    est_actif = Column(Boolean, default=True)
    
    categorie = relationship("Categorie")

class Serveur(Base):
    __tablename__ = "Serveur"
    
    serveur_id = Column(UNIQUEIDENTIFIER(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom_serveur = Column(String(255), nullable=False)
    nom_hote = Column(String(255))
    adresse_ip = Column(String(50))
    role_id = Column(UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("Role.role_id"), nullable=False)
    environnement_id = Column(UNIQUEIDENTIFIER(as_uuid=True), ForeignKey("Environnement.environnement_id"), nullable=False)
    port_winrm = Column(Integer, default=5985)
    port = Column(Integer)
    identifiant = Column(String(255))
    mot_de_passe = Column(String)
    
    role = relationship("Role")
    environnement = relationship("Environnement")
