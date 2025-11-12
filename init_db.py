"""
Script d'initialisation de la base de données pour COLPRAD 2025
À exécuter après le premier déploiement sur Render
"""

from app import app, db

def init_database():
    """Initialise la base de données avec les tables nécessaires"""
    with app.app_context():
        # Créer toutes les tables
        db.create_all()
        print("✅ Base de données initialisée avec succès!")
        print("✅ Toutes les tables ont été créées.")
        
        # Afficher les tables créées
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\n📊 Tables créées ({len(tables)}):")
        for table in tables:
            print(f"  - {table}")

if __name__ == "__main__":
    init_database()
