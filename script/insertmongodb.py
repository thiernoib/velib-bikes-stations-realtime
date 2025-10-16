import requests
from pymongo import MongoClient

class TrafficDataHandler:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['database_velib']
        self.collection = self.db['stations_velib']
    
    def get_traffic_data(self):
        url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records?limit=-1"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                print("Réponse 200 : Données récupérées avec succès")
                return data
            else:
                print("Erreur lors de la requête : ", response.status_code)
                return None
        except Exception as e:
            print("Erreur lors de la récupération des données :", e)
            return None
    
    def insert_into_mongodb(self, data):
        try:
            self.collection.insert_many(data['results'])
            print("Données insérées avec succès dans MongoDB")
        except Exception as e:
            print("Erreur lors de l'insertion des données dans MongoDB :", e)

# Créer une instance de la classe TrafficDataHandler
traffic_handler = TrafficDataHandler()

# Appeler la méthode pour récupérer les données
traffic_data = traffic_handler.get_traffic_data()

# Vérifier si des données ont été récupérées avec succès
if traffic_data:
    # Insérer les données dans MongoDB
    traffic_handler.insert_into_mongodb(traffic_data)
else:
    print("Aucune donnée à afficher.")
