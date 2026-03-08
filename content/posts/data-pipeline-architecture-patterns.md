---
title: "Batch, micro-batch, streaming : quel pattern pour quel besoin"
slug: data-pipeline-architecture-patterns
date: 2026-02-01
description: "Les 3 patterns d'architecture de pipeline data comparés. Critères de choix concrets selon la fraîcheur, le volume et la complexité de votre contexte."
categories: ["data-engineering"]
tags: ["architecture", "data-pipelines", "etl", "streaming", "batch"]
keywords: []
series: ""
image: "/images/og-default.svg"
draft: false
---

## Le choix qui structure tout

Le premier choix d'architecture d'une plateforme data est : comment la donnée circule de la source à la destination ? Ce choix impacte le tooling, les coûts, les compétences nécessaires et les délais de livraison.

Il existe 3 patterns. Chacun a ses cas d'usage légitimes.

## Pattern 1 : Batch

La donnée s'accumule, puis est traitée en bloc à intervalles réguliers (toutes les nuits, toutes les heures).

**Fonctionnement** : extraction planifiée → transformation → chargement dans le warehouse.

**Quand l'utiliser :**
- La fraîcheur quotidienne ou horaire suffit
- Le volume est élevé mais pas continu
- L'équipe est petite et la simplicité est prioritaire
- Le budget calcul doit rester bas

**Limites** : donnée toujours en retard, temps de récupération long après un échec, gère mal les données tardives.

## Pattern 2 : Micro-batch

Du batch avec des intervalles plus courts — toutes les 5 à 15 minutes.

**Fonctionnement** : même logique que le batch, mais orchestré en boucles courtes (via Airflow par exemple).

**Quand l'utiliser :**
- Besoin de fraîcheur inférieure à l'heure sans la complexité du streaming
- L'infrastructure batch est déjà en place
- Le volume est gérable par tranches

**Limites** : pas du temps réel, overhead d'orchestration si les intervalles sont très courts.

## Pattern 3 : Streaming

La donnée est traitée enregistrement par enregistrement, en continu, au fil de l'eau.

**Fonctionnement** : les événements arrivent dans un broker (Kafka, Kinesis), sont transformés et chargés quasi-instantanément.

**Quand l'utiliser :**
- Détection de fraude, alertes temps réel
- Données IoT ou événementielles à fort débit
- Le métier exige une latence de quelques secondes

**Limites** : complexité opérationnelle élevée, debugging difficile, coûts plus importants, compétences spécialisées nécessaires.

## Tableau de décision

| Critère | Batch | Micro-batch | Streaming |
|---|---|---|---|
| Fraîcheur | Heures/jour | Minutes | Secondes |
| Complexité ops | Basse | Moyenne | Haute |
| Coût | Bas | Moyen | Élevé |
| Debugging | Simple | Moyen | Difficile |
| Cas typique | Reporting, warehouse | Dashboards opérationnels | Fraude, alertes |

## Conseil pratique

Commencer par du batch. C'est le plus simple, le plus fiable, le moins cher. Passer en micro-batch si la fraîcheur quotidienne ne suffit plus. N'introduire du streaming que si le besoin temps réel est validé par un cas métier concret — pas par une envie technique.

La plupart des plateformes data en production utilisent un mix batch + micro-batch. Le streaming pur reste l'exception.

---

**Vous avez un projet data similaire ? Parlons-en → [isdataconsulting.com](https://isdataconsulting.com)**
