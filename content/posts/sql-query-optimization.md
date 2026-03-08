---
title: "Optimisation SQL : rendre ses requêtes rapides"
slug: sql-query-optimization
date: 2026-02-08
description: "Les techniques d'optimisation SQL essentielles. EXPLAIN, index, réécriture de requêtes et bonnes pratiques pour des performances en production."
categories: ["data-engineering", "sql"]
tags: ["sql", "optimisation", "performance", "index", "explain"]
keywords: []
series: ""
image: "/images/og-default.svg"
draft: false
---

## Pourquoi optimiser

Une requête lente, c'est un pipeline qui dépasse sa fenêtre, un dashboard qui timeout, un utilisateur qui attend. L'optimisation SQL n'est pas un luxe — c'est une compétence de base du data engineer.

## EXPLAIN : comprendre avant d'optimiser

Avant de toucher à quoi que ce soit, regarder le plan d'exécution :

```sql
EXPLAIN ANALYZE
SELECT o.order_id, c.name, o.amount
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_date >= '2024-01-01';
```

Ce qu'il faut lire :
- **Seq Scan** : scan complet de la table → souvent le problème
- **Index Scan** : utilise un index → rapide
- **Hash Join** vs **Nested Loop** : le moteur choisit la stratégie de jointure
- **Actual time** : le temps réel (pas l'estimation)

**Règle** : toujours `EXPLAIN ANALYZE` avant et après une optimisation. Sans mesure, pas d'optimisation.

## Les index

### Créer les bons index

```sql
-- Index simple sur une colonne filtrée
CREATE INDEX idx_orders_date ON orders (order_date);

-- Index composite pour les requêtes avec plusieurs filtres
CREATE INDEX idx_orders_date_customer ON orders (order_date, customer_id);

-- Index partiel pour les cas fréquents
CREATE INDEX idx_orders_recent ON orders (order_date)
WHERE order_date >= '2024-01-01';
```

### Quand indexer

- Colonnes dans les `WHERE`
- Colonnes dans les `JOIN ... ON`
- Colonnes dans les `ORDER BY`
- Colonnes avec haute cardinalité (beaucoup de valeurs distinctes)

### Quand ne pas indexer

- Tables petites (< 10 000 lignes) : le scan séquentiel est plus rapide
- Colonnes avec peu de valeurs distinctes (booléens, statuts)
- Tables avec beaucoup d'écritures : chaque index ralentit les INSERT/UPDATE

## Réécrire les requêtes

### Éviter le SELECT *

```sql
-- Mauvais : charge toutes les colonnes
SELECT * FROM orders WHERE order_date = '2024-01-15';

-- Bon : charge uniquement ce qui est nécessaire
SELECT order_id, customer_id, amount FROM orders WHERE order_date = '2024-01-15';
```

### Remplacer les sous-requêtes corrélées

```sql
-- Lent : sous-requête exécutée pour chaque ligne
SELECT o.order_id, o.amount,
    (SELECT name FROM customers c WHERE c.customer_id = o.customer_id)
FROM orders o;

-- Rapide : une seule jointure
SELECT o.order_id, o.amount, c.name
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id;
```

### Utiliser EXISTS au lieu de IN

```sql
-- Lent sur les grandes listes
SELECT * FROM orders
WHERE customer_id IN (SELECT customer_id FROM vip_customers);

-- Plus efficace
SELECT * FROM orders o
WHERE EXISTS (
    SELECT 1 FROM vip_customers v
    WHERE v.customer_id = o.customer_id
);
```

### Éviter les fonctions sur les colonnes indexées

```sql
-- L'index sur order_date n'est PAS utilisé
SELECT * FROM orders WHERE EXTRACT(YEAR FROM order_date) = 2024;

-- L'index est utilisé
SELECT * FROM orders WHERE order_date >= '2024-01-01' AND order_date < '2025-01-01';
```

## Partitionnement

Pour les très grandes tables, le partitionnement divise les données en segments physiques.

```sql
CREATE TABLE orders (
    order_id   BIGINT,
    order_date DATE,
    amount     NUMERIC(10,2)
) PARTITION BY RANGE (order_date);

CREATE TABLE orders_2024_q1 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
```

Le moteur ne scanne que les partitions pertinentes. Sur une table de 500M de lignes, ça change tout.

## Les statistiques

PostgreSQL s'appuie sur les statistiques pour choisir son plan d'exécution :

```sql
ANALYZE orders;
```

Après un chargement massif, toujours lancer `ANALYZE`. Sinon le planificateur travaille avec des stats obsolètes et choisit de mauvais plans.

## Checklist d'optimisation

1. `EXPLAIN ANALYZE` sur la requête lente
2. Identifier les Seq Scan sur les grandes tables
3. Créer les index manquants
4. Réécrire les sous-requêtes en jointures
5. Vérifier que les filtres n'appliquent pas de fonction sur les colonnes indexées
6. `ANALYZE` après les chargements massifs
7. Partitionner si la table dépasse 100M de lignes

## En résumé

L'optimisation SQL commence par EXPLAIN ANALYZE, passe par les index et la réécriture de requêtes, et finit par le partitionnement pour les très gros volumes. Mesurez, corrigez, re-mesurez.

---

**Vous avez un projet data similaire ? Parlons-en → [isdataconsulting.com](https://isdataconsulting.com)**
