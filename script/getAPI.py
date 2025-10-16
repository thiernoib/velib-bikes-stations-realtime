import os
import requests
from dotenv import load_dotenv
from pymongo import MongoClient

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer les variables depuis .env
VELIB_API_URL = os.getenv("VELIB_API_URL")
MONGO_URI = os.getenv("MONGO_URI")

# Définir directement les noms de base et collection
DB_NAME = "database_velib"
COLLECTION_NAME = "stations_velib"

def get_traffic_data():
    """Récupère les données Velib depuis l'API"""
    try:
        response = requests.get(VELIB_API_URL)
        if response.status_code == 200:
            print("✅ Données récupérées avec succès depuis l'API Velib")
            return response.json()
        else:
            print(f"⚠️ Erreur API Velib : {response.status_code}")
            return None
    except Exception as e:
        print("❌ Erreur de connexion à l'API :", e)
        return None

def save_to_mongodb(data):
    """Insère les données dans MongoDB"""
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        # On vide la collection avant d’insérer les nouvelles données
        collection.delete_many({})

        # On insère les enregistrements si présents
        records = data.get("results", [])
        if records:
            collection.insert_many(records)
            print(f"✅ {len(records)} documents insérés dans {COLLECTION_NAME}")
        else:
            print("⚠️ Aucune donnée à insérer")

    except Exception as e:
        print("❌ Erreur MongoDB :", e)

# --- Exécution directe du code ---

data = get_traffic_data()

if data:
    save_to_mongodb(data)
else:
    print("⚠️ Aucune donnée récupérée, insertion annulée.")
