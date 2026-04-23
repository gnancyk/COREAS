from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.core.security import get_current_user
from app.schemas.sql_server import (
    SQLAuditBaseRequest, FragmentationResponse, 
    MissingIndexResponse, TriggerResponse, 
    OrgIdResponse, CatalogResponse
)
from app.services.sql_server.service import SQLService

router = APIRouter(prefix="/sql", tags=["SQL Server Audit"])

@router.post("/audit/performance", response_model=dict)
async def audit_performance(payload: SQLAuditBaseRequest, current_user: str = Depends(get_current_user)):
    """
    Analyse de la fragmentation des index et détection des index manquants.
    """
    try:
        fragmentation = SQLService.verifier_indices_fragmentation(payload.db_name)
        missing = SQLService.verifier_indices_manquants(payload.db_name)
        return {
            "database": payload.db_name,
            "fragmentation_results": fragmentation,
            "missing_index_results": missing
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'audit SQL : {str(e)}")

@router.post("/audit/conformite", response_model=dict)
async def audit_conformite(payload: SQLAuditBaseRequest, current_user: str = Depends(get_current_user)):
    """
    Vérification des triggers critiques et de la cohérence de l'OrganizationID.
    """
    try:
        triggers = SQLService.verifier_triggers_saphir(payload.db_name)
        orgid = SQLService.verifier_coherence_orgid(payload.db_name)
        return {
            "database": payload.db_name,
            "triggers_results": triggers,
            "organization_consistency": orgid
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'audit SQL : {str(e)}")

@router.post("/audit/catalogues", response_model=CatalogResponse)
async def audit_catalogues(payload: SQLAuditBaseRequest, current_user: str = Depends(get_current_user)):
    """
    Détection des noms de bases de données écrits en dur dans le code SQL.
    """
    try:
        results = SQLService.verifier_catalogues_suspects(payload.db_name)
        return {"database": payload.db_name, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'audit SQL : {str(e)}")
