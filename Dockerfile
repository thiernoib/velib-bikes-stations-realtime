# =========================
# Image de base Python
# =========================
FROM python:3.12-slim

# =========================
# Installer dépendances système et timezone
# =========================
RUN apt-get update && apt-get install -y \
        bash \
        curl \
        gcc \
        libpq-dev \
        build-essential \
        tzdata \
    && ln -fs /usr/share/zoneinfo/Europe/Paris /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# =========================
# Répertoire de travail
# =========================
WORKDIR /app

# =========================
# Copier requirements si existant
# =========================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# =========================
# Installer Airflow + dépendances
# =========================
RUN pip install --no-cache-dir \
        apache-airflow==2.9.0 \
        pymongo \
        pandas \
        requests \
        matplotlib \
        psycopg2-binary \
        streamlit

# =========================
# Copier projet
# =========================
COPY . .

# =========================
# Exposer ports
# =========================
EXPOSE 8080 8501

# =========================
# Commande par défaut
# =========================
# Override via docker-compose pour webserver, scheduler ou streamlit
CMD ["bash"]
