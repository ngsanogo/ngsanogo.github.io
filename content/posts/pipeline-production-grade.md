---
title: "Construire un pipeline production-grade : idempotence, erreurs et traitement incrémental"
slug: pipeline-production-grade
date: 2026-02-22
description: "Trois propriétés que tout pipeline data doit avoir avant de toucher la prod : idempotence, gestion des erreurs et traitement incrémental. En pratique, avec du code."
categories: ["data-engineering"]
tags: ["pipelines", "fiabilité", "idempotence", "gestion-erreurs", "incremental-processing", "bonnes-pratiques"]
keywords: []
image: "/images/og-default.svg"
draft: false
aliases:
  - /posts/idempotent-pipelines/
  - /posts/error-handling-pipelines/
  - /posts/incremental-data-processing/
---

## Pourquoi cet article

J'ai eu deux incidents marquants en production. Le premier : un pipeline relancé après un bug avait doublé toutes les données de la table — personne ne s'en était rendu compte pendant 3 jours. Le deuxième : un pipeline critique avait planté un vendredi soir sans alerte, et l'équipe métier a signalé des données manquantes le lundi matin.

Ces deux incidents ont la même cause profonde : des pipelines qui n'étaient pas pensés pour la production. Pas idempotents. Sans gestion d'erreurs. Pas incrémentaux. Ce sont les trois propriétés que j'exige maintenant systématiquement avant de mettre un pipeline en prod.

## Quick Start (Docker)

Pour tester les exemples SQL :

```bash
docker run --name pg-prod -e POSTGRES_PASSWORD=secret -d postgres:16
docker exec -it pg-prod psql -U postgres
```

Pour les exemples Python :

```bash
docker run --rm -it python:3.12-slim bash -c "pip install -q tenacity requests && python"
```

Pour nettoyer : `docker rm -f pg-prod`.

---

## 1. Idempotence : lancer deux fois, obtenir le même résultat

Un pipeline idempotent produit le même résultat qu'on le lance 1 fois ou 10 fois avec les mêmes inputs.

Lancez-le une fois : 100 enregistrements chargés. Lancez-le encore : toujours 100, pas 200.

Sans idempotence, chaque incident nécessite une intervention manuelle pour nettoyer les doublons. Sur un pipeline qui tourne 5 fois par jour, c'est une catastrophe opérationnelle.

Les pipelines sont relancés constamment : retry automatique après un échec, backfill de données historiques, reprocessing après correction d'un bug. Si le pipeline n't pas idempotent, chaque relance risque de corrompre les données.

### Les patterns

**UPSERT / MERGE** — fusionner au lieu d'ajouter :

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

**DELETE + INSERT par partition** — la solution la plus simple et la plus robuste :

```sql
DELETE FROM orders_mart WHERE order_date = '2024-01-15';
INSERT INTO orders_mart
SELECT * FROM staging_orders WHERE order_date = '2024-01-15';
```

Simple, efficace, idempotent par construction. C'est le pattern que j'utilise par défaut.

**INSERT OVERWRITE** (cloud warehouses) :

```sql
INSERT OVERWRITE orders_mart
PARTITION (order_date = '2024-01-15')
SELECT * FROM staging_orders WHERE order_date = '2024-01-15';
```

**Déduplication en Python avant chargement** :

```python
from datetime import date
from sqlalchemy import text

def load_orders(df, execution_date: date, engine):
    df = df.drop_duplicates(subset=["order_id"])
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM orders WHERE order_date = :dt"), {"dt": str(execution_date)})
        df.to_sql("orders", conn, if_exists="append", index=False)
```

### Les pièges à éviter

`INSERT INTO` sans contrôle est la cause n°1 de doublons. À bannir pour les tables de faits.

Une dépendance à l'état précédent casse l'idempotence. Un pipeline qui fait un delta basé sur `max(updated_at)` de la table destination n'est pas idempotent — si on le relance après un incident, le delta sera faux.

Sans partition date, impossible d'écraser proprement une journée sans toucher au reste.

---

## 2. Gestion des erreurs : un pipeline silencieux est un pipeline dangereux

Les défaillances sont inévitables : API inaccessibles, schémas qui changent, volumes inattendus, timeouts réseau. Un pipeline robuste ne tente pas d'éviter les erreurs — il sait quoi faire quand elles surviennent.

### Niveau 1 — Retry automatique

La majorité des erreurs sont transitoires. Un retry avec backoff exponentiel suffit :

```python
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=60))
def fetch_api_data(endpoint):
    response = requests.get(endpoint, timeout=30)
    response.raise_for_status()
    return response.json()
```

Règles : backoff exponentiel (pas de retry immédiat), nombre de tentatives limité, timeout sur chaque appel.

### Niveau 2 — Isolation des erreurs

Une erreur sur un enregistrement ne doit pas bloquer les milliers d'autres :

```python
success, errors = [], []
for record in records:
    try:
        result = transform(record)
        success.append(result)
    except ValidationError as e:
        errors.append({"record": record, "error": str(e)})

load(success)
quarantine(errors)
```

Les enregistrements en erreur sont mis en quarantaine pour analyse, pas perdus.

### Niveau 3 — Dégradation gracieuse

Quand une source non critique est indisponible, continuer avec les données disponibles plutôt que tout arrêter. Exemple : un pipeline qui enrichit des commandes avec des données météo. Si l'API météo est down, les commandes sont quand même chargées — la colonne météo sera `NULL` et complétée au prochain run.

### Circuit breaker

Quand une source externe échoue systématiquement, ne pas continuer à la marteler. Après N échecs consécutifs, couper l'appel et alerter. Tester périodiquement si la source est revenue.

### Alertes : le minimum vital

À alerter systématiquement :

- échec après tous les retries
- volume anormalement bas (possible perte de données)
- durée anormalement longue (possible blocage)
- taux d'erreur au-dessus du seuil

L'alerte doit contenir : quel pipeline, quelle étape, quel message d'erreur, un lien vers les logs.

---

## 3. Traitement incrémental : ne retraiter que ce qui a changé

Le full reload (tout retraiter à chaque run) fonctionne au début. Mais quand les tables grossissent, les runs durent des heures, les coûts cloud explosent et les fenêtres de maintenance rétrécissent.

### Les 3 patterns

**Timestamp-based** — la source a une colonne `updated_at`. On filtre sur les enregistrements modifiés depuis le dernier run :

```sql
SELECT *
FROM source_orders
WHERE updated_at > '2024-01-14 23:59:59'
```

Simple et universel. Piège : les suppressions ne sont pas détectées. Et si `updated_at` n'est pas indexé, le filtre est lent.

**CDC (Change Data Capture)** — la source envoie un flux de changements : inserts, updates, deletes. Outils : Debezium, AWS DMS, pg_logical. Avantage : détecte aussi les suppressions, temps réel possible. Piège : plus complexe à mettre en place et à monitorer.

**Snapshot + diff** — snapshot complet régulier comparé au précédent pour identifier les changements :

```sql
SELECT s.*
FROM source_snapshot s
LEFT JOIN previous_snapshot p ON s.order_id = p.order_id
WHERE p.order_id IS NULL
   OR s.hash_row != p.hash_row
```

Fonctionne même sans colonne `updated_at`. Coûteux en stockage et en compute sur les grosses tables.

### Comment choisir

| Critère                   | Timestamp | CDC                 | Snapshot + diff |
| ------------------------- | --------- | ------------------- | --------------- |
| Détecte inserts + updates | Oui       | Oui                 | Oui             |
| Détecte les deletes       | Non       | Oui                 | Oui             |
| Complexité                | Faible    | Élevée              | Moyenne         |
| Latence                   | Batch     | Temps réel possible | Batch           |

**Règle** : commencer par timestamp-based. Passer à CDC quand les deletes comptent ou que la latence est critique. Snapshot + diff en dernier recours.

### Incrémental + idempotence — les deux vont ensemble

Un pipeline incrémental doit rester idempotent. Le pattern recommandé :

1. Identifier la partition à traiter (`order_date = '2024-01-15'`)
2. Écraser la partition complète (DELETE + INSERT)
3. Incrémenter le watermark

Jamais d'`INSERT INTO` brut sur un pipeline incrémental — c'est la recette des doublons.

---

## La checklist avant la prod

- [ ] Le pipeline peut être relancé sans créer de doublons
- [ ] Chaque run traite une partition clairement définie
- [ ] Pas de dépendance à l'état de la table destination
- [ ] Les erreurs sont catchées, isolées ou alertées — jamais silencieuses
- [ ] Il y a une alerte en cas d'échec ou de volume anormal
- [ ] Le traitement est incrémental si les volumes dépassent 10 Go

## En résumé

| Propriété              | Problème qu'elle résout                   |
| ---------------------- | ----------------------------------------- |
| Idempotence            | Relances sûres, pas de doublons           |
| Gestion des erreurs    | Pas de données corrompues silencieusement |
| Traitement incrémental | Coûts et durées maîtrisés à l'échelle     |

Un pipeline production-grade n'est pas plus compliqué qu'un pipeline basique. Il est juste pensé pour les cas qui arrivent inévitablement : relances, pannes, volumes croissants.
