import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Charger le .env depuis le dossier app
load_dotenv("app/.env")

url = os.getenv("DATABASE_URL")
print(f"Testing URL: {url}")

try:
    engine = create_engine(url)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT @@VERSION"))
        print("Success! SQL Server Version:")
        print(result.fetchone()[0])
except Exception as e:
    print(f"Failed to connect: {e}")
