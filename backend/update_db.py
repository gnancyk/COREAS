import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv("app/.env")
url = os.getenv("DATABASE_URL")
engine = create_engine(url)

try:
    with engine.begin() as conn:
        # Essayer d'ajouter les colonnes. Si elles existent déjà, intercepter l'erreur
        try:
            conn.execute(text("ALTER TABLE Serveur ADD port INT;"))
            print("Colonne port ajoutée.")
        except Exception as e:
            print("Le port existe peut-être déjà.")
            
        try:
            conn.execute(text("ALTER TABLE Serveur ADD identifiant NVARCHAR(255);"))
            print("Colonne identifiant ajoutée.")
        except Exception as e:
            print("L'identifiant existe peut-être déjà.")
            
        try:
            conn.execute(text("ALTER TABLE Serveur ADD mot_de_passe NVARCHAR(MAX);"))
            print("Colonne mot_de_passe ajoutée.")
        except Exception as e:
            print("Le mot_de_passe existe peut-être déjà.")
            
    print("Mise à jour SQL terminée.")
except Exception as e:
    print(f"Erreur globale : {e}")
