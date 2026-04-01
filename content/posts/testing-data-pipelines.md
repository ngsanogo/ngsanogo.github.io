---
title: "Tester ses pipelines data : ce qui compte vraiment"
slug: testing-data-pipelines
date: 2026-03-01
description: "Comment tester des pipelines data efficacement. Tests unitaires, d'intégration et de données — les approches pragmatiques qui protègent la production."
categories: ["data-engineering", "testing"]
tags: ["tests", "qualité", "pipelines", "pytest", "bonnes-pratiques"]
keywords: []
image: "/images/og-default.svg"
draft: false
---

## Pourquoi tester ses pipelines

Un pipeline sans tests, c'est un pipeline qui casse en silence. Les données arrivent mal formatées, un schéma change, une colonne disparaît — et personne ne s'en aperçoit avant qu'un dashboard affiche n'importe quoi.

Les tests ne sont pas un luxe. C'est ce qui permet de refactorer, de déployer et de dormir tranquille.

## Quick Start (Docker)

Pour exécuter les tests Python de cet article :

```bash
docker run --rm -it python:3.12-slim bash -c "
  pip install -q pandas pytest &&
  python
"
```

Collez les fonctions de test et lancez-les avec `pytest`. Pour les tests SQL, lancez un PostgreSQL : `docker run --name pg-test -e POSTGRES_PASSWORD=secret -d postgres:16`.

## Les 3 niveaux de tests

### 1. Tests unitaires : la logique de transformation

Tester les fonctions de transformation isolément, sans base de données ni fichier.

```python
# test_transform.py
import pandas as pd
from pipeline.transform import clean_orders

def test_removes_duplicates():
    df = pd.DataFrame({
        "order_id": [1, 1, 2],
        "amount": [100, 100, 200]
    })
    result = clean_orders(df)
    assert len(result) == 2

def test_removes_negative_amounts():
    df = pd.DataFrame({
        "order_id": [1, 2],
        "amount": [100, -50]
    })
    result = clean_orders(df)
    assert result["amount"].min() >= 0

def test_rounds_amounts():
    df = pd.DataFrame({
        "order_id": [1],
        "amount": [10.456]
    })
    result = clean_orders(df)
    assert result["amount"].iloc[0] == 10.46
```

**Rapide**, **fiable**, **pas de dépendance externe**. C'est le test le plus rentable.

### 2. Tests d'intégration : les connexions

Vérifier que le pipeline se connecte, lit et écrit correctement.

```python
# test_integration.py
import pytest
from pipeline.extract import extract_orders
from pipeline.load import load_to_warehouse

@pytest.fixture
def test_db():
    """Base de test éphémère."""
    conn = create_test_database()
    seed_test_data(conn)
    yield conn
    drop_test_database(conn)

def test_extract_returns_dataframe(test_db):
    df = extract_orders("2024-01-15", conn=test_db)
    assert len(df) > 0
    assert "order_id" in df.columns

def test_load_writes_to_target(test_db):
    df = pd.DataFrame({"order_id": [1], "amount": [100]})
    load_to_warehouse(df, "orders", conn=test_db)
    result = pd.read_sql("SELECT * FROM orders", test_db)
    assert len(result) == 1
```

Plus lent, mais attrape les vrais problèmes : permissions, schémas, types.

### 3. Tests de données : la qualité en production

Vérifier les données elles-mêmes après chaque run.

```sql
-- Pas de doublons
SELECT order_id, COUNT(*)
FROM warehouse.orders
GROUP BY order_id
HAVING COUNT(*) > 1;

-- Pas de nulls sur les colonnes critiques
SELECT COUNT(*)
FROM warehouse.orders
WHERE customer_id IS NULL;

-- Volume cohérent
SELECT COUNT(*) AS row_count
FROM warehouse.orders
WHERE order_date = CURRENT_DATE - INTERVAL '1 day'
HAVING COUNT(*) < 50;
```

Outils : dbt tests, Great Expectations, Soda.

## Quoi tester en priorité

La réponse pragmatique :

1. **Les transformations métier** — c'est là que les bugs ont le plus d'impact
2. **Les contrats de schéma** — colonnes présentes, types corrects
3. **Les invariants de données** — unicité, non-nullité, bornes

Ne pas tester :
- Les librairies tierces (Pandas sait lire un CSV)
- Les requêtes SQL triviales
- L'infrastructure (c'est le job du monitoring)

## Fixtures et données de test

```python
@pytest.fixture
def sample_orders():
    return pd.DataFrame({
        "order_id": [1, 2, 3],
        "customer_id": [10, 20, 30],
        "amount": [100.0, 200.0, 300.0],
        "order_date": ["2024-01-15"] * 3
    })

def test_total_amount(sample_orders):
    total = sample_orders["amount"].sum()
    assert total == 600.0
```

**Règle** : des fixtures simples, avec des valeurs évidentes. Le test doit être lisible sans contexte.

## Intégrer les tests dans le CI

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
      - run: pytest tests/ -v --tb=short
```

Chaque push déclenche les tests. Pas de merge sans tests verts.

## Les erreurs classiques

- **Tester trop tard** : quand le pipeline est en prod depuis 6 mois, c'est trop tard pour écrire des tests
- **Tester trop** : 100% de couverture sur du code glue n'apporte rien
- **Données de test fragiles** : un test qui dépend d'une base de dev partagée casse tout le temps
- **Ignorer les tests qui échouent** : un test rouge qu'on ignore est pire que pas de test

## En résumé

Testez les transformations en unitaire, les connexions en intégration, les données en production. Commencez par les tests unitaires — c'est rapide, fiable, et ça couvre 80% des bugs.
