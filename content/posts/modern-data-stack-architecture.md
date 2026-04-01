---
title: "Modern data stack : ce qui compte vraiment"
slug: modern-data-stack-architecture
date: 2026-01-30
description: "Les composants essentiels d'une plateforme data moderne. Ce qu'il faut choisir, dans quel ordre, et ce qui peut attendre."
categories: ["architecture"]
tags: ["architecture", "modern-data-stack", "elt", "cloud", "data-warehouse"]
keywords: []
image: "/images/og-default.svg"
format: "article"
draft: false
aliases:
  - /posts/essential-data-engineering-tools/
---

## Ce qui a changé

Il y a 10 ans, une plateforme data coûtait des millions et prenait des mois à déployer. Aujourd'hui, une startup peut avoir une stack data solide pour quelques centaines d'euros par mois.

La raison : le cloud, le pay-per-use, et des outils composables qui font chacun une seule chose bien.

## Les 5 couches d'une stack moderne

### 1. Sources

Tout ce qu'on veut analyser : bases applicatives (PostgreSQL, MySQL), outils SaaS (Salesforce, Stripe, HubSpot), fichiers, flux d'événements.

### 2. Ingestion

Déplacer la donnée des sources vers le warehouse. L'approche moderne est ELT : on charge d'abord brut, on transforme après dans le warehouse.

Outils courants : Fivetran, Airbyte, scripts custom pour les sources exotiques.

**Règle** : ne construire du custom que si aucun connecteur n'existe, si la latence requise est inférieure à la minute, ou si le volume rend les connecteurs trop chers.

### 3. Stockage (warehouse)

Le cœur de la stack. Toute la donnée vit ici, toutes les transformations y tournent.

Les options principales :
- **Snowflake** : séparation stockage/calcul, facturation à la seconde
- **BigQuery** : serverless, paiement à la requête, écosystème Google
- **Databricks** : lakehouse (lac + warehouse combiné), bon pour le ML

Pour la plupart des cas, le choix entre ces 3 dépend de l'écosystème existant et du budget.

### 4. Transformation

C'est là que la donnée brute devient exploitable. L'outil dominant est **dbt** : SQL versionné, testé, documenté.

Le pattern :
- `staging` : nettoyage léger, renommage
- `marts` : logique métier, indicateurs, tables consommables

### 5. Restitution

Dashboards, rapports, API. Looker, Metabase, Tableau, Power BI.

La couche la plus visible mais la moins importante à choisir en premier. Un bon warehouse avec des transformations propres rend n'importe quel outil de visualisation efficace.

## Les couches transverses

- **Orchestration** : Airflow ou Dagster pour planifier et enchaîner les jobs
- **Observabilité** : monitoring des pipelines, alertes sur la qualité de données
- **Catalogue** : documentation des métriques et des tables

## Par où commencer

1. **Warehouse** : choisir et déployer en premier
2. **Ingestion** : connecter les 3-5 sources prioritaires
3. **Transformation** : structurer staging + marts pour un premier cas d'usage
4. **Dashboard** : livrer un premier indicateur utile

Ne pas tout déployer en même temps. Rendre une couche fiable avant de passer à la suivante.

## Ce qui peut attendre

- Le catalogue de données (utile à partir de 10+ sources)
- Le streaming (commencer par du batch)
- La couche sémantique (attendre d'avoir des incohérences de métriques)
- Le data mesh (attendre d'avoir plusieurs domaines data matures)

La meilleure stack est celle qui livre de la valeur vite, pas celle qui a le plus de composants.

## Pour aller plus loin

Articles associés pour approfondir chaque couche :

- **Ingestion** → [ETL vs ELT : comment choisir](/posts/etl-vs-elt-when-to-choose/)
- **Transformation** → [dbt en production : au-delà du getting started](/posts/dbt-pour-les-nuls-guide-pratique/)
- **Orchestration** → [MinIO et Airflow : construire un data lake local](/posts/minio-airflow-data-lake/)
- **Fiabilité** → [Monitoring des pipelines data en production](/posts/monitoring-data-pipelines/)
- **Architecture** → [Batch, micro-batch, streaming : quel pattern ?](/posts/data-pipeline-architecture-patterns/)
