from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.services.auth.ad_service import ADService
from app.core.database import get_db
from app.core.security import create_access_token, get_current_user, oauth2_scheme
from app.schemas.auth import LoginRequest, LoginResponse
from app.models.auth import BlacklistedToken

router = APIRouter(prefix="/auth", tags=["Authentification AD"])

@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest):
    """
    Authentification via AD et génération de token JWT.
    """
    user_data = ADService.authenticate_user(payload.username, payload.password)
    
    if not user_data:
        raise HTTPException(status_code=401, detail="Identifiants AD invalides")
    
    # Génération du token
    access_token = create_access_token(data={"sub": payload.username})
    
    return {
        **user_data,
        "is_authenticated": True,
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Invalide le token actuel en l'ajoutant à la liste noire.
    """
    # Ajout à la blacklist
    try:
        blacklisted = BlacklistedToken(token=token)
        db.add(blacklisted)
        db.commit()
    except Exception as e:
        # Si déjà blacklisted, on ignore
        db.rollback()
    
    return {"message": f"Déconnexion réussie pour l'utilisateur {current_user}"}
