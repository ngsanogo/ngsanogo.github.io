---
title: "PostgreSQL : la base de données à maîtriser"
slug: postgresql-basics
date: 2026-01-25
description: "Les fondamentaux de PostgreSQL pour le data engineering. Installation, commandes essentielles, types de données et bonnes pratiques pour bien démarrer."
categories: ["data-engineering", "sql"]
tags: ["postgresql", "sql", "base-de-données", "fondamentaux"]
draft: false
---

## Pourquoi PostgreSQL

PostgreSQL est la base relationnelle open source la plus complète. Fiable, performante, extensible. C'est le choix par défaut pour :
- les bases applicatives
- les entrepôts de données de taille moyenne
- le développement local avant de passer sur un cloud warehouse

La plupart des outils data (Airflow, dbt, Metabase) s'y connectent nativement.

## Installation rapide

```bash
# Ubuntu / Debian
sudo apt install postgresql postgresql-client

# Démarrer le service
sudo systemctl start postgresql

# Se connecter
sudo -u postgres psql
```

Sous macOS : `brew install postgresql@16 && brew services start postgresql@16`.

## Les commandes psql essentielles

```sql
-- Lister les bases
\l

-- Se connecter à une base
\c ma_base

-- Lister les tables
\dt

-- Décrire une table
\d ma_table

-- Quitter
\q
```

psql est l'interface en ligne de commande. Brut mais efficace.

## Créer une base et des tables

```sql
CREATE DATABASE analytics;

\c analytics

CREATE TABLE orders (
    order_id    SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    amount      NUMERIC(10, 2) NOT NULL,
    order_date  DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(255) UNIQUE,
    created_at  TIMESTAMP DEFAULT NOW()
);
```

**SERIAL** : auto-incrément. **NUMERIC(10,2)** : précision décimale pour les montants. **DEFAULT** : valeurs par défaut.

## Les types de données importants

| Type | Usage |
|---|---|
| INTEGER / BIGINT | Identifiants, compteurs |
| NUMERIC(p, s) | Montants, calculs précis |
| VARCHAR(n) | Texte court |
| TEXT | Texte long sans limite |
| DATE | Dates sans heure |
| TIMESTAMP | Dates avec heure |
| BOOLEAN | Vrai/faux |
| JSONB | JSON indexable |

**Règle** : utiliser NUMERIC pour l'argent, jamais FLOAT. Utiliser TIMESTAMP WITH TIME ZONE en production.

## Les requêtes de base

```sql
-- Insérer
INSERT INTO orders (customer_id, amount, order_date)
VALUES (1, 150.00, '2024-01-15');

-- Lire avec filtre
SELECT o.order_id, c.name, o.amount
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_date >= '2024-01-01'
ORDER BY o.amount DESC;

-- Mettre à jour
UPDATE orders SET amount = 175.00 WHERE order_id = 1;

-- Supprimer
DELETE FROM orders WHERE order_date < '2023-01-01';
```

## Index : la performance

Sans index, PostgreSQL scanne toute la table. Avec un index sur les colonnes filtrées, la requête est instantanée.

```sql
CREATE INDEX idx_orders_date ON orders (order_date);
CREATE INDEX idx_orders_customer ON orders (customer_id);
```

**Règle** : indexer les colonnes utilisées dans WHERE, JOIN et ORDER BY. Ne pas tout indexer — chaque index ralentit les écritures.

## Fonctionnalités avancées utiles

### JSONB

```sql
CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    payload  JSONB NOT NULL
);

SELECT payload->>'event_type' AS event_type
FROM events
WHERE payload @> '{"source": "web"}';
```

### Window functions

```sql
SELECT
    customer_id,
    order_date,
    amount,
    SUM(amount) OVER (PARTITION BY customer_id ORDER BY order_date) AS cumul
FROM orders;
```

### CTEs

```sql
WITH daily_totals AS (
    SELECT order_date, SUM(amount) AS total
    FROM orders
    GROUP BY order_date
)
SELECT order_date, total
FROM daily_totals
WHERE total > 1000;
```

## Bonnes pratiques

1. **Toujours définir une clé primaire** — pas de table sans PK
2. **Utiliser des contraintes** : NOT NULL, UNIQUE, FOREIGN KEY
3. **Nommer les index explicitement** : `idx_table_colonne`
4. **VACUUM et ANALYZE réguliers** : PostgreSQL en a besoin pour rester performant
5. **pg_dump pour les sauvegardes** : `pg_dump -Fc ma_base > backup.dump`

## En résumé

PostgreSQL est la base de données fiable et polyvalente que tout data engineer doit maîtriser. Commencez par les fondamentaux, indexez intelligemment, et vous aurez un socle solide pour vos pipelines.

---

**Vous avez un projet data similaire ? Parlons-en → [isdataconsulting.com](https://isdataconsulting.com)**
