import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Charger les variables d'environnement
load_dotenv()

# Récupérer l'URI de connexion
MONGO_URI = os.getenv("MONGO_URI")

try:
    # Connexion à MongoDB
    client = MongoClient(MONGO_URI)
    print("✅ Connexion établie avec succès à MongoDB Atlas")

    # Vérifier l'accès à la liste des bases de données
    print("Bases de données disponibles :", client.list_database_names())

except Exception as e:
    print("❌ Erreur de connexion à MongoDB :", e)
