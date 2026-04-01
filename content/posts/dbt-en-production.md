---
title: "dbt en production : au-delà du getting started"
slug: dbt-en-production
date: 2026-01-05
description: "dbt en production, c'est autre chose que le getting started. Tests de non-régression, sources contractuelles, séparation staging/marts, gestion des environnements."
categories: ["tools"]
tags: ["dbt", "sql", "analytics-engineering", "production"]
keywords: []
image: "/images/og-default.svg"
draft: false
aliases:
  - /posts/dbt-pour-les-nuls-guide-pratique/
  - /posts/dbt-en-production/
---

## dbt, c'est quoi en une phrase

dbt te permet d'écrire des transformations SQL comme du code versionné, testé, documenté et déployé proprement.

## Quick Start (Docker)

Pour tester dbt sans rien installer, avec PostgreSQL :

```bash
docker run --name pg-dbt -e POSTGRES_PASSWORD=secret -p 5432:5432 -d postgres:16
docker run --rm -it python:3.12-slim bash -c "
  pip install -q dbt-postgres &&
  dbt init my_project &&
  cd my_project &&
  bash
"
```

Configurez la connexion vers `host.docker.internal:5432` et lancez `dbt debug`.

## Pourquoi dbt change la donne

Sans dbt, on voit souvent :
- des requêtes SQL copiées dans plusieurs endroits
- des définitions métier incohérentes
- peu de tests
- une doc obsolète

Avec dbt :
- chaque modèle est un fichier clair
- les dépendances sont explicites
- les tests sont automatisés
- la documentation est générée

## Le minimum à comprendre

### 1. `model`

Un model = une transformation SQL matérialisée en table ou view.

### 2. `ref()`

`ref('nom_modele')` déclare une dépendance entre models.

### 3. tests

Deux niveaux :
- tests génériques (`not_null`, `unique`, `accepted_values`)
- tests métier personnalisés

### 4. `sources`

Permet de documenter et tester les tables d'entrée.

## Structure simple pour commencer

```text
models/
  staging/
    stg_customers.sql
    stg_orders.sql
  marts/
    fct_orders.sql
    dim_customers.sql
  schema.yml
```

Règle utile :
- staging = nettoyage léger + renommage cohérent
- marts = logique métier et indicateurs

## Exemple concret

```sql
-- models/staging/stg_orders.sql
select
  order_id,
  customer_id,
  cast(order_date as date) as order_date,
  amount
from {{ source('app', 'orders') }}
where order_id is not null
```

```sql
-- models/marts/fct_orders.sql
select
  o.order_id,
  o.customer_id,
  o.order_date,
  o.amount,
  c.country
from {{ ref('stg_orders') }} o
left join {{ ref('stg_customers') }} c
  on o.customer_id = c.customer_id
```

## Les 5 commandes à connaître

- `dbt debug`
- `dbt run`
- `dbt test`
- `dbt build`
- `dbt docs generate`

## Plan de déploiement en 3 phases

1. **Pilote** : un domaine métier, 5 à 10 models, tests de base.
2. **Standardisation** : conventions de nommage, revues SQL, CI.
3. **Industrialisation** : monitoring des runs, SLA, ownership par domaine.

## Erreurs fréquentes

- tout mettre dans un seul model géant
- ignorer les tests source
- mélanger logique métier et nettoyage dans les marts
- ne pas versionner les changements de définitions KPI

## En résumé

dbt n'est pas magique. C'est surtout une discipline qui rend les transformations lisibles, testables et maintenables. Commence petit, impose des conventions, et monte en puissance progressivement.
