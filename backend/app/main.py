from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.auth.router import router as auth_router
from app.api.v1.crm.router import router as crm_router
from app.api.v1.sql_server.router import router as sql_router
from app.api.v1.infra.router import router as infra_router
from app.api.v1.central_param.router import router as central_param_router
from app.api.v1.batch.router import router as batch_router
from app.core.database import engine, Base
from app.models.verification import VerificationConfigurations
from app.models.auth import BlacklistedToken

# Création des tables en base de données
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SaphirV3 - Audit Platform")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routeurs modulaires
app.include_router(auth_router)
app.include_router(crm_router)
app.include_router(sql_router)
app.include_router(infra_router)
app.include_router(central_param_router)
app.include_router(batch_router)

@app.get("/")
async def root():
    return {"message": "SaphirV3 Backend is running with Modular MVC architecture"}