---
title: "PostgreSQL en production : ce que j'ai appris en optimisant des requêtes sur de vraies données"
slug: postgresql-en-production
date: 2026-02-08
description: "ACID, index, transactions, EXPLAIN — les fondamentaux PostgreSQL vus sous l'angle du data engineer qui doit optimiser des requêtes sur des tables de plusieurs centaines de millions de lignes."
categories: ["data-engineering"]
tags: ["postgresql", "sql", "optimisation", "performance", "bases-de-données", "fondamentaux"]
keywords: []
image: "/images/og-default.svg"
format: "article"
draft: false
aliases:
  - /posts/databases-sgbd-fundamentals/
  - /posts/sql-query-optimization/
  - /posts/why-learn-sql/
---

## Pourquoi cet article

Beaucoup de data engineers traitent PostgreSQL comme une boîte noire : ils savent écrire du SQL, mais ignorent pourquoi une requête est lente, pourquoi un pipeline crée des doublons à la relance, ou pourquoi un chargement plante à mi-chemin.

Cet article couvre les deux côtés : d'abord les fondamentaux théoriques qu'il faut comprendre pour ne pas travailler à l'aveugle, puis les techniques d'optimisation concrètes. Pas un cours académique — ce que j'aurais voulu avoir quand j'ai commencé à débugger des requêtes sur des tables de 200 millions de lignes.

## Quick Start (Docker)

Toute la partie pratique tourne avec cette seule commande :

```bash
docker run --name pg-prod -e POSTGRES_PASSWORD=secret -p 5432:5432 -d postgres:16
docker exec -it pg-prod psql -U postgres
```

Pour nettoyer : `docker rm -f pg-prod`.

---

## Partie 1 — Ce qu'il faut comprendre

### ACID : les 4 garanties qui comptent pour les pipelines

- **Atomicity** — une transaction passe entièrement ou pas du tout, jamais à moitié
- **Consistency** — les données restent dans un état valide après chaque opération
- **Isolation** — les transactions concurrentes ne s'interfèrent pas
- **Durability** — les données validées survivent à un crash serveur

Pourquoi ça compte concrètement : quand vous chargez des données dans plusieurs tables, les transactions garantissent la cohérence. Si une étape échoue, tout est annulé — ce qui évite les chargements partiels qui corrompent les données en aval.

```sql
BEGIN;
  INSERT INTO orders (customer_id, amount) VALUES (1, 150.00);
  UPDATE inventory SET stock = stock - 1 WHERE product_id = 42;
COMMIT;
-- Si le UPDATE échoue, le INSERT est aussi annulé.
```

### Les index : ce que le moteur fait quand vous n'en avez pas

Sans index sur une colonne filtrée, PostgreSQL effectue un **Seq Scan** — il lit chaque ligne de la table. Sur 10 lignes, c'est instantané. Sur 100 millions, c'est plusieurs secondes ou minutes.

L'index est une structure auxiliaire qui permet au moteur de sauter directement aux lignes pertinentes, comme un index de livre. Il accélère les lectures au prix d'un surcoût en écriture et en stockage.

**Règle** : indexer les colonnes utilisées dans les `WHERE`, `JOIN ON` et `ORDER BY` des requêtes fréquentes. Ne pas tout indexer : chaque index ralentit les `INSERT`/`UPDATE`.

### Pool de connexions

Chaque requête utilise une connexion. Un pipeline qui ouvre 100 connexions simultanées peut saturer PostgreSQL (qui a un `max_connections` limité). Utiliser PgBouncer ou le pool SQLAlchemy pour réutiliser les connexions existantes.

### Organisation des schémas

La convention que j'applique systématiquement :

```
raw       → données brutes ingérées sans transformation
staging   → données nettoyées, typées, renommées
marts     → tables exploitables pour les consommateurs finaux
```

---

## Partie 2 — Optimisation en pratique

### EXPLAIN ANALYZE : toujours commencer par là

Avant de toucher à quoi que ce soit :

```sql
EXPLAIN ANALYZE
SELECT o.order_id, c.name, o.amount
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_date >= '2024-01-01';
```

Ce qu'il faut lire :
- **Seq Scan** sur une grande table → problème, il manque probablement un index
- **Index Scan** → le moteur utilise un index, c'est bien
- **Actual time** → le temps réel (pas l'estimation)

**Règle absolue** : `EXPLAIN ANALYZE` avant et après toute optimisation. Sans mesure, pas d'optimisation.

### Créer les bons index

```sql
-- Index simple sur une colonne filtrée
CREATE INDEX idx_orders_date ON orders (order_date);

-- Index composite pour les requêtes avec plusieurs filtres
CREATE INDEX idx_orders_date_customer ON orders (order_date, customer_id);

-- Index partiel pour les cas les plus fréquents (plus petit, plus rapide)
CREATE INDEX idx_orders_recent ON orders (order_date)
WHERE order_date >= '2024-01-01';
```

Quand **ne pas** indexer : tables < 10 000 lignes (le Seq Scan est plus rapide), colonnes avec peu de valeurs distinctes (booléens, statuts), tables avec beaucoup d'écritures.

### Réécrire les requêtes

**Éviter SELECT *** — charger uniquement les colonnes nécessaires :

```sql
-- Mauvais
SELECT * FROM orders WHERE order_date = '2024-01-15';

-- Bon
SELECT order_id, customer_id, amount FROM orders WHERE order_date = '2024-01-15';
```

**Remplacer les sous-requêtes corrélées par des jointures** :

```sql
-- Lent : la sous-requête s'exécute pour chaque ligne
SELECT o.order_id, o.amount,
    (SELECT name FROM customers c WHERE c.customer_id = o.customer_id)
FROM orders o;

-- Rapide : une seule jointure
SELECT o.order_id, o.amount, c.name
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id;
```

**Ne jamais appliquer une fonction sur une colonne indexée dans un WHERE** :

```sql
-- L'index sur order_date n'est PAS utilisé
SELECT * FROM orders WHERE EXTRACT(YEAR FROM order_date) = 2024;

-- L'index est utilisé
SELECT * FROM orders WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01';
```

### Partitionnement pour les très grandes tables

Pour les tables qui dépassent 100M de lignes, le partitionnement divise les données en segments physiques. Le moteur ne scanne que les partitions pertinentes :

```sql
CREATE TABLE orders (
    order_id   BIGINT,
    order_date DATE,
    amount     NUMERIC(10,2)
) PARTITION BY RANGE (order_date);

CREATE TABLE orders_2024_q1 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
```

Sur une table de 500M de lignes partitionnée par mois, une requête sur un mois ne lit qu'1/24 des données. C'est le changement qui a fait passer certaines de mes requêtes de 40 secondes à 2 secondes.

### Statistiques et ANALYZE

PostgreSQL s'appuie sur les statistiques pour choisir son plan d'exécution. Après un chargement massif, les stats sont obsolètes et le planificateur peut choisir de mauvais plans :

```sql
ANALYZE orders;
```

À lancer après chaque chargement massif. Le `VACUUM ANALYZE` régulier est aussi important pour maintenir les performances au fil du temps.

### Types de données — les erreurs courantes

| Utiliser | Pour |
|---|---|
| `NUMERIC(10,2)` | Montants — jamais `FLOAT` (erreurs d'arrondi) |
| `TIMESTAMP WITH TIME ZONE` | Dès que vous manipulez plusieurs fuseaux horaires |
| `JSONB` | Données semi-structurées, indexable et performant |
| `TEXT` | Texte long sans limite imposée |

La règle que j'applique sans exception : ne jamais stocker de l'argent dans un `FLOAT`. Les erreurs d'arrondi des flottants corrompent les calculs financiers de façon silencieuse.

---

## La checklist d'optimisation

1. `EXPLAIN ANALYZE` sur la requête lente
2. Identifier les Seq Scan sur les grandes tables
3. Créer les index manquants
4. Réécrire les sous-requêtes en jointures
5. Vérifier que les filtres n'appliquent pas de fonction sur les colonnes indexées
6. `ANALYZE` après les chargements massifs
7. Partitionner si la table dépasse 100M de lignes

## En résumé

Comprendre ce que PostgreSQL fait sous le capot — index, transactions, planificateur, statistiques — change complètement la façon dont on écrit et débugge du SQL. Les patterns appris ici se transfèrent directement sur Snowflake, BigQuery ou Redshift : les moteurs changent, les principes restent.
