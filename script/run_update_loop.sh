#!/bin/bash

echo "⏳ Attente de MongoDB..."

until python - << END
from pymongo import MongoClient
import os
try:
    MongoClient(
        host=os.getenv("MONGO_HOST"),
        port=int(os.getenv("MONGO_PORT")),
        serverSelectionTimeoutMS=2000
    ).server_info()
    print("✅ MongoDB prêt")
except:
    raise SystemExit(1)
END
do
  sleep 2
done

echo "🔄 Lancement du worker MongoDB"
python script/update_velib_data.py &

echo "🚀 Lancement Streamlit"
streamlit run script/app_streamlit.py \
  --server.address=0.0.0.0 \
  --server.port=8501
