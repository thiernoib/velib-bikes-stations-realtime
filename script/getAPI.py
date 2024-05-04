import requests

def get_traffic_data():
    url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records?limit=20"
    
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

# Appeler la fonction pour récupérer les données
traffic_data = get_traffic_data()

# Vérifier si des données ont été récupérées avec succès
if traffic_data:
    # Afficher les données récupérées
    print(traffic_data)
else:
    print("Aucune donnée à afficher.")
