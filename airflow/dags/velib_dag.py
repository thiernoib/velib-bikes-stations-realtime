from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import pandas as pd
from pymongo import MongoClient, errors
import os
import logging

# ================= CONFIG =================
MONGO_URI = "mongodb://mongodb:27017/"
DB_NAME = "velib"
COLLECTION_NAME = "stations"
DATA_DIR = "/opt/airflow/data"

API_KEY = os.environ.get("JCDECAUX_API_KEY")

# Logger Airflow
logger = logging.getLogger("airflow.task")

# ================= TASKS =================
def fetch_velib_data(ti):
    if not API_KEY:
        logger.warning("JCDECAUX_API_KEY is not set. Skipping fetch.")
        return

    url = f"https://api.jcdecaux.com/vls/v1/stations?contract=Paris&apiKey={API_KEY}"

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        df = pd.DataFrame(data)
        os.makedirs(DATA_DIR, exist_ok=True)
        csv_path = f"{DATA_DIR}/velib_data.csv"
        df.to_csv(csv_path, index=False)
        ti.xcom_push(key="velib_data", value=df.to_dict("records"))
        logger.info(f"Fetched {len(df)} stations from JCDecaux API.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch Velib data: {e}")
        return

def save_to_mongodb(ti):
    data = ti.xcom_pull(task_ids="fetch_velib_data", key="velib_data")
    if not data:
        logger.warning("No data fetched, skipping MongoDB insert.")
        return

    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info()  # Check connection
        db = client[DB_NAME]
        col = db[COLLECTION_NAME]
        col.delete_many({})
        col.insert_many(data)
        client.close()
        logger.info(f"Inserted {len(data)} stations into MongoDB.")
    except errors.ServerSelectionTimeoutError:
        logger.error("Could not connect to MongoDB.")
    except Exception as e:
        logger.error(f"Error inserting data into MongoDB: {e}")

# ================= DAG =================
with DAG(
    dag_id="velib_dag",
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
