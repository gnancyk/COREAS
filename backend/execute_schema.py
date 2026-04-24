import os
import re
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv("app/.env")

url = os.getenv("DATABASE_URL")
print(f"Connecting to: {url}")

try:
    engine = create_engine(url)
    
    with open("schema.sql", "r", encoding="utf-8") as f:
        sql = f.read()

    # Nettoyage des commentaires et séparation des commandes si nécessaire
    # SQL Server via pyodbc peut exécuter un gros bloc, mais on va gérer par requête s'il le faut.
    statements = [s.strip() for s in sql.split(';') if s.strip()]

    with engine.begin() as conn:
        for stmt in statements:
            if stmt:
                print(f"Executing: {stmt[:50]}...")
                conn.execute(text(stmt))
                
    print("Base de données initialisée avec succès !")
    
except Exception as e:
    print(f"Erreur lors de l'exécution: {e}")
