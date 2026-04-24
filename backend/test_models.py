import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from app.models import (
    Utilisateur, Categorie, Role, Environnement, Serveur,
    Module, Controle, Verification, CaptureConfig,
    VerificationModule, ResultatControle, ResultatServeur
)

load_dotenv("app/.env")
url = os.getenv("DATABASE_URL")
engine = create_engine(url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_models():
    db = SessionLocal()
    try:
        # Simple test to verify models map to the schema without throwing errors on initialization
        print("Checking tables mapping...")
        print("Utilisateur table:", Utilisateur.__table__.name)
        print("ResultatControle table:", ResultatControle.__table__.name)
        
        # Test Query (should be empty but won't crash if mapped correctly)
        users = db.query(Utilisateur).limit(1).all()
        print("Users found:", len(users))
        print("Models successfully verified!")
    except Exception as e:
        print(f"Error validating models: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_models()
