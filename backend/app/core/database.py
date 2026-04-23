from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# On utilise SQLite par défaut si DATABASE_URL n'est pas fourni, 
# mais ici on suppose que l'utilisateur fournira une URL SQL Server ou PostgreSQL
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL if settings.DATABASE_URL else "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    # check_same_thread est seulement requis pour SQLite
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
