---
title: "Construire un data warehouse de zéro : retour d'expérience à l'Institut Jérôme Lejeune"
slug: how-to-build-a-data-warehouse-from-scratch-jerome-lejeune
date: 2026-02-16
description: "Un plan concret pour construire un data warehouse de zéro en contexte recherche médicale : cadrage, modélisation, pipelines, gouvernance et adoption."
categories: ["architecture"]
tags: ["data-warehouse", "santé", "modélisation", "gouvernance", "etl"]
draft: false
---

## Le vrai défi

Construire un warehouse de zéro n'est pas d'abord un problème d'outillage. C'est un problème de séquencement : décider quoi faire maintenant, quoi reporter, et quoi standardiser dès le départ.

En contexte recherche médicale, c'est encore plus critique : la qualité, la traçabilité et la confiance doivent être intégrées dès le premier jour.

## Phase 1 — Cadrage (semaines 1-4)

Avant d'écrire du code, comprendre :
- quels systèmes sources existent (DPI, LIMS, fichiers Excel, bases Access)
- qui a besoin de quoi (médecins, chercheurs, direction)
- quelles décisions seront prises avec ces données

Le livrable : un périmètre clair avec 3-5 cas d'usage prioritaires.

## Phase 2 — Modélisation (semaines 3-6)

Commencer par un schéma en étoile sur le premier cas d'usage :
- une table de faits (consultations, échantillons, prescriptions)
- les dimensions associées (patient, médecin, date, protocole)

Ne pas modéliser tout le SI. Commencer petit, livrer, itérer.

## Phase 3 — Pipelines (semaines 5-10)

Architecture en 3 couches :
- **raw** : copie brute des sources, sans transformation
- **staging** : nettoyage, renommage, typage
- **marts** : logique métier, tables consommables

Chaque couche est idempotente. On peut tout relancer sans risque de duplication.

## Phase 4 — Gouvernance (continu)

Dès le premier pipeline en production :
- documentation des tables et des colonnes (dbt docs ou simple fichier)
- tests de qualité automatisés (unicité, non-null, cohérence)
- lignage : savoir d'où vient chaque donnée

En contexte médical, la traçabilité n'est pas optionnelle. C'est une exigence réglementaire.

## Phase 5 — Adoption (continu)

Le meilleur warehouse du monde est inutile si personne ne l'utilise.

- Former les équipes métier à interroger les marts (SQL basique ou BI)
- Livrer des dashboards concrets dès les premières semaines
- Intégrer les retours métier dans les itérations suivantes

## Ce que cette expérience m'a appris

Le séquencement compte plus que la techno. Les quick wins construisent la confiance. Et en santé, la gouvernance n'est pas un luxe — c'est la condition pour que le projet survive.

---

**Vous avez un projet data similaire ? Parlons-en → [isdataconsulting.com](https://isdataconsulting.com)**
