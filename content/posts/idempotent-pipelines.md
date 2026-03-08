---
title: "Pipelines idempotents : lancer deux fois, obtenir le même résultat"
slug: idempotent-pipelines
date: 2026-02-16
description: "Comment construire des pipelines data idempotents. Les lancer plusieurs fois sans risque, éviter les doublons et garantir un retraitement fiable."
categories: ["data-engineering"]
tags: ["pipelines", "bonnes-pratiques", "fiabilité"]
draft: false
---

## C'est quoi l'idempotence

Un pipeline idempotent produit le même résultat qu'on le lance 1 fois ou 10 fois avec les mêmes inputs.

Lancez-le une fois : 100 enregistrements chargés. Lancez-le encore : toujours 100, pas 200.

Sans idempotence, chaque incident nécessite une intervention manuelle pour nettoyer les données en double. Ce n'est pas tenable en production.

## Pourquoi c'est critique

Les pipelines sont relancés constamment :
- retry automatique après un échec
- backfill de données historiques
- reprocessing après une correction de bug

Si le pipeline n'est pas idempotent, chaque relance risque de corrompre les données.

## Les patterns

### 1. UPSERT / MERGE

Au lieu d'ajouter des lignes, fusionner :

```sql
MERGE INTO orders_mart AS target
USING staging_orders AS source
ON target.order_id = source.order_id
WHEN MATCHED THEN UPDATE SET
    amount = source.amount,
    updated_at = source.updated_at
WHEN NOT MATCHED THEN INSERT (order_id, amount, updated_at)
    VALUES (source.order_id, source.amount, source.updated_at);
```

### 2. DELETE + INSERT par partition

Écraser la partition complète à chaque run :

```sql
DELETE FROM orders_mart WHERE order_date = '2024-01-15';
INSERT INTO orders_mart
SELECT * FROM staging_orders WHERE order_date = '2024-01-15';
```

Simple, efficace, idempotent par construction.

### 3. INSERT OVERWRITE (warehouses cloud)

```sql
INSERT OVERWRITE orders_mart
PARTITION (order_date = '2024-01-15')
SELECT * FROM staging_orders WHERE order_date = '2024-01-15';
```

### 4. Clé de déduplication en Python

```python
from datetime import date

def load_orders(df, execution_date: date):
    df = df.drop_duplicates(subset=["order_id"])
    engine.execute(f"DELETE FROM orders WHERE order_date = '{execution_date}'")
    df.to_sql("orders", engine, if_exists="append", index=False)
```

## Les pièges

**INSERT INTO sans contrôle.** C'est la cause n°1 de doublons. À bannir pour les tables de faits.

**Dépendance à l'état précédent.** Un pipeline qui fait un delta basé sur le `max(updated_at)` de la table destination n'est pas idempotent — si on le relance après un incident, le delta sera faux.

**Pas de partition date.** Sans découpage temporel, impossible d'écraser proprement une journée sans toucher au reste.

## Checklist idempotence

- [ ] Le pipeline peut être relancé sans créer de doublons
- [ ] Chaque run traite une partition clairement définie
- [ ] Pas de dépendance à l'état de la table destination
- [ ] Les tests vérifient l'unicité des clés après chargement

## En résumé

L'idempotence est la propriété la plus importante d'un pipeline data. Elle rend les relances, les backfills et le reprocessing sûrs. Le pattern le plus simple : partitionner par date et écraser la partition à chaque run.

---

**Vous avez un projet data similaire ? Parlons-en → [isdataconsulting.com](https://isdataconsulting.com)**
