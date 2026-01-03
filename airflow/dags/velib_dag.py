from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import pandas as pd
from pymongo import MongoClient
import os

# ================= CONFIG =================
MONGO_URI = "mongodb://mongodb:27017/"
DB_NAME = "velib"
COLLECTION_NAME = "stations"
DATA_DIR = "/opt/airflow/data"
API_KEY = os.environ.get("JCDECAUX_API_KEY")

# ================= TASKS =================
def fetch_velib_data(ti):
    url = f"https://api.jcdecaux.com/vls/v1/stations?contract=Paris&apiKey={API_KEY}"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data)

    os.makedirs(DATA_DIR, exist_ok=True)
    csv_path = f"{DATA_DIR}/velib_data.csv"
    df.to_csv(csv_path, index=False)

    ti.xcom_push(key="velib_data", value=df.to_dict("records"))

def save_to_mongodb(ti):
    data = ti.xcom_pull(task_ids="fetch_velib_data", key="velib_data")
    if not data:
        return

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    col = db[COLLECTION_NAME]
    col.delete_many({})
    col.insert_many(data)
    client.close()

# ================= DAG =================
with DAG(
    dag_id="velib_complete_dag",
    start_date=datetime(2024, 1, 1),
    schedule="*/5 * * * *",
    catchup=False,
    tags=["velib", "mongodb"],
) as dag:

    fetch = PythonOperator(
        task_id="fetch_velib_data",
        python_callable=fetch_velib_data,
    )

    save = PythonOperator(
        task_id="save_to_mongodb",
        python_callable=save_to_mongodb,
    )

    fetch >> save
