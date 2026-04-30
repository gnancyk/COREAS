from fastapi import APIRouter, Depends
from typing import List
import uuid
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.crm.service import CRMService
from app.schemas.batch import BatchBaseRequest
from app.models.environment import Serveur

router = APIRouter(prefix="/crm", tags=["CRM Dynamics"])

@router.post("/services/verification")
async def verifier_services_crm(payload: BatchBaseRequest, current_user: str = Depends(get_current_user)):
    """
    Vérifie l'état des services MSCRM (Async & Sandbox) et affiche les comptes de démarrage.
    """
    results = CRMService.verifier_services_crm(payload.servers, payload.username, payload.password)
    return {"results": results}

@router.post("/services/environnement/{environnement_id}")
async def verifier_services_crm_environnement(
    environnement_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Vérifie les services CRM sur tous les serveurs d'un environnement (Zéro Saisie).
    """
    serveurs = db.query(Serveur).filter(Serveur.environnement_id == environnement_id).all()
    if not serveurs:
        return {"results": []}
    
    results = []
    for srv in serveurs:
        # Filtrage : l'audit CRM n'a de sens que sur les serveurs CRM
        role_nom = srv.role.nom.upper() if srv.role else ""
        if "CRM" not in role_nom:
            continue

        # Utilisation du nom d'hôte (sans instance) pour WinRM
        target = srv.nom_hote or srv.nom_serveur or srv.adresse_ip
        
        srv_results = CRMService.verifier_services_crm(
            [target], 
            srv.identifiant, 
            srv.mot_de_passe
        )
        # On remet le nom complet pour l'affichage frontend
        for r in srv_results:
            r["server"] = srv.nom_serveur
            
        results.extend(srv_results)
    
    return {"results": results}
