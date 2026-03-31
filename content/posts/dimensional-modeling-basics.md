---
title: "Modélisation dimensionnelle : structurer un data warehouse"
slug: dimensional-modeling-basics
date: 2026-02-20
description: "Tables de faits, tables de dimensions, schéma en étoile. Comment structurer un warehouse que les analystes peuvent interroger facilement."
categories: ["data-modeling"]
tags: ["modélisation", "data-warehouse", "schéma-étoile", "star-schema"]
keywords: []
image: "/images/og-default.svg"
format: "article"
draft: false
---

## Le problème

Les données brutes sont chargées dans le warehouse. Des tables partout. Des jointures complexes. Les analystes passent plus de temps à comprendre le modèle qu'à produire des insights.

La modélisation dimensionnelle résout ce problème en organisant les données pour la consommation, pas pour le stockage.

## Quick Start (Docker)

Pour tester les exemples SQL de cet article :

```bash
docker run --name pg-dim -e POSTGRES_PASSWORD=secret -d postgres:16
docker exec -it pg-dim psql -U postgres
```

Copiez les `CREATE TABLE` et requêtes directement dans `psql`. Pour nettoyer : `docker rm -f pg-dim`.

## Le schéma en étoile

Le modèle le plus courant : une table de faits au centre, entourée de tables de dimensions.

### Table de faits

Elle contient les événements mesurables : ventes, commandes, visites, prescriptions. Chaque ligne = un événement. Les colonnes = des mesures (montant, quantité) et des clés vers les dimensions.

```sql
CREATE TABLE fct_orders (
    order_id BIGINT PRIMARY KEY,
    customer_key INT REFERENCES dim_customers(customer_key),
    product_key INT REFERENCES dim_products(product_key),
    date_key INT REFERENCES dim_dates(date_key),
    quantity INT,
    amount DECIMAL(10, 2)
);
```

### Tables de dimensions

Elles décrivent le contexte : qui, quoi, quand, où. Client, produit, date, localisation.

```sql
CREATE TABLE dim_customers (
    customer_key INT PRIMARY KEY,
    customer_id VARCHAR(50),
    name VARCHAR(100),
    segment VARCHAR(50),
    country VARCHAR(50)
);
```

### Pourquoi ça marche

Les analystes écrivent des requêtes simples et performantes :

```sql
SELECT d.month, c.segment, SUM(f.amount)
FROM fct_orders f
JOIN dim_dates d ON f.date_key = d.date_key
JOIN dim_customers c ON f.customer_key = c.customer_key
GROUP BY d.month, c.segment;
```

Pas de sous-requêtes complexes. Pas de jointures en chaîne.

## Faits vs dimensions : comment distinguer

- **Fait** : mesurable, numérique, additionnable. Montant, quantité, durée.
- **Dimension** : descriptif, textuel, filtrable. Nom, catégorie, date, pays.

Règle : si vous pouvez faire un `SUM()` dessus, c'est probablement un fait.

## Slowly Changing Dimensions (SCD)

Les dimensions changent. Un client déménage, un produit change de catégorie.

- **Type 1** : écraser l'ancienne valeur. Simple mais perd l'historique.
- **Type 2** : ajouter une nouvelle ligne avec dates de début/fin. Conserve l'historique.

Type 2 est le standard quand l'historique compte.

## Erreurs courantes

**Des faits trop larges.** Si une table de faits a 50 colonnes descriptives, ce sont des dimensions déguisées. Extraire dans des tables dédiées.

**Pas de table de dates.** Une `dim_dates` avec jour, semaine, mois, trimestre, année, jour férié simplifie toutes les analyses temporelles.

**Normaliser les dimensions.** En warehouse, la dénormalisation est normale. Pas besoin de 3NF pour les dimensions — les jointures supplémentaires ralentissent les requêtes.

## En résumé

La modélisation dimensionnelle n'est pas académique. C'est l'approche qui rend un warehouse utilisable au quotidien. Faits au centre, dimensions autour, schéma en étoile. Commencez par un domaine métier, livrez un premier mart, et étendez progressivement.
