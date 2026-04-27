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
