---
title: "Structurer un projet Python pour les pipelines data"
slug: python-project-structure-data
date: 2026-02-01
description: "Comment organiser un projet Python data proprement. Arborescence, packaging, configuration et bonnes pratiques pour des projets maintenables."
categories: ["data-engineering", "programming"]
tags: ["python", "structure-projet", "bonnes-pratiques", "packaging"]
draft: false
---

## Le problème

La plupart des projets data démarrent avec un seul script. Puis deux. Puis dix fichiers éparpillés dans un dossier sans structure.

Résultat : personne ne sait où est quoi, les imports cassent, et le déploiement est un cauchemar.

Structurer son projet dès le départ coûte 10 minutes. Ne pas le faire coûte des heures de dette technique.

## L'arborescence de référence

```
my_pipeline/
├── src/
│   └── my_pipeline/
│       ├── __init__.py
│       ├── extract.py
│       ├── transform.py
│       ├── load.py
│       └── config.py
├── tests/
│   ├── __init__.py
│   ├── test_extract.py
│   ├── test_transform.py
│   └── test_load.py
├── dags/
│   └── daily_orders.py
├── pyproject.toml
├── Makefile
├── .env.example
└── README.md
```

**Principe** : le code métier dans `src/`, les tests dans `tests/`, l'orchestration dans `dags/`.

## Le pyproject.toml

```toml
[project]
name = "my-pipeline"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "pandas>=2.0",
    "psycopg2-binary>=2.9",
    "python-dotenv>=1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "ruff>=0.1",
]
```

Installer le projet en mode éditable :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Avec `-e`, les modifications du code sont immédiatement disponibles sans réinstallation.

## La configuration

Jamais de credentials en dur. Toujours des variables d'environnement.

```python
# src/my_pipeline/config.py
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ["DB_HOST"]
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
S3_BUCKET = os.environ.get("S3_BUCKET", "data-lake")
```

Le fichier `.env.example` documente les variables attendues (sans les valeurs) :

```
DB_HOST=
DB_NAME=
DB_USER=
DB_PASSWORD=
S3_BUCKET=data-lake
```

`.env` est dans le `.gitignore`. Toujours.

## Séparer extract / transform / load

```python
# src/my_pipeline/extract.py
import pandas as pd
from my_pipeline.config import DB_HOST, DB_NAME

def extract_orders(date: str) -> pd.DataFrame:
    conn_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    query = "SELECT * FROM orders WHERE order_date = %(date)s"
    return pd.read_sql(query, conn_string, params={"date": date})
```

```python
# src/my_pipeline/transform.py
import pandas as pd

def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset=["order_id"])
    df = df[df["amount"] > 0]
    df["amount"] = df["amount"].round(2)
    return df
```

```python
# src/my_pipeline/load.py
import pandas as pd

def load_to_warehouse(df: pd.DataFrame, table: str):
    df.to_sql(table, warehouse_conn, if_exists="replace", index=False)
```

Chaque module a une responsabilité claire. Le transform ne connaît ni la source ni la destination.

## Les tests

```python
# tests/test_transform.py
import pandas as pd
from my_pipeline.transform import clean_orders

def test_removes_duplicates():
    df = pd.DataFrame({"order_id": [1, 1, 2], "amount": [10, 10, 20]})
    result = clean_orders(df)
    assert len(result) == 2

def test_removes_negative_amounts():
    df = pd.DataFrame({"order_id": [1, 2], "amount": [10, -5]})
    result = clean_orders(df)
    assert len(result) == 1
```

```bash
pytest tests/ -v
```

**Règle** : tester le transform en priorité. C'est là que vivent les bugs métier.

## Le Makefile

```makefile
.PHONY: install test lint run

install:
pip install -e ".[dev]"

test:
pytest tests/ -v

lint:
ruff check src/ tests/

run:
python -m my_pipeline.main
```

Un `make test` vaut mieux qu'un README de 3 pages.

## Les erreurs classiques

- **Tout dans un seul fichier** : impossible à tester, impossible à relire
- **Imports relatifs cassés** : résolu par le `pip install -e .`
- **Credentials dans le repo** : fuite garantie
- **Pas de tests** : refactoring impossible, régressions assurées
- **Dépendances non épinglées** : `pip install pandas` installe une version différente chaque mois

## En résumé

Un projet Python data bien structuré : `src/` pour le code, `tests/` pour les tests, `pyproject.toml` pour les dépendances, `.env` pour la config. C'est simple, mainstream, et ça tient dans le temps.

---

**Vous avez un projet data similaire ? Parlons-en → [isdataconsulting.com](https://isdataconsulting.com)**
