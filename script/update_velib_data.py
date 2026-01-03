import requests
from pymongo import MongoClient
import time
from datetime import datetime
import traceback

class TrafficDataHandler:
    def __init__(self):
        #self.client = MongoClient('mongodb://localhost:27017/')
        self.client = MongoClient('mongodb://mongodb:27017/')
        self.db = self.client['database_velib']
        self.collection = self.db['stations_velib']
        self.log_file = "script/update_log.txt"

    def log(self, message):
        """Enregistre un message avec l’heure dans un fichier log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        with open(self.log_file, "a") as f:
            f.write(log_message + "\n")

    def get_traffic_data(self):
        url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records?limit=-1"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log("✅ Données récupérées avec succès depuis l’API.")
                return data
            else:
                self.log(f"❌ Erreur HTTP {response.status_code} lors de la récupération des données.")
                return None
        except Exception as e:
            self.log(f"⚠️ Erreur réseau : {e}")
            self.log(traceback.format_exc())
            return None

    def insert_into_mongodb(self, data):
        try:
            # On remplace les anciennes données pour éviter les doublons
            self.collection.delete_many({})
            self.collection.insert_many(data['results'])
            self.log(f"📥 Insertion réussie de {len(data['results'])} documents dans MongoDB.")
        except Exception as e:
            self.log(f"⚠️ Erreur d’insertion MongoDB : {e}")
            self.log(traceback.format_exc())

    def run(self, interval=300):
        """Boucle principale pour actualiser automatiquement les données toutes les X secondes."""
        self.log("🚀 Démarrage du script de mise à jour automatique des données Vélib.")
        while True:
            self.log("🔄 Lancement d’une nouvelle mise à jour...")
            data = self.get_traffic_data()
            if data:
                self.insert_into_mongodb(data)
            else:
                self.log("Aucune donnée récupérée — nouvelle tentative dans 5 minutes.")
            self.log("⏳ Attente avant la prochaine mise à jour...\n")
            time.sleep(interval)

# ----------------------------
# Exécution principale
# ----------------------------
if __name__ == "__main__":
    handler = TrafficDataHandler()
    handler.run(interval=300)  # 300 secondes = 5 minutes
