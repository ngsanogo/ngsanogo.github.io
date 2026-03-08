---
title: "Python pour le data engineering"
slug: python-for-data-engineering
date: 2026-01-18
description: "Les bases de Python pour le data engineering. Les librairies essentielles, les patterns courants et les bonnes pratiques pour écrire des pipelines solides."
categories: ["data-engineering", "programming"]
tags: ["python", "pipelines", "programmation", "bonnes-pratiques"]
keywords: []
series: ""
image: "/images/og-default.svg"
draft: false
---

## Pourquoi Python

Python est le langage dominant en data engineering. Pas parce qu'il est le plus rapide — mais parce que l'écosystème est imbattable :
- Pandas, Polars, DuckDB pour la manipulation de données
- SQLAlchemy, psycopg2 pour les bases de données
- Airflow, Prefect, Dagster pour l'orchestration
- boto3 pour AWS, google-cloud pour GCP

Et surtout : tout le monde le lit. Le code Python d'un pipeline est compréhensible par un analyste, un data scientist ou un DevOps.

## Les fondamentaux à maîtriser

### Lire et écrire des fichiers

```python
import csv
import json

# CSV
with open("orders.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["order_id"], row["amount"])

# JSON
with open("config.json") as f:
    config = json.load(f)
```

### Manipuler des données avec Pandas

```python
import pandas as pd

df = pd.read_csv("orders.csv")
df["amount"] = df["amount"].astype(float)
df = df[df["amount"] > 0]
df = df.drop_duplicates(subset=["order_id"])

df.to_parquet("orders_clean.parquet", index=False)
```

**Attention** : Pandas charge tout en mémoire. Pour les gros fichiers (> 1 Go), préférer Polars ou DuckDB.

### Polars : l'alternative rapide

```python
import polars as pl

df = pl.read_csv("orders.csv")
df = df.filter(pl.col("amount") > 0).unique(subset=["order_id"])
df.write_parquet("orders_clean.parquet")
```

Polars est plus rapide que Pandas sur les gros volumes, avec une API plus stricte.

## Se connecter aux bases de données

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="analytics",
    user="etl_user",
    password="secret"  # En prod : variable d'environnement
)

with conn.cursor() as cur:
    cur.execute("SELECT * FROM orders WHERE order_date = %s", ("2024-01-15",))
    rows = cur.fetchall()

conn.close()
```

**Règle absolue** : requêtes paramétrées (`%s`), jamais de f-string avec du SQL. C'est la porte ouverte aux injections.

## Interagir avec le cloud

```python
import boto3

s3 = boto3.client("s3")

# Upload
s3.upload_file("orders.parquet", "data-lake", "landing/orders/2024-01-15.parquet")

# Download
s3.download_file("data-lake", "staging/orders/latest.parquet", "local_orders.parquet")
```

Le même pattern fonctionne avec GCS (google-cloud-storage) et Azure Blob (azure-storage-blob).

## Les patterns courants

### Extract-Transform-Load

```python
def extract():
    return pd.read_sql("SELECT * FROM source_orders", source_conn)

def transform(df):
    df = df.drop_duplicates(subset=["order_id"])
    df["amount_eur"] = df["amount_usd"] * 0.92
    return df

def load(df):
    df.to_sql("orders", target_conn, if_exists="replace", index=False)

# Pipeline
raw = extract()
clean = transform(raw)
load(clean)
```

### Gestion des erreurs

```python
import logging

logger = logging.getLogger(__name__)

def safe_extract(source):
    try:
        df = pd.read_sql(f"SELECT * FROM {source}", conn)
        logger.info(f"Extracted {len(df)} rows from {source}")
        return df
    except Exception as e:
        logger.error(f"Failed to extract from {source}: {e}")
        raise
```

Toujours logger avant de lever l'exception. En production, c'est le log qui permet de diagnostiquer.

## Les librairies essentielles

| Librairie | Usage |
|---|---|
| pandas / polars | Manipulation de données |
| psycopg2 / sqlalchemy | Connexion PostgreSQL |
| boto3 | AWS (S3, Glue, etc.) |
| requests | Appels API HTTP |
| python-dotenv | Variables d'environnement |
| pydantic | Validation de schémas |
| pytest | Tests unitaires |

## Bonnes pratiques

1. **Environnements virtuels** : toujours `python -m venv .venv` avant d'installer quoi que ce soit
2. **Requirements épinglés** : `pip freeze > requirements.txt` avec des versions fixes
3. **Pas de credentials dans le code** : `os.environ["DB_PASSWORD"]`, jamais en dur
4. **Type hints** : `def extract(table: str) -> pd.DataFrame:` — ça documente le code gratuitement
5. **Fonctions courtes** : une fonction = une responsabilité

## En résumé

Python pour le data engineering, c'est avant tout Pandas/Polars pour les données, psycopg2/SQLAlchemy pour les bases, et boto3 pour le cloud. Maîtrisez ces briques, écrivez du code propre et testable, et vos pipelines tiendront en production.

---

**Vous avez un projet data similaire ? Parlons-en → [isdataconsulting.com](https://isdataconsulting.com)**
