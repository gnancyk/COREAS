from fastapi import APIRouter, Depends
from typing import List
from app.core.security import get_current_user
from app.schemas.batch import (
    ServiceCheckRequest, ServiceCheckResponse,
    DateTimeResponse, BatchBaseRequest,
    CriteriaCheckRequest, CriteriaResponse,
    DynamicAuditRequest, DynamicAuditResponse,
    SQLConnectRequest, SQLConnectResponse,
    ComplianceCheckRequest, ComplianceCheckResponse
)
from app.services.batch.service import BatchService
from app.services.infra.service import InfraService
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.environment import Environnement, Serveur, Role
import uuid

router = APIRouter(prefix="/batch", tags=["Batch & Services Audit"])

@router.post("/services/verification", response_model=ServiceCheckResponse)
async def verifier_services(payload: ServiceCheckRequest, current_user: str = Depends(get_current_user)):
    """
    Vérifie l'état des services Windows (SAPHIRV3, ASP.NET State, etc.)
    """
    results = BatchService.verifier_services_windows(payload.servers, payload.services, payload.username, payload.password)
    return {"results": results}

@router.post("/datetime/verification", response_model=DateTimeResponse)
async def verifier_datetime(payload: BatchBaseRequest, current_user: str = Depends(get_current_user)):
    """
    Vérifie la synchronisation de la date et de l'heure sur les serveurs.
    """
    results = BatchService.verifier_datetime(payload.servers, payload.username, payload.password)
    return {"results": results}

@router.post("/criteres/verification", response_model=CriteriaResponse)
async def verifier_criteres(payload: CriteriaCheckRequest, current_user: str = Depends(get_current_user)):
    """
    Vérifie l'existence des fichiers de critères sur les serveurs Batch.
    """
    results = BatchService.verifier_existence_fichiers(payload.servers, payload.file_paths, payload.username, payload.password)
    return {"results": results}

@router.post("/webdeploy/verification")
async def verifier_webdeploy(payload: BatchBaseRequest, current_user: str = Depends(get_current_user)):
    """
    Vérifie que le package Web Deploy est bien installé via le module Infra.
    """
    results = InfraService.verifier_fonctionnalites(payload.servers, ["Web-Deploy"], payload.username, payload.password)
    return {"results": results}

@router.post("/http/sante")
async def verifier_http(payload: List[str], current_user: str = Depends(get_current_user)):
    """
    Vérifie les réponses HTTP (200 OK) pour une liste d'URLs.
    """
    results = BatchService.verifier_sante_http(payload)
    return {"results": results}

@router.post("/audit-dynamique", response_model=DynamicAuditResponse)
async def auditer_dynamique(payload: DynamicAuditRequest, current_user: str = Depends(get_current_user)):
    """
    Lance un audit complet en mode découverte automatique (recherche .config, critères et pools).
    """
    results = BatchService.auditer_dynamique_saphir(payload.servers, payload.search_roots, payload.username, payload.password)
    return {"results": results}

@router.post("/sql/connexion", response_model=SQLConnectResponse)
async def tester_sql(payload: SQLConnectRequest, current_user: str = Depends(get_current_user)):
    """
    Teste si le serveur Batch peut atteindre l'instance SQL (Test de port réseau).
    """
    results = BatchService.tester_connexion_sql_remote(payload.servers, payload.sql_instance, payload.port, payload.username, payload.password)
    return {"results": results}


@router.post("/conformite/centralisation", response_model=ComplianceCheckResponse)
async def verifier_conformite_centralisation(payload: ComplianceCheckRequest, current_user: str = Depends(get_current_user)):
    """
    Audit de conformité : vérifie si le paramètre CentralisationParamEndPoint dans les .config
    est identique à l'URL CentralParam de référence.
    """
    results = BatchService.verifier_conformite_centralisation(
        payload.servers, 
        payload.central_param_url, 
        payload.saphir_modules, 
        payload.username, 
        payload.password
    )
    return {"results": results}


@router.post("/audit/environnement/{environnement_id}", response_model=DynamicAuditResponse)
async def auditer_environnement_dynamique(
    environnement_id: uuid.UUID, 
    search_roots: List[str] = ["C:\\inetpub", "C:\\Program Files\\gs2E2"],
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    """
    Lance un audit dynamique sur TOUS les serveurs d'un environnement (Zéro Saisie).
    Récupère automatiquement les credentials en base.
    """
    serveurs = db.query(Serveur).filter(Serveur.environnement_id == environnement_id).all()
    if not serveurs:
        return {"results": []}
    
    results = []
    for srv in serveurs:
        # Filtrage : l'audit dynamique (IIS/Config) n'a de sens que sur Web ou Batch
        role_nom = srv.role.nom.upper() if srv.role else ""
        if "WEB" not in role_nom and "BATCH" not in role_nom:
            continue

        # Utilisation du nom d'hôte (sans instance) pour WinRM
        target = srv.nom_hote or srv.nom_serveur or srv.adresse_ip
        
        srv_results = BatchService.auditer_dynamique_saphir(
            [target], 
            search_roots, 
            srv.identifiant, 
            srv.mot_de_passe
        )
        # On remet le nom complet pour l'affichage frontend
        for r in srv_results:
            r["server"] = srv.nom_serveur
            
        results.extend(srv_results)
        
    return {"results": results}

@router.post("/services/environnement/{environnement_id}", response_model=ServiceCheckResponse)
async def verifier_services_environnement(
    environnement_id: uuid.UUID, 
    services: List[str] = ["SAPHIRV3*", "aspnet_state", "W3SVC"],
    db: Session = Depends(get_db), 
    current_user: str = Depends(get_current_user)
):
    """
    Vérifie les services Windows sur tous les serveurs d'un environnement (Zéro Saisie).
    """
    serveurs = db.query(Serveur).filter(Serveur.environnement_id == environnement_id).all()
    if not serveurs:
        return {"results": []}
    
    results = []
    for srv in serveurs:
        # Utilisation du nom d'hôte (sans instance) pour WinRM
        target = srv.nom_hote or srv.nom_serveur or srv.adresse_ip
        
        srv_results = BatchService.verifier_services_windows(
            [target], 
            services, 
            srv.identifiant, 
            srv.mot_de_passe
        )
        # On remet le nom complet pour l'affichage frontend
        for r in srv_results:
            r["server"] = srv.nom_serveur
            
        results.extend(srv_results)
        
    return {"results": results}
