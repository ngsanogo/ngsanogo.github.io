---
title: "dbt pour les nuls: guide pratique"
slug: dbt-pour-les-nuls-guide-pratique
date: 2026-01-05
description: "Guide simple et concret pour debuter avec dbt: models, tests, documentation, et deploiement progressif en production."
categories: ["tools"]
tags: ["dbt", "sql", "analytics-engineering", "beginners"]
draft: false
---

## dbt, c'est quoi en une phrase

dbt te permet d'ecrire des transformations SQL comme du code versionne, teste, documente, et deploye proprement.

## Pourquoi dbt change la donne

Sans dbt, on voit souvent:
- des requetes SQL copiees dans plusieurs endroits
- des definitions metier incoherentes
- peu de tests
- une doc obsolete

Avec dbt:
- chaque modele est un fichier clair
- les dependances sont explicites
- les tests sont automatises
- la documentation est generee

## Le minimum a comprendre

### 1. `model`

Un model = une transformation SQL materialisee en table ou view.

### 2. `ref()`

`ref('nom_modele')` declare une dependance entre models.

### 3. tests

Deux niveaux:
- tests generiques (`not_null`, `unique`, `accepted_values`)
- tests metier personnalises

### 4. `sources`

Permet de documenter et tester les tables d'entree.

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

Regle utile:
- staging = nettoyage leger + renommage coherent
- marts = logique metier et indicateurs

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

## Les 5 commandes a connaitre

- `dbt debug`
- `dbt run`
- `dbt test`
- `dbt build`
- `dbt docs generate`

## Plan de deploiement en 3 phases

1. **Pilote**: un domaine metier, 5 a 10 models, tests de base.
2. **Standardisation**: conventions de nommage, revues SQL, CI.
3. **Industrialisation**: monitoring des runs, SLA, ownership par domaine.

## Erreurs frequentes

- tout mettre dans un seul model geant
- ignorer les tests source
- melanger logique metier et nettoyage dans les marts
- ne pas versionner les changements de definitions KPI

## Final

dbt n'est pas magique. C'est surtout une discipline qui rend les transformations lisibles, testables, et maintainables. Commence petit, impose des conventions, et monte en puissance progressivement.

---

**Vous avez un projet data similaire ? Parlons-en → [isdataconsulting.com](https://isdataconsulting.com)**
