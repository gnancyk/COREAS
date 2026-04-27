from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class CategorieBase(BaseModel):
    nom: str

class CategorieCreate(CategorieBase):
    pass

class CategorieResponse(CategorieBase):
    categorie_id: UUID

    class Config:
        from_attributes = True

class EnvironnementBase(BaseModel):
    nom: str
    url_central_param: str
    categorie_id: UUID

class EnvironnementCreate(EnvironnementBase):
    pass

class EnvironnementResponse(EnvironnementBase):
    environnement_id: UUID
    est_actif: bool
    categorie: CategorieResponse

    class Config:
        from_attributes = True

class RoleBase(BaseModel):
    nom: str

class RoleResponse(RoleBase):
    role_id: UUID

    class Config:
        from_attributes = True

class ServeurBase(BaseModel):
    nom_serveur: str
    nom_hote: Optional[str] = None
    adresse_ip: Optional[str] = None
    role_id: UUID
    environnement_id: UUID
    port_winrm: Optional[int] = 5985
    port: Optional[int] = None
    identifiant: Optional[str] = None
    mot_de_passe: Optional[str] = None

class ServeurResponse(ServeurBase):
    serveur_id: UUID
    role: Optional[RoleResponse] = None
    environnement: Optional[EnvironnementResponse] = None

    class Config:
        from_attributes = True
