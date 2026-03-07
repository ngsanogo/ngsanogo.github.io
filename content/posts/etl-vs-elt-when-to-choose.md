---
title: "ETL vs ELT : comment choisir"
slug: etl-vs-elt-when-to-choose
date: 2026-01-26
description: "ETL ou ELT n'est pas un choix dogmatique. Un cadre de décision basé sur la sensibilité des données, la latence, les compétences de l'équipe et la plateforme."
categories: ["fundamentals"]
tags: ["etl", "elt", "architecture", "data-pipelines"]
draft: false
---

## Rappel : qu'est-ce que l'ETL ?

ETL signifie **Extract, Transform, Load**. C'est le processus fondamental du data engineering : extraire des données de systèmes sources, les transformer, puis les charger dans un système cible (warehouse, base analytique).

ELT inverse les deux dernières étapes : on charge d'abord la donnée brute dans le warehouse, puis on la transforme sur place en SQL.

## La vraie question

La plupart des équipes demandent « ETL ou ELT, c'est quoi le mieux ? »

La question utile : **quel pattern minimise le risque et le temps de livraison pour ce flux de données précis ?**

## 5 critères de décision

### 1. Sensibilité des données

**ETL** quand il faut anonymiser ou masquer avant le stockage analytique (données de santé, PII, contraintes RGPD strictes).

**ELT** quand le landing brut est autorisé avec un contrôle d'accès approprié.

### 2. Force de la plateforme

**ELT** si le warehouse est puissant en SQL (BigQuery, Snowflake, Databricks).

**ETL** si les transformations nécessitent du code complexe, des librairies spécialisées, ou un enrichissement externe avant chargement.

### 3. Latence et coût

ELT est souvent plus rapide à mettre en place et plus facile à itérer.

ETL peut réduire les coûts de stockage et compute quand on filtre agressivement à la source.

### 4. Compétences de l'équipe

Équipe SQL-first → ELT plus maintenable.

Équipe Python/Scala avec des pipelines applicatifs robustes → ETL peut être plus propre.

### 5. Rejouabilité

ELT simplifie les replays et backfills car la donnée brute est conservée.

ETL demande une conception plus soignée du replay mais offre un contrôle plus fin sur l'exposition des données.

## Règle pratique

- **ELT par défaut** pour les workloads analytiques modernes
- **ETL délibérément** pour les flux sensibles, fortement normalisés, ou nécessitant du pré-traitement lourd
- **Hybride** dans la plupart des systèmes réels : ETL léger pour la conformité, puis ELT pour la modélisation

## Matrice de décision

| Contexte | Premier choix |
|---|---|
| Analytics marketing, itération rapide | ELT |
| Données cliniques avec masquage obligatoire | ETL |
| Consolidation finance, schémas stables | ELT |
| Pré-traitement NLP/image avant warehouse | ETL |
| Besoins mixtes réglementaires + analytiques | Hybride |

## En résumé

ETL vs ELT est une décision de contexte, pas de doctrine. Choisir le pattern qui correspond le mieux aux contraintes de conformité, aux capacités de la plateforme, et à la maintenabilité par l'équipe.

---

**Vous avez un projet data similaire ? Parlons-en → [isdataconsulting.com](https://isdataconsulting.com)**
