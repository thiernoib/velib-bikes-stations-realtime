FROM python:3.10-slim

ENV AIRFLOW_HOME=/opt/airflow
ENV TZ=Europe/Paris

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

WORKDIR $AIRFLOW_HOME

# Installer Airflow et dépendances compatibles
RUN pip install --no-cache-dir \
    apache-airflow==2.9.0 \
    psycopg2-binary \
    pymongo \
    pandas \
    requests \
    matplotlib \
    streamlit

# Créer les dossiers Airflow
RUN mkdir -p dags logs plugins data script

COPY airflow/dags dags
COPY airflow/logs logs
COPY script script
COPY data data

EXPOSE 8080 8501

CMD ["bash"]
