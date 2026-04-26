from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.core.security import get_current_user
from app.schemas.infra import (
    PortVerificationRequest, PortVerificationResponse,
    FeatureVerificationRequest, FeatureVerificationResponse,
    OSInfoRequest, OSInfoResponse, # Note: I'll need to define OSInfoRequest
    AvailabilityRequest, AvailabilityResponse # Note: Add these too
)
from app.services.infra.service import InfraService

router = APIRouter(prefix="/infra", tags=["Infrastructure Audit"])

@router.post("/port/verification", response_model=PortVerificationResponse)
async def verifier_ports(payload: PortVerificationRequest, current_user: str = Depends(get_current_user)):
    """
    Teste l'ouverture du port 5986 (WinRM HTTPS).
    """
    results = InfraService.verifier_port_5986(payload.servers)
    return {"results": results}

@router.post("/disponibilite/serveur", response_model=AvailabilityResponse)
async def verifier_disponibilite(payload: AvailabilityRequest, current_user: str = Depends(get_current_user)):
    """
    Ping de disponibilité pour une liste de serveurs.
    """
    results = InfraService.verifier_disponibilite(payload.servers)
    return {"results": results}

@router.post("/caracteristiques/serveur", response_model=OSInfoResponse)
async def obtenir_caracteristiques(payload: OSInfoRequest, current_user: str = Depends(get_current_user)):
    """
    Récupération des informations OS (Version, Uptime, CPU). supporte les credentials.
    """
    results = InfraService.obtenir_caracteristiques_os(payload.servers, payload.username, payload.password)
    return {"results": results}

@router.post("/fonctionnalites/verification", response_model=FeatureVerificationResponse)
async def verifier_fonctionnalites(payload: FeatureVerificationRequest, current_user: str = Depends(get_current_user)):
    """
    Prend une liste de fonctionnalités et de serveurs, retourne état installé/non installé.
    """
    results = InfraService.verifier_fonctionnalites(payload.servers, payload.features, payload.username, payload.password)
    return {"results": results}
