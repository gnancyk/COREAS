from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.environment import (
    CategorieCreate, CategorieResponse,
    EnvironnementCreate, EnvironnementResponse
)
from app.models.environment import Categorie, Environnement, Serveur, Role
from app.services.central_param.service import CentralParamService
import re

router = APIRouter(prefix="/environnements", tags=["Environnements & Catégories"])

# --- CATEGORIES ---

@router.get("/categories", response_model=List[CategorieResponse])
async def lister_categories(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Récupère toutes les catégories (ex: Dev, UAT, PROD).
    """
    return db.query(Categorie).all()

@router.post("/categories", response_model=CategorieResponse, status_code=status.HTTP_201_CREATED)
async def creer_categorie(
    payload: CategorieCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Crée une nouvelle catégorie.
    """
    if db.query(Categorie).filter(Categorie.nom == payload.nom).first():
        raise HTTPException(status_code=400, detail="Cette catégorie existe déjà.")
    
    nouvelle_categorie = Categorie(nom=payload.nom)
    db.add(nouvelle_categorie)
    db.commit()
    db.refresh(nouvelle_categorie)
    return nouvelle_categorie

# --- ENVIRONNEMENTS ---

@router.get("/", response_model=List[EnvironnementResponse])
async def lister_environnements(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Récupère tous les environnements configurés.
    """
    return db.query(Environnement).all()

@router.post("/", response_model=EnvironnementResponse, status_code=status.HTTP_201_CREATED)
async def creer_environnement(
    payload: EnvironnementCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Configure un nouvel environnement.
    Vérifie formellement que l'url CentralParam est conforme (CrmConnectionString présent et non vide)
    avant de l'insérer en base.
    """
    # 1. Vérification de la catégorie
    categorie = db.query(Categorie).filter(Categorie.categorie_id == payload.categorie_id).first()
    if not categorie:
        raise HTTPException(status_code=404, detail="La catégorie spécifiée n'existe pas.")
        
    # 2. Vérifier si un environnement avec le même nom existe
    if db.query(Environnement).filter(Environnement.nom == payload.nom).first():
        raise HTTPException(status_code=400, detail="Un environnement avec ce nom existe déjà.")

    # 3. Validation de l'URL via CentralParamService (même logique que /central_param/conforme)
    syntax_valid = CentralParamService.verifier_syntaxe_url(payload.url_central_param)
    if not syntax_valid:
        raise HTTPException(status_code=400, detail="Syntaxe de l'URL CentralParam incorrecte.")

    result = CentralParamService.verifier_service_soap(payload.url_central_param)
    if not result.get("is_wcf"):
        raise HTTPException(status_code=400, detail="Le service CentralParam est inaccessible ou n'est pas un service WCF valide.")

    try:
        params = CentralParamService.extraire_parametres(payload.url_central_param, filter_list=["CrmConnectionString"])
        if len(params) > 0:
            crm_conn = params[0].get("value", "")
            if not (crm_conn and str(crm_conn).strip()):
                raise HTTPException(status_code=400, detail="CentralParam non conforme : le paramètre 'CrmConnectionString' existe mais est vide (page blanche).")
        else:
            raise HTTPException(status_code=400, detail="CentralParam non conforme : le paramètre 'CrmConnectionString' est introuvable sur cette URL.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur lors de la validation du CentralParam : {str(e)}")

    # 4. Si tout est valide, création !
    nouvel_env = Environnement(
        nom=payload.nom,
        url_central_param=payload.url_central_param,
        categorie_id=payload.categorie_id,
        est_actif=True
    )
    db.add(nouvel_env)
    db.commit()
    return nouvel_env

# --- DECOUVERTE SERVEURS ---

def _get_or_create_role(db: Session, role_name: str) -> Role:
    role = db.query(Role).filter(Role.nom == role_name).first()
    if not role:
        role = Role(nom=role_name)
        db.add(role)
        db.commit()
        db.refresh(role)
    return role

@router.post("/{environnement_id}/decouvrir-serveurs")
async def decouvrir_serveurs(
    environnement_id: str,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Parcourt le CentralParam associé à l'environnement pour déduire les serveurs,
    leurs instances, rôles métiers finaux, identifiants, mots de passe et ports.
    """
    env = db.query(Environnement).filter(Environnement.environnement_id == environnement_id).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environnement introuvable.")

    try:
        params = CentralParamService.extraire_parametres(env.url_central_param)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur d'extraction des paramètres: {e}")

    serveurs_trouves = []
    
    for param in params:
        name = param.get("name", "")
        value = param.get("value", "")
        if not value or not str(value).strip():
            continue
            
        role_metier = None
        nom_complet = None
        port = None
        identifiant = None
        mdp = None
        
        # 1. Base de données
        if "Data Source=" in value or "user id=" in value.lower():
            match_ds = re.search(r"Data Source=([^;]+)", value, re.IGNORECASE)
            if match_ds:
                nom_complet = match_ds.group(1).strip()
            
            match_user = re.search(r"User\s*Id=([^;]+)", value, re.IGNORECASE)
            if not match_user:
                match_user = re.search(r"Username=([^;]+)", value, re.IGNORECASE)
            if match_user:
                identifiant = match_user.group(1).strip()
                
            match_pass = re.search(r"Password=([^;]+)", value, re.IGNORECASE)
            if match_pass:
                mdp = match_pass.group(1).strip()
                
            port = 1433
            role_metier = "BD SQL"
            name_lower = name.lower()
            if "crm" in name_lower and "ext" in name_lower: role_metier = "BD Ext CRM"
            elif "crm" in name_lower: role_metier = "BD CRM"
            elif "caisse" in name_lower: role_metier = "BD Caisse"
            elif "saphirpept" in name_lower: role_metier = "BD SaphirPEPT"
            elif "saphircom" in name_lower: role_metier = "BD SaphirCom"
            elif "compta" in name_lower: role_metier = "BD Compta"
            
        # 2. URLs / Web
        elif value.startswith("http://") or value.startswith("https://"):
            match_url = re.search(r"https?://([^/:]+)(?::(\d+))?", value)
            if match_url:
                nom_complet = match_url.group(1).strip()
                port = int(match_url.group(2)) if match_url.group(2) else (80 if value.startswith("http://") else 443)
                
                match_user = re.search(r"Username=([^;]+)", value, re.IGNORECASE)
                if match_user:
                    identifiant = match_user.group(1).strip()
                
                match_pass = re.search(r"Password=([^;]+)", value, re.IGNORECASE)
                if match_pass:
                    mdp = match_pass.group(1).strip()
                    
                role_metier = "Serveur Web"
                name_lower = name.lower()
                if "crm" in name_lower: role_metier = "Serveur Web CRM"
                elif "lbtp" in name_lower: role_metier = "Service Web LBTP"
                elif "caisse" in name_lower: role_metier = "Service Web Caisse"
                elif "report" in name_lower: role_metier = "Service Web Report Server"
                
        # 3. Répertoire UNC / Batch / Fichiers
        elif value.startswith("\\\\"):
            match_unc = re.search(r"\\\\([^\\]+)", value)
            if match_unc:
                nom_complet = match_unc.group(1).strip()
                port = 445 # Port par défaut SMB
                
                role_metier = "Serveur Fichiers"
                name_lower = name.lower()
                if "log" in name_lower: role_metier = "Serveur Logs"
                elif "working" in name_lower or "pept" in name_lower or "batch" in name_lower:
                    role_metier = "Serveur Batch"

        if nom_complet and role_metier:
            serveurs_trouves.append({
                "nom_complet": nom_complet,
                "role_metier": role_metier,
                "identifiant": identifiant,
                "mot_de_passe": mdp,
                "port": port
            })
            
    # Insertion et déduplication
    enregistres = []
    
    for srv in serveurs_trouves:
        role = _get_or_create_role(db, srv["role_metier"])
        nom_hote = str(srv["nom_complet"]).split('\\')[0] # Extraire le nom pur sans l'instance
        
        existant = db.query(Serveur).filter(
            Serveur.environnement_id == environnement_id,
            Serveur.nom_serveur == srv["nom_complet"],
            Serveur.role_id == role.role_id
        ).first()
        
        if not existant:
            nouveau = Serveur(
                nom_serveur=srv["nom_complet"],    # Garde l'instance si SQL
                nom_hote=nom_hote,
                role_id=role.role_id,
                environnement_id=environnement_id,
                identifiant=srv["identifiant"],
                mot_de_passe=srv["mot_de_passe"],
                port=srv["port"],
                port_winrm=5985
            )
            db.add(nouveau)
            enregistres.append(f"{srv['nom_complet']} ({srv['role_metier']})")
    
    db.commit()
    
    return {
        "message": f"Découverte terminée.",
        "nombre_total_trouves": len(serveurs_trouves),
        "nouveaux_enregistres": len(enregistres),
        "serveurs": enregistres
    }

