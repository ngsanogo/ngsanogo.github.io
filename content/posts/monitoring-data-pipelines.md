---
title: "Monitoring des pipelines data en production"
slug: monitoring-data-pipelines
date: 2026-03-15
description: "Comment surveiller ses pipelines data efficacement. Les métriques essentielles, les alertes utiles et les patterns de monitoring qui marchent en production."
categories: ["data-engineering", "observability"]
tags: ["monitoring", "observabilité", "alerting", "production", "pipelines"]
draft: false
---

## Pourquoi monitorer

Un pipeline qui tourne ne veut pas dire un pipeline qui fonctionne. Les données peuvent arriver en retard, être incomplètes ou corrompues — et personne ne s'en aperçoit si le monitoring est absent.

Le monitoring data, c'est répondre à 3 questions en permanence :
1. **Est-ce que ça tourne ?** (orchestration)
2. **Est-ce que les données arrivent ?** (freshness)
3. **Est-ce que les données sont correctes ?** (qualité)

## Les 4 niveaux de monitoring

### Niveau 1 : Infrastructure

Le socle. CPU, mémoire, disque, réseau. Si le serveur est saturé, rien d'autre ne compte.

Outils : Prometheus + Grafana, CloudWatch, Datadog.

### Niveau 2 : Orchestration

Les runs de pipelines : succès, échec, durée, retries.

Airflow expose ces métriques nativement :
- `dag_run_duration`
- `task_instance_failures`
- `scheduler_heartbeat`

**Alerte minimale** : tout DAG en échec depuis plus de 2 runs consécutifs.

### Niveau 3 : Freshness

Les données sont-elles à jour ? On vérifie le timestamp du dernier enregistrement chargé.

```sql
SELECT MAX(loaded_at) AS last_load
FROM warehouse.orders
```

Si `last_load` date de plus de 2h alors que le pipeline tourne toutes les heures → alerte.

### Niveau 4 : Qualité

Les données sont-elles correctes ? C'est le niveau le plus précieux et le plus négligé.

Contrôles classiques :
- Volume : le nombre de lignes est-il dans la fourchette attendue ?
- Nulls : les colonnes obligatoires sont-elles remplies ?
- Unicité : pas de doublons sur les clés primaires ?
- Distribution : les valeurs sont-elles cohérentes ?

```sql
-- Contrôle de volume
SELECT COUNT(*) AS row_count
FROM warehouse.orders
WHERE order_date = CURRENT_DATE - INTERVAL '1 day'
HAVING COUNT(*) < 100 OR COUNT(*) > 10000
```

## Les métriques essentielles

| Métrique | Quoi | Seuil d'alerte |
|---|---|---|
| Pipeline success rate | % de runs réussis | < 95% sur 24h |
| Pipeline duration | Temps d'exécution | > 2× la moyenne |
| Data freshness | Âge du dernier chargement | > 2× la fréquence |
| Row count delta | Variation du volume | > ±50% vs veille |
| Null rate | % de nulls par colonne | > seuil métier |

## Alerting : moins c'est mieux

Le piège classique : trop d'alertes. L'équipe les ignore, une vraie panne passe inaperçue.

Règles :
- **Chaque alerte doit être actionnable**. Si personne ne sait quoi faire quand elle sonne, elle ne sert à rien.
- **Sévérité claire** : critique (action immédiate) vs warning (à traiter dans la journée).
- **Canaux séparés** : Slack pour les warnings, PagerDuty/appel pour les critiques.
- **Pas d'alerte sur les retries** : alerter seulement après l'échec final.

## Le dashboard minimum

Un seul dashboard pour commencer :

1. **Vue globale** : tous les DAGs, statut du dernier run (vert/rouge)
2. **Freshness** : dernière mise à jour par table critique
3. **Tendance** : durée des runs sur 7 jours (détecter les dérives)
4. **Incidents ouverts** : alertes actives non résolues

Pas besoin de 15 dashboards. Un seul, bien fait, que l'équipe consulte chaque matin.

## Les erreurs classiques

- **Monitorer uniquement l'orchestration** : le pipeline est vert mais les données sont fausses
- **Pas de baseline** : impossible de détecter une anomalie sans connaître le comportement normal
- **Alertes sur chaque tâche** : bruit insupportable, personne ne regarde
- **Pas de runbook** : l'alerte sonne, personne ne sait quoi faire

## En résumé

Le monitoring data, c'est 4 niveaux : infra, orchestration, freshness, qualité. Commencez par les alertes critiques, ajoutez progressivement. Un bon monitoring ne produit pas du bruit — il produit de la confiance.

---

**Vous avez un projet data similaire ? Parlons-en → [isdataconsulting.com](https://isdataconsulting.com)**
