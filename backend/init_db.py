"""
init_db.py — Script d'initialisation de la base de données COREAS.

Crée toutes les tables (si elles n'existent pas) et insère les données
de référence nécessaires au fonctionnement du projet :
  - Catégories : Dev, TIF, TNR, Production, Recette

Usage (depuis le dossier backend/) :
    python init_db.py
"""
import sys
import os

# S'assurer que le dossier backend/ est dans le path Python
sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import engine, Base, SessionLocal

# Import de TOUS les modèles pour que Base.metadata les connaisse
from app.models.auth import BlacklistedToken, Utilisateur
from app.models.environment import Categorie, Role, Environnement, Serveur
from app.models.verification import (
    VerificationConfigurations, Module, Controle, Verification,
    CaptureConfig, VerificationModule, ResultatControle, ResultatServeur
)

def init_db():
    print("=" * 55)
    print("  COREAS — Initialisation de la base de données")
    print("=" * 55)

    # 1. Création de toutes les tables
    print("\n[1/2] Création des tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("  ✓ Toutes les tables ont été créées avec succès.")
    except Exception as e:
        print(f"  ✗ Erreur lors de la création des tables : {e}")
        sys.exit(1)

    # 2. Insertion des données de référence
    print("\n[2/2] Insertion des données de référence...")
    db = SessionLocal()
    try:
        categories_a_inserer = ["Dev", "TIF", "TNR", "Production", "Recette"]
        inserees = 0
        ignorees = 0

        for nom in categories_a_inserer:
            existant = db.query(Categorie).filter(Categorie.nom == nom).first()
            if not existant:
                db.add(Categorie(nom=nom))
                print(f"  ✓ Catégorie ajoutée  : {nom}")
                inserees += 1
            else:
                print(f"  ~ Catégorie existante : {nom} (ignorée)")
                ignorees += 1

        db.commit()
        print(f"\n  Résumé : {inserees} catégorie(s) insérée(s), {ignorees} ignorée(s).")

    except Exception as e:
        db.rollback()
        print(f"  ✗ Erreur lors de l'insertion des données : {e}")
        sys.exit(1)
    finally:
        db.close()

    print("\n" + "=" * 55)
    print("  Initialisation terminée avec succès !")
    print("  Vous pouvez démarrer l'application.")
    print("=" * 55)

if __name__ == "__main__":
    init_db()
