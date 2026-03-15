---
title: "Bases de données et PostgreSQL : les fondamentaux pour le data engineer"
slug: databases-sgbd-fundamentals
date: 2024-11-26
description: "Comprendre les SGBD de l'intérieur, puis maîtriser PostgreSQL en pratique. Le guide du data engineer : ACID, index, transactions, et exemples prêts à l'emploi."
categories: ["fundamentals"]
tags: ["bases-de-données", "postgresql", "sql", "fondamentaux", "data-engineering"]
keywords: []
series: ""
image: "/images/og-default.svg"
draft: false
---

## Pourquoi lire cet article ?

Tout pipeline data atterrit dans — ou lit depuis — une base de données. Pourtant, beaucoup de data engineers traitent les bases comme des boîtes noires : ils savent écrire du SQL, mais ignorent pourquoi une requête est lente, pourquoi un pipeline crée des doublons à la relance, ou pourquoi un chargement plante à mi-chemin.

Cet article comble ce manque en deux temps : d'abord les fondamentaux théoriques communs à tous les SGBD, puis les fondamentaux pratiques de **PostgreSQL** — la base relationnelle open-source que tout data engineer doit maîtriser.

## Quick Start (Docker)

Toute la partie pratique de cet article tourne avec cette seule commande :

```bash
docker run --name pg-fundamentals \
  -e POSTGRES_PASSWORD=secret \
  -p 5432:5432 \
  -d postgres:16

docker exec -it pg-fundamentals psql -U postgres
```

Pour nettoyer : `docker rm -f pg-fundamentals`.

---

## Partie 1 — Les fondamentaux des SGBD

### C'est quoi une base de données ?

Un SGBD (Système de Gestion de Base de Données) est un système de stockage qui permet de trouver, modifier et organiser des millions d'enregistrements instantanément, tout en garantissant la cohérence et la durabilité des données.

Ce n'est pas qu'un système de fichiers sophistiqué. Un SGBD apporte des garanties que les fichiers plats n'ont pas : cohérence, isolation, performances à l'échelle.

### Les deux grandes familles

#### Relationnel (SQL)

Tables avec lignes et colonnes. Relations entre les tables. Schéma prédéfini. Transactions ACID natives.

Exemples : **PostgreSQL**, MySQL, SQL Server, Oracle.

C'est le choix par défaut pour les données structurées. Quand le schéma est clair et que les relations entre entités comptent, le relationnel est la bonne réponse.

#### Non-relationnel (NoSQL)

Pas de schéma imposé. Formats flexibles : documents JSON, clé-valeur, graphes, colonnes larges.

Exemples : MongoDB (documents), Redis (clé-valeur), Neo4j (graphes), Cassandra (colonnes).

Utile quand : le schéma change trop vite, les volumes nécessitent un scaling horizontal massif, ou la structure des données ne rentre pas dans des tables.

### ACID : les 4 garanties fondamentales

Ces 4 propriétés sont critiques pour la fiabilité des pipelines data :

- **Atomicity** — une transaction passe entièrement ou pas du tout, jamais à moitié
- **Consistency** — les données restent dans un état valide après chaque opération
- **Isolation** — les transactions concurrentes ne s'interfèrent pas
- **Durability** — les données validées survivent à un crash serveur

**Pourquoi ça compte pour un pipeline** : quand vous chargez des données dans plusieurs tables, les transactions garantissent la cohérence. Si une étape échoue, tout est annulé — ce qui évite les chargements partiels qui corrompent les données en aval.

### Ce qui compte pour un data engineer

#### Index

Un index accélère les lectures au prix d'un coût en écriture et stockage. Sans index sur une colonne filtrée, le SGBD scanne toute la table — ce qui prend des secondes sur 10 lignes, des heures sur 100 millions.

**Règle** : indexer les colonnes utilisées dans les `WHERE`, `JOIN` et `ORDER BY` des requêtes fréquentes. Ne pas tout indexer : chaque index ralentit les INSERT/UPDATE.

#### Transactions dans un pipeline

```sql
BEGIN;
  INSERT INTO orders (customer_id, amount) VALUES (1, 150.00);
  UPDATE inventory SET stock = stock - 1 WHERE product_id = 42;
COMMIT;
```

Si le `UPDATE` échoue, le `ROLLBACK` annule l'`INSERT`. Les deux opérations réussissent ensemble ou échouent ensemble.

#### Pool de connexions

Chaque requête utilise une connexion. Un pipeline qui ouvre 100 connexions simultanées peut saturer la base. Utiliser un pool (PgBouncer, SQLAlchemy pool) pour réutiliser les connexions existantes.

#### Organisation des schémas

```
raw       → données brutes ingérées sans transformation
staging   → données nettoyées, typées, renommées
marts     → tables exploitables pour les consommateurs finaux
```

### Relationnel vs NoSQL : comment choisir

| Critère | Relationnel | NoSQL |
|---|---|---|
| Données structurées | Oui | Non nécessaire |
| Relations complexes | Oui | Limité |
| Schéma flexible | Non | Oui |
| Transactions ACID | Natif | Partiel |
| Volume massif (scaling horizontal) | Limité | Conçu pour |

**Règle pragmatique** : pour 90 % des projets data, commencer par du relationnel. Ajouter du NoSQL uniquement quand un besoin spécifique le justifie pleinement.

---

## Partie 2 — PostgreSQL en pratique

### Pourquoi PostgreSQL

PostgreSQL est la base relationnelle open source la plus complète. Fiable, extensible, gratuite. C'est le choix par défaut pour :
- les bases applicatives et les entrepôts de données de taille moyenne
- le développement local avant de migrer sur un cloud warehouse (Snowflake, BigQuery, Redshift)
- les projets qui ont besoin de JSONB, de partitionnement natif, de window functions ou d'extensions

Tous les outils de la modern data stack s'y connectent nativement : Airflow, dbt, Metabase, Great Expectations.

### Les commandes psql essentielles

```sql
\l              -- Lister les bases
\c ma_base      -- Se connecter à une base
\dt             -- Lister les tables
\d ma_table     -- Décrire une table (colonnes, types, contraintes)
\q              -- Quitter
```

### Créer une base et des tables

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

**SERIAL** : auto-incrément. **NUMERIC(10,2)** : précision décimale pour les montants. **TIMESTAMP DEFAULT NOW()** : horodatage automatique d'ingestion.

### Les types de données importants

| Type | Usage |
|---|---|
| INTEGER / BIGINT | Identifiants, compteurs |
| NUMERIC(p, s) | Montants, calculs financiers précis |
| VARCHAR(n) | Texte court et contraint |
| TEXT | Texte long sans limite |
| DATE | Dates sans heure |
| TIMESTAMP | Dates avec heure |
| BOOLEAN | Vrai/faux |
| JSONB | JSON indexable — semi-structuré |

**Règle absolue** : utiliser `NUMERIC` pour l'argent, jamais `FLOAT` (les flottants ont des erreurs d'arrondi qui corrompent les calculs financiers). Préférer `TIMESTAMP WITH TIME ZONE` dès qu'on manipule plusieurs fuseaux horaires.

### Requêtes courantes

```sql
-- Insérer
INSERT INTO orders (customer_id, amount, order_date)
VALUES (1, 150.00, '2024-01-15');

-- Lire avec filtre et jointure
SELECT o.order_id, c.name, o.amount
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_date >= '2024-01-01'
ORDER BY o.amount DESC;

-- Mettre à jour
UPDATE orders SET amount = 175.00 WHERE order_id = 1;

-- Supprimer (avec filtre — jamais de DELETE sans WHERE en prod)
DELETE FROM orders WHERE order_date < '2023-01-01';
```

### Index : la clé de la performance

Sans index, PostgreSQL effectue un **Seq Scan** (scan complet de la table). Avec un index sur les colonnes filtrées, la requête est instantanée même sur des centaines de millions de lignes.

```sql
-- Index simple
CREATE INDEX idx_orders_date ON orders (order_date);

-- Index composite (requêtes filtrant sur deux colonnes)
CREATE INDEX idx_orders_date_customer ON orders (order_date, customer_id);

-- Index partiel (optimise les cas les plus fréquents)
CREATE INDEX idx_orders_recent ON orders (order_date)
WHERE order_date >= '2024-01-01';
```

Vérifier qu'un index est utilisé : `EXPLAIN ANALYZE SELECT ...` — chercher `Index Scan` au lieu de `Seq Scan`.

### Fonctionnalités avancées utiles

#### JSONB — données semi-structurées

```sql
CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    payload  JSONB NOT NULL
);

SELECT payload->>'event_type' AS event_type
FROM events
WHERE payload @> '{"source": "web"}';
```

JSONB est indexable et performant — c'est la solution PostgreSQL pour les données d'événements ou d'API.

#### Window functions

```sql
SELECT
    customer_id,
    order_date,
    amount,
    SUM(amount) OVER (PARTITION BY customer_id ORDER BY order_date) AS cumul
FROM orders;
```

#### CTEs (Common Table Expressions)

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

### Bonnes pratiques

1. **Toujours une clé primaire** — pas de table sans PK, c'est la base de l'idempotence des pipelines
2. **Contraintes explicites** : `NOT NULL`, `UNIQUE`, `FOREIGN KEY` — elles protègent la qualité des données à la source
3. **Nommer les index** : `idx_table_colonne` — facilite le diagnostic sous `EXPLAIN`
4. **`VACUUM` et `ANALYZE` réguliers** — PostgreSQL en a besoin pour maintenir ses performances après des chargements massifs
5. **Sauvegardes** : `pg_dump -Fc ma_base > backup.dump` — automatiser en production

## En résumé

Maîtriser les fondamentaux SGBD — ACID, index, transactions, schémas — est le socle de tout data engineer sérieux. PostgreSQL est le meilleur terrain d'apprentissage : les patterns appris ici se transfèrent directement sur Snowflake, BigQuery ou Redshift.

Les deux articles à lire ensuite pour aller plus loin :
- [Optimisation SQL →](/posts/sql-query-optimization/) pour les plans d'exécution et les stratégies d'index avancées
- [ETL vs ELT →](/posts/etl-vs-elt-when-to-choose/) pour décider comment charger les données dans votre base

---

**Vous avez un projet data similaire ? Parlons-en → [isdataconsulting.com](https://isdataconsulting.com)**
