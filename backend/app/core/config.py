from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    # Sécurité
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Active Directory
    AD_SERVER_URL: str
    AD_DOMAIN: str
    AD_BASE_DN: str

    # Base de données
    DATABASE_URL: str

    # Central Param (SOAP)
    CENTRAL_PARAM_WSDL: str = ""


    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    )

settings = Settings()
