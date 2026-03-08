---
title: "MinIO et Airflow : construire un data lake local"
slug: minio-airflow-data-lake
date: 2026-03-08
description: "Comment combiner MinIO et Apache Airflow pour monter un data lake S3-compatible en local. Architecture, configuration et pipelines concrets."
categories: ["data-engineering", "tools"]
tags: ["minio", "airflow", "data-lake", "s3", "architecture"]
draft: false
---

## Pourquoi un data lake local

Travailler avec S3 en production, c'est standard. Mais développer directement sur AWS coûte cher et ralentit les itérations. MinIO résout ça : un stockage objet S3-compatible qui tourne en local.

Combiné à Airflow, on obtient un environnement de développement complet :
- Stockage objet (landing, staging, curated)
- Orchestration des pipelines
- Tests reproductibles sans accès cloud

## L'architecture

```
[Sources]
    ↓
[Airflow DAGs]
    ↓
[MinIO buckets]
    ├── landing/      (données brutes)
    ├── staging/      (données nettoyées)
    └── curated/      (données prêtes à consommer)
```

Airflow orchestre les DAGs qui lisent et écrivent dans MinIO via le protocole S3. Le code est identique à celui qu'on déploiera en production sur AWS.

## Mise en place avec Docker Compose

Un fichier `docker-compose.yml` suffit pour faire tourner les deux :

```yaml
services:
  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin

  airflow:
    image: apache/airflow:2.8.1
    environment:
      AWS_ACCESS_KEY_ID: minioadmin
      AWS_SECRET_ACCESS_KEY: minioadmin
      AWS_ENDPOINT_URL: http://minio:9000
    volumes:
      - ./dags:/opt/airflow/dags
```

Airflow se connecte à MinIO comme s'il parlait à S3. Aucune modification du code des DAGs.

## Connexion Airflow → MinIO

Dans Airflow, créer une connexion S3 :

```python
from airflow.hooks.S3_hook import S3Hook

hook = S3Hook(aws_conn_id="minio_conn")
hook.load_string(
    string_data="test",
    key="landing/test.txt",
    bucket_name="data-lake"
)
```

Ou via l'UI Airflow :
- **Conn Type** : Amazon Web Services
- **Extra** : `{"endpoint_url": "http://minio:9000"}`

## Un DAG concret

Pipeline classique : ingestion → nettoyage → agrégation.

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import boto3

s3 = boto3.client(
    "s3",
    endpoint_url="http://minio:9000",
    aws_access_key_id="minioadmin",
    aws_secret_access_key="minioadmin",
)

def ingest():
    # Récupérer les données et les poser dans landing/
    s3.put_object(
        Bucket="data-lake",
        Key="landing/orders/2024-01-15.csv",
        Body=raw_data
    )

def clean():
    # Lire depuis landing/, nettoyer, écrire dans staging/
    obj = s3.get_object(Bucket="data-lake", Key="landing/orders/2024-01-15.csv")
    cleaned = transform(obj["Body"].read())
    s3.put_object(Bucket="data-lake", Key="staging/orders/2024-01-15.parquet", Body=cleaned)

with DAG("orders_pipeline", start_date=datetime(2024, 1, 1), schedule="@daily"):
    PythonOperator(task_id="ingest", python_callable=ingest) >> \
    PythonOperator(task_id="clean", python_callable=clean)
```

## Organisation des buckets

La convention de nommage des clés structure le lake :

```
data-lake/
├── landing/
│   └── orders/
│       └── 2024-01-15.csv
├── staging/
│   └── orders/
│       └── 2024-01-15.parquet
└── curated/
    └── orders_daily/
        └── 2024-01-15.parquet
```

**landing/** : données brutes, jamais modifiées.
**staging/** : données nettoyées et typées.
**curated/** : données agrégées, prêtes pour les consommateurs.

## Passer en production

L'intérêt de cette architecture : le passage en production est trivial.

1. Remplacer l'endpoint MinIO par S3
2. Mettre les credentials dans un secret manager
3. Déployer les mêmes DAGs

Le code ne change pas. Seule la configuration change.

## Les limites

- MinIO en local : pas de haute disponibilité (c'est du dev)
- Airflow LocalExecutor : suffisant pour le dev, pas pour la prod
- Les credentials en dur dans le Compose ne passent jamais en prod

## En résumé

MinIO + Airflow en local, c'est un data lake de développement complet. Même protocole que la prod, mêmes outils, mêmes patterns. Développez en local, déployez sur le cloud.

---

**Vous avez un projet data similaire ? Parlons-en → [isdataconsulting.com](https://isdataconsulting.com)**
