---
title: "Traitement incrémental : ne traiter que ce qui a changé"
slug: incremental-data-processing
date: 2026-02-22
description: "Comment ne traiter que les données nouvelles ou modifiées. Les patterns incrémentaux pour des pipelines efficaces qui arrêtent de tout retraiter."
categories: ["data-engineering"]
tags: ["traitement-incrémental", "performance", "pipelines", "bonnes-pratiques"]
keywords: []
series: ""
image: "/images/og-default.svg"
draft: false
---

## Le problème du full reload

Le full reload (tout retraiter à chaque run) fonctionne au début. Mais quand les tables grossissent :
- les runs durent des heures
- les coûts cloud explosent
- les fenêtres de maintenance rétrécissent

Le traitement incrémental résout ça : ne charger que les données nouvelles ou modifiées depuis le dernier run.

## Les 3 patterns

### 1. Timestamp-based

La source a une colonne `updated_at`. On filtre sur les enregistrements modifiés depuis le dernier run.

```sql
SELECT *
FROM source_orders
WHERE updated_at > '2024-01-14 23:59:59'
```

**Avantage** : simple et universel.
**Piège** : les suppressions ne sont pas détectées. Et si `updated_at` n'est pas indexé, le filtre est lent.

### 2. CDC (Change Data Capture)

La source envoie un flux de changements : inserts, updates, deletes. On consomme ce flux.

Outils : Debezium, AWS DMS, pg_logical.

**Avantage** : détecte aussi les suppressions. Temps réel possible.
**Piège** : plus complexe à mettre en place et à monitorer.

### 3. Snapshot + diff

On prend un snapshot complet régulièrement et on compare avec le précédent pour identifier les changements.

```sql
SELECT s.*
FROM source_snapshot s
LEFT JOIN previous_snapshot p ON s.order_id = p.order_id
WHERE p.order_id IS NULL
   OR s.hash_row != p.hash_row
```

**Avantage** : fonctionne même sans colonne `updated_at`.
**Piège** : coûteux en stockage et en compute sur les grosses tables.

## Comment choisir

| Critère | Timestamp | CDC | Snapshot + diff |
|---|---|---|---|
| Détecte les inserts | Oui | Oui | Oui |
| Détecte les updates | Oui (si updated_at fiable) | Oui | Oui |
| Détecte les deletes | Non | Oui | Oui |
| Complexité | Faible | Élevée | Moyenne |
| Latence | Batch | Temps réel possible | Batch |

**Règle** : commencer par timestamp-based. Passer à CDC quand les deletes comptent ou que la latence est critique.

## Incrémental + idempotence

Un pipeline incrémental doit rester idempotent. Le pattern recommandé :

1. Identifier la partition à traiter (ex: `order_date = '2024-01-15'`)
2. Écraser la partition complète (DELETE + INSERT)
3. Incrémenter le watermark

Jamais d'`INSERT INTO` brut sur un pipeline incrémental — c'est la recette des doublons.

## En résumé

Le traitement incrémental est indispensable dès que les volumes grandissent. La règle pragmatique :

- **Volumes < 10 Go** : le full reload reste viable, ne compliquez pas
- **Volumes > 10 Go et source avec `updated_at`** : timestamp-based, c'est le plus simple
- **Besoin de détecter les suppressions** : passez à CDC
- **Source sans colonnes de tracking** : snapshot + diff en dernier recours

Commencez par le pattern le plus simple qui fonctionne. N'introduisez de la complexité que quand le besoin est prouvé. Et dans tous les cas, gardez l'idempotence.

---

**Vous avez un projet data similaire ? Parlons-en → [isdataconsulting.com](https://isdataconsulting.com)**
