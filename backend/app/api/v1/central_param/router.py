from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.central_param import (
    UrlControlRequest, 
    ControlResponse, 
    ParamRequest, 
    CentralParamResponse, 
    ParamItem,
    ConformityResponse
)
from app.services.central_param.service import CentralParamService

router = APIRouter(prefix="/central_param", tags=["Central Param (SOAP)"])

@router.post("/controle", response_model=ControlResponse)
async def verifier_service(
    payload: UrlControlRequest, 
    current_user: str = Depends(get_current_user)
):
    """
    Vérifie la syntaxe et l'accessibilité d'un service CentralParam.
    """
    if not CentralParamService.verifier_syntaxe_url(payload.url):
        return {
            "is_valid": False,
            "message": "Syntaxe d'URL incorrecte (doit inclure http/https et un domaine/hôte)"
        }
    
    result = CentralParamService.verifier_service_soap(payload.url)
    message = "Url du centralParam soumis est correct" if result["is_wcf"] else "Url du centralParam n'est pas un service svc"
    
    return {
        "url": payload.url,
        "is_valid_syntax": True,
        "is_wcf_service": result["is_wcf"],
        "status_code": result["status_code"],
        "health_check": result["health_check"],
        "message": message
    }

@router.post("/parametres", response_model=CentralParamResponse)
async def obtenir_tous_parametres(
    payload: UrlControlRequest, 
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère tous les paramètres d'un service CentralParam.
    """
    try:
        results = CentralParamService.extraire_parametres(payload.url)
        return CentralParamResponse(
            url=payload.url,
            count=len(results),
            parameters=[ParamItem(**p) for p in results]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/conforme", response_model=ConformityResponse)
async def verifier_conformite(payload: UrlControlRequest, current_user: str = Depends(get_current_user)):
    """
    Vérification complète : Validité technique + Présence et vérification de CrmConnectionString.
    """
    syntax_valid = CentralParamService.verifier_syntaxe_url(payload.url)
    if not syntax_valid:
        return {
            "url": payload.url,
            "is_valid_syntax": False,
            "is_wcf_service": False,
            "param_count": 0,
            "is_conforme": False,
            "health_check": "Invalide",
            "message": "Url du centralParam est incorrect (Syntaxe)"
        }
    
    result = CentralParamService.verifier_service_soap(payload.url)
    param_count = 0
    is_conforme = False
    message = ""

    if result["is_wcf"]:
        try:
            params = CentralParamService.extraire_parametres(payload.url, filter_list=["CrmConnectionString"])
            param_count = len(params)
            
            if param_count > 0:
                crm_conn = params[0].get("value", "")
                if crm_conn and str(crm_conn).strip():
                    is_conforme = True
                    message = "CentralParam conforme (CrmConnectionString présent et renseigné)"
                else:
                    message = "CentralParam non conforme (CrmConnectionString est vide ou page blanche)"
            else:
                message = "CentralParam non conforme (paramètre CrmConnectionString introuvable)"
        except Exception as e:
            param_count = 0
            message = "CentralParam non conforme (Erreur à l'extraction)"
    else:
        message = "Service inaccessible ou non WCF"

    return {
        "url": payload.url,
        "is_valid_syntax": True,
        "is_wcf_service": result["is_wcf"],
        "param_count": param_count,
        "is_conforme": is_conforme,
        "health_check": result["health_check"],
        "message": message
    }

@router.post("/parametre", response_model=ParamItem)
async def obtenir_un_parametre(
    payload: ParamRequest, 
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupère un paramètre spécifique, le parse et enregistre un snapshot.
    """
    if not payload.param_name:
        raise HTTPException(status_code=400, detail="param_name est requis")
        
    try:
        results = CentralParamService.extraire_parametres(payload.url, filter_list=[payload.param_name])
        if not results:
            raise HTTPException(status_code=404, detail=f"Paramètre '{payload.param_name}' non trouvé")
            
        param = results[0]
        # On enregistre le snapshot en base
        CentralParamService.enregistrer_snapshot(db, payload.url, param, current_user)
        
        return ParamItem(**param)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/historique", response_model=List[Dict])
async def obtenir_historique_snapshots(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Récupère l'historique des snapshots enregistrés en base de données.
    """
    from app.models.verification import VerificationConfigurations
    snapshots = db.query(VerificationConfigurations).order_by(VerificationConfigurations.created_at.desc()).limit(limit).all()
    return [
        {
            "id": s.id,
            "url": s.wsdl_url,
            "param_name": s.param_name,
            "param_value": s.param_value,
            "parsed_json": s.parsed_json,
            "created_at": s.created_at,
            "created_by": s.created_by
        }
        for s in snapshots
    ]
