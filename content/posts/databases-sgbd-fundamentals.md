---
title: "Bases de données : les fondamentaux pour un data engineer"
slug: databases-sgbd-fundamentals
date: 2024-11-26
description: "Comprendre les bases de données (SGBD) : ce qu'elles sont, comment elles fonctionnent, et pourquoi chaque data engineer doit les maîtriser."
categories: ["fundamentals"]
tags: ["bases-de-données", "fondamentaux", "data-engineering"]
keywords: []
series: ""
image: "/images/og-default.svg"
draft: false
---

## C'est quoi une base de données

Une base de données (SGBD — Système de Gestion de Base de Données) est du stockage de données organisé. Un système de fichiers sophistiqué qui permet de trouver, modifier et organiser des millions d'enregistrements instantanément.

Sans bases de données, les entreprises ne peuvent pas fonctionner.

## Les deux grandes familles

### Relationnel (SQL)

Tables avec lignes et colonnes. Relations entre les tables. Un schéma prédéfini.

Exemples : PostgreSQL, MySQL, SQL Server, Oracle.

C'est le choix par défaut pour les données structurées. Quand les données ont un schéma clair et des relations entre elles, le relationnel est le bon choix.

### Non-relationnel (NoSQL)

Pas de schéma imposé. Formats flexibles : documents JSON, clé-valeur, graphes, colonnes larges.

Exemples : MongoDB (documents), Redis (clé-valeur), Neo4j (graphes), Cassandra (colonnes).

Utile quand : le schéma change souvent, les volumes sont massifs, ou la structure ne rentre pas dans des tables.

## ACID : les garanties d'une base relationnelle

- **Atomicity** : une transaction passe entièrement ou pas du tout
- **Consistency** : les données restent valides après chaque opération
- **Isolation** : les transactions concurrentes ne se gênent pas
- **Durability** : les données validées survivent à un crash

Ces garanties sont critiques en data engineering. Quand un pipeline charge des données, on veut que le chargement soit complet ou annulé — jamais à moitié.

## Ce qui compte pour un data engineer

### Index

Un index accélère les requêtes de lecture au prix d'un coût en écriture et stockage. Sans index sur une colonne filtrée, la base scanne toute la table.

Règle : indexer les colonnes utilisées dans les `WHERE`, `JOIN` et `ORDER BY` des requêtes fréquentes.

### Transactions

Quand un pipeline charge des données dans plusieurs tables, les transactions garantissent la cohérence. Si une étape échoue, tout est annulé.

### Connexions

Chaque requête utilise une connexion. Les pipelines qui ouvrent trop de connexions peuvent saturer la base. Utiliser un pool de connexions.

### Schémas

Organiser les tables par usage : `raw` pour les données brutes, `staging` pour les transformations intermédiaires, `marts` pour les données exploitables.

## Relationnel vs non-relationnel : quand choisir quoi

| Critère | Relationnel | NoSQL |
|---|---|---|
| Données structurées | Oui | Non nécessaire |
| Relations complexes | Oui | Limité |
| Schéma flexible | Non | Oui |
| Transactions ACID | Natif | Partiel |
| Volume massif | Limité (scaling vertical) | Conçu pour (scaling horizontal) |

Pour 90 % des projets data, commencez par du relationnel. Ajoutez du NoSQL quand un besoin spécifique le justifie.

## En résumé

Les bases de données sont le socle de tout système data. Maîtriser les fondamentaux — relations, index, transactions, schémas — est indispensable avant de travailler sur des pipelines, des warehouses ou de l'orchestration.

---

**Vous avez un projet data similaire ? Parlons-en → [isdataconsulting.com](https://isdataconsulting.com)**
