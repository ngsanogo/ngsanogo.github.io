---
title: "ETL vs ELT : comment choisir"
slug: etl-vs-elt-when-to-choose
date: 2026-01-26
description: "ETL ou ELT n'est pas un choix dogmatique. Un cadre de décision basé sur la sensibilité des données, la latence, les compétences de l'équipe et la plateforme."
categories: ["fundamentals"]
tags: ["etl", "elt", "architecture", "data-pipelines"]
keywords: []
image: "/images/og-default.svg"
draft: false
---

## Rappel : qu'est-ce que l'ETL ?

ETL signifie **Extract, Transform, Load**. C'est le processus fondamental du data engineering : extraire des données de systèmes sources, les transformer, puis les charger dans un système cible (warehouse, base analytique).

ELT inverse les deux dernières étapes : on charge d'abord la donnée brute dans le warehouse, puis on la transforme sur place en SQL.

La différence n'est pas cosmétique. Elle impacte l'architecture, les coûts, la sécurité et la maintenabilité.

## La vraie question

La plupart des équipes demandent « ETL ou ELT, c'est quoi le mieux ? »

La question utile : **quel pattern minimise le risque et le temps de livraison pour ce flux de données précis ?**

La réponse dépend du contexte, pas d'une doctrine.

## 5 critères de décision

### 1. Sensibilité des données

**ETL** quand il faut anonymiser ou masquer avant le stockage analytique. C'est le cas classique en santé (données patients), en finance (PII) ou avec des contraintes RGPD strictes.

**ELT** quand le landing brut est autorisé, avec un contrôle d'accès approprié au niveau du warehouse.

**Règle** : si les données brutes ne doivent jamais atterrir dans le warehouse, c'est ETL.

### 2. Force de la plateforme

**ELT** si le warehouse est puissant en SQL (BigQuery, Snowflake, Databricks). Ces plateformes sont conçues pour transformer massivement en SQL — autant les utiliser.

**ETL** si les transformations nécessitent du code complexe, des librairies spécialisées (NLP, parsing, enrichissement API) ou un pré-traitement lourd avant chargement.

### 3. Latence et coût

ELT est souvent plus rapide à mettre en place et plus facile à itérer. On charge la donnée brute, puis on itère les transformations en SQL sans toucher au pipeline d'ingestion.

ETL peut réduire les coûts de stockage et de compute quand on filtre agressivement à la source. Moins de données chargées = moins de stockage = moins de compute.

### 4. Compétences de l'équipe

- Équipe SQL-first (analysts, analytics engineers) → **ELT** plus maintenable, dbt comme standard
- Équipe Python/Scala avec des pipelines applicatifs robustes → **ETL** peut être plus propre et plus testable

### 5. Rejouabilité

ELT simplifie les replays et les backfills car la donnée brute est conservée dans le warehouse. On peut transformer à nouveau sans re-extraire.

ETL demande une conception plus soignée du replay mais offre un contrôle plus fin sur l'exposition des données.

## En pratique : 3 scénarios

**Scénario 1 — Analytics marketing, startup**
Sources : API CRM, Google Analytics, Stripe. Warehouse : BigQuery. Équipe : 1 analytics engineer.
→ **ELT**. Fivetran/Airbyte pour l'extraction, dbt pour les transformations. Simple, rapide, itérable.

**Scénario 2 — Données cliniques, hôpital**
Sources : EHR, bases de laboratoire. Données patients à anonymiser. Warehouse : PostgreSQL on-premise.
→ **ETL**. Anonymisation en Python avant chargement. Aucune donnée nominative dans le warehouse.

**Scénario 3 — Plateforme data, scale-up B2B**
Sources multiples, besoins analytiques + conformité. Warehouse : Snowflake.
→ **Hybride**. ETL léger pour les flux sensibles (masquage PII), ELT pour la modélisation analytique.

## Matrice de décision

| Contexte                                    | Premier choix |
| ------------------------------------------- | ------------- |
| Analytics marketing, itération rapide       | ELT           |
| Données cliniques avec masquage obligatoire | ETL           |
| Consolidation finance, schémas stables      | ELT           |
| Pré-traitement NLP/image avant warehouse    | ETL           |
| Besoins mixtes réglementaires + analytiques | Hybride       |

## Les erreurs classiques

- **Choisir ELT par effet de mode** alors que les données sont sensibles et ne devraient pas atterrir brutes dans le warehouse
- **Rester sur ETL par habitude** alors qu'un warehouse moderne ferait le travail en SQL, plus simple et plus maintenable
- **Ne pas documenter le choix** : 6 mois plus tard, personne ne sait pourquoi on transforme en Python et pas en dbt

## En résumé

ETL vs ELT est une décision de contexte, pas de doctrine. Choisir le pattern qui correspond le mieux aux contraintes de conformité, aux capacités de la plateforme, et à la maintenabilité par l'équipe. En cas de doute : ELT par défaut, ETL quand la sécurité l'exige.
