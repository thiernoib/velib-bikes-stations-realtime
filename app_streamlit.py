import streamlit as st
import pandas as pd
from pymongo import MongoClient
import matplotlib.pyplot as plt
from datetime import datetime

# -------------------------------
# Configuration de la page
# -------------------------------
st.set_page_config(
    page_title="Vélib’ Dashboard",
    page_icon="🚲",
    layout="wide"
)

st.title("🚲 Tableau de bord Vélib’ Ile de France — Données en temps réel")

# -------------------------------
# Paramètres d'actualisation
# -------------------------------
REFRESH_INTERVAL = 300  # secondes (5 minutes)
st.sidebar.info(f"🔄 Les données se mettent à jour automatiquement toutes les {REFRESH_INTERVAL//60} minutes.")
refresh_button = st.sidebar.button("Rafraîchir maintenant")

# -------------------------------
# Connexion MongoDB
# -------------------------------
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "database_velib"
COLLECTION_NAME = "stations_velib"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# -------------------------------
# Fonction de chargement des données
# -------------------------------
@st.cache_data(ttl=REFRESH_INTERVAL)
def load_data():
    data = list(collection.find({}, {"_id": 0}))
    df = pd.DataFrame(data) if data else pd.DataFrame()
    update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return df, update_time

# Forcer le rechargement si l'utilisateur clique sur le bouton
if refresh_button:
    st.cache_data.clear()

# -------------------------------
# Chargement des données
# -------------------------------
df, update_time = load_data()

if df.empty:
    st.error("❌ Aucune donnée trouvée dans la base MongoDB.")
    st.stop()

# -------------------------------
# Indicateur de dernière mise à jour
# -------------------------------
st.markdown(
    f"<p style='text-align:right; color:gray;'>🕒 Dernière mise à jour : <b>{update_time}</b></p>",
    unsafe_allow_html=True
)

# -------------------------------
# Filtres interactifs
# -------------------------------
arrondissements = sorted(df["nom_arrondissement_communes"].dropna().unique())
selected_arr = st.sidebar.multiselect(
    "🏙️ Sélectionne un ou plusieurs arrondissements :", arrondissements, default=arrondissements
)

min_cap = int(df["capacity"].min())
max_cap = int(df["capacity"].max())
capacity_filter = st.sidebar.slider("📊 Filtrer par capacité :", min_cap, max_cap, (min_cap, max_cap))

# Application des filtres
df_filtered = df[
    (df["nom_arrondissement_communes"].isin(selected_arr)) &
    (df["capacity"].between(capacity_filter[0], capacity_filter[1]))
]

# -------------------------------
# Statistiques générales
# -------------------------------
st.subheader("📈 Statistiques globales")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Nombre de stations", df_filtered.shape[0])
col2.metric("Vélos disponibles", int(df_filtered["numbikesavailable"].sum()))
col3.metric("Places libres", int(df_filtered["numdocksavailable"].sum()))
col4.metric("Stations ouvertes", df_filtered[df_filtered["is_installed"] == "OUI"].shape[0])

# -------------------------------
# Tableau interactif
# -------------------------------
st.subheader("📋 Données filtrées")
st.dataframe(df_filtered[["stationcode", "name", "nom_arrondissement_communes", "capacity",
                          "numbikesavailable", "numdocksavailable", "ebike", "mechanical"]])

# -------------------------------
# Graphique par arrondissement
# -------------------------------
if not df_filtered.empty:
    st.subheader("📊 Répartition des vélos disponibles par arrondissement")
    df_group = df_filtered.groupby("nom_arrondissement_communes")["numbikesavailable"].sum().sort_values(ascending=False)

    fig, ax = plt.subplots()
    df_group.plot(kind="bar", ax=ax, color="royalblue")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Nombre de vélos disponibles")
    plt.tight_layout()
    st.pyplot(fig)
else:
    st.warning("Aucune station ne correspond aux filtres sélectionnés.")

# -------------------------------
# Carte des stations
# -------------------------------
if "coordonnees_geo" in df_filtered.columns and not df_filtered["coordonnees_geo"].isna().all():
    st.subheader("🗺️ Carte des stations sélectionnées")
    coords = pd.DataFrame(df_filtered["coordonnees_geo"].tolist(), columns=["lat", "lon"])
    st.map(coords)

# -------------------------------
# Footer
# -------------------------------
st.markdown("---")
st.caption("Données issues de l’API Vélib’ — Projet Data réalisé par Thierno Ibrahima Bah 🚀")
