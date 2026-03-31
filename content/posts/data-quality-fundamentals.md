---
title: "Les 6 dimensions de la qualité des données — et celles qu'on oublie toujours"
slug: data-quality-fundamentals
date: 2026-02-03
description: "La qualité des données est le socle de tout projet data fiable. Les 6 dimensions, les erreurs courantes et les stratégies concrètes pour l'implémenter."
categories: ["data-quality"]
tags: ["qualité-données", "data-engineering", "bonnes-pratiques"]
keywords: []
image: "/images/og-default.svg"
format: "article"
draft: false
---

## Pourquoi c'est le sujet n°1

Une donnée de mauvaise qualité coûte cher. Pas seulement en argent : en confiance. Quand un dashboard affiche des chiffres incohérents, personne ne le regarde plus. Et quand personne ne regarde, les décisions se prennent au doigt mouillé.

Le vrai coût de la mauvaise qualité, c'est l'érosion de la confiance dans la plateforme data.

## Les 6 dimensions de la qualité

### 1. Complétude

Les données attendues sont-elles présentes ? Des colonnes `NULL` partout, des lignes manquantes, des fichiers vides — c'est le symptôme le plus fréquent.

### 2. Exactitude

Les données correspondent-elles à la réalité ? Un patient de 250 ans, un montant négatif sur une facture — l'exactitude se vérifie par des règles métier.

### 3. Cohérence

Les mêmes données racontent-elles la même chose partout ? Si le CA diffère entre deux dashboards, c'est un problème de cohérence.

### 4. Fraîcheur

Les données sont-elles à jour ? Un pipeline en retard de 48h rend les dashboards inutiles pour le pilotage opérationnel.

### 5. Unicité

Pas de doublons. Une même commande comptée deux fois fausse tous les indicateurs en aval.

### 6. Validité

Les données respectent-elles le format attendu ? Dates au bon format, emails valides, codes postaux cohérents.

## Les erreurs qui reviennent

**Tester trop tard.** Vérifier la qualité après le chargement en production, c'est éteindre un incendie. Testez à chaque étape du pipeline.

**S'appuyer sur des tests manuels.** Les checks doivent être automatisés et intégrés au pipeline.

**Ignorer les données sources.** La meilleure validation du monde ne compense pas une source pourrie. Remontez les problèmes à la source.

**Pas d'alertes.** Un test qui échoue sans prévenir personne ne sert à rien.

## Stratégie concrète

### Niveau 1 — Tests de base (semaine 1)

- clés primaires uniques
- colonnes critiques non nulles
- volumes cohérents (pas de table vide sans raison)

### Niveau 2 — Tests métier (mois 1)

- règles métier (montant > 0, date dans le futur impossible)
- cohérence entre tables (foreign keys valides)
- comparaison de volumes source vs destination

### Niveau 3 — Observabilité (mois 3)

- détection d'anomalies sur les volumes
- alertes sur la fraîcheur
- tableau de bord qualité pour les équipes métier

## Outils

dbt tests pour les validations SQL. Great Expectations ou Soda pour des checks plus avancés. Alertes Slack/email pour la notification.

L'outil compte moins que la discipline : des tests écrits, automatisés, qui alertent quand ça casse.

## En résumé

La qualité des données n'est pas un projet ponctuel. C'est une pratique continue, intégrée aux pipelines, visible par les équipes métier. Commencez par les tests basiques, montez en puissance, et surtout : faites en sorte que les problèmes remontent avant que quelqu'un ne les découvre dans un dashboard.
