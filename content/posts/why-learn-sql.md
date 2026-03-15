---
title: "Pourquoi SQL est la compétence n°1 du data engineer"
slug: why-learn-sql
date: 2026-01-11
description: "SQL est le langage le plus important pour un data engineer. Pourquoi il reste incontournable et comment le maîtriser efficacement."
categories: ["data-engineering", "sql"]
tags: ["sql", "compétences", "carrière", "fondamentaux"]
keywords: []
series: ""
image: "/images/og-default.svg"
draft: false
---

## SQL ne meurt jamais

Chaque année, un nouvel outil promet de remplacer SQL. Et chaque année, SQL est toujours là. Depuis 1974.

Pourquoi ? Parce que SQL fait exactement ce qu'on lui demande : interroger des données. Et il le fait mieux que tout le reste.

## Quick Start (Docker)

Pour tester les exemples SQL de cet article :

```bash
docker run --name pg-sql -e POSTGRES_PASSWORD=secret -d postgres:16
docker exec -it pg-sql psql -U postgres
```

Pour nettoyer : `docker rm -f pg-sql`.

## Le langage universel de la data

SQL est partout :
- **Bases relationnelles** : PostgreSQL, MySQL, SQL Server
- **Cloud warehouses** : BigQuery, Snowflake, Redshift
- **Moteurs de requêtes** : Spark SQL, Trino, DuckDB
- **Outils de transformation** : dbt (100% SQL)
- **Streaming** : Kafka KSQL, Flink SQL

Quel que soit l'outil, SQL est l'interface. Un data engineer qui maîtrise SQL peut travailler sur n'importe quelle stack.

## Ce que SQL permet

### Explorer les données

```sql
SELECT
    order_date,
    COUNT(*) AS nb_orders,
    SUM(amount) AS total,
    AVG(amount) AS avg_order
FROM orders
WHERE order_date >= '2024-01-01'
GROUP BY order_date
ORDER BY order_date;
```

En 6 lignes, on a une vue complète de l'activité. Faites la même chose en Python — ça prend 15 lignes et une dépendance.

### Transformer les données

```sql
WITH daily_orders AS (
    SELECT
        customer_id,
        order_date,
        SUM(amount) AS daily_total
    FROM orders
    GROUP BY customer_id, order_date
)
SELECT
    customer_id,
    order_date,
    daily_total,
    SUM(daily_total) OVER (
        PARTITION BY customer_id
        ORDER BY order_date
    ) AS cumulative_total
FROM daily_orders;
```

CTEs + window functions = transformations complexes lisibles.

### Contrôler la qualité

```sql
-- Doublons
SELECT order_id, COUNT(*)
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1;

-- Nulls inattendus
SELECT COUNT(*) FROM orders WHERE customer_id IS NULL;

-- Valeurs hors bornes
SELECT * FROM orders WHERE amount < 0 OR amount > 100000;
```

SQL est aussi un outil d'audit. Pas besoin d'un framework de data quality pour les contrôles de base.

## SQL vs Python : pas un choix

La question n'est pas « SQL ou Python ». Les deux sont complémentaires :

| Tâche | Meilleur outil |
|---|---|
| Requêter une base | SQL |
| Transformer en batch | SQL (dbt) |
| Appeler une API | Python |
| Manipuler des fichiers | Python |
| Fenêtrage et agrégation | SQL |
| Logique complexe (boucles, conditions) | Python |
| Tests de données | SQL |
| Orchestration | Python (Airflow) |

**Règle** : si ça peut se faire en SQL, faites-le en SQL. Le moteur de la base optimise mieux que votre code Python.

## Les concepts à maîtriser

Par ordre de priorité :

1. **SELECT, WHERE, GROUP BY, ORDER BY** — la base
2. **JOINs** — INNER, LEFT, comprendre les NULL
3. **Agrégations** — COUNT, SUM, AVG, MIN, MAX
4. **CTEs** — structurer les requêtes complexes
5. **Window functions** — ROW_NUMBER, LAG, SUM OVER
6. **CASE WHEN** — logique conditionnelle
7. **Sous-requêtes** — savoir quand les éviter
8. **INSERT, UPDATE, DELETE** — manipulation de données
9. **CREATE TABLE, ALTER TABLE** — DDL
10. **EXPLAIN** — comprendre les plans d'exécution

## Comment progresser

- **Pratiquer sur des vraies données** : pas des exercices abstraits. Prenez un jeu de données qui vous intéresse.
- **Lire le SQL des autres** : les requêtes dbt, les dashboards existants.
- **Apprendre EXPLAIN** : comprendre pourquoi une requête est lente vaut plus que 100 tutos.
- **Écrire des CTEs** : dès qu'une requête dépasse 10 lignes, structurez avec des CTEs.

## En résumé

SQL est le socle du data engineering. Universel, performant, durable. Maîtrisez-le avant tout autre outil — c'est l'investissement le plus rentable de votre carrière data.

---

**Vous avez un projet data similaire ? Parlons-en → [isdataconsulting.com](https://isdataconsulting.com)**
