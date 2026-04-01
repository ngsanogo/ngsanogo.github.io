---
title: "Le Zen du data engineering"
slug: zen-of-data-engineering
date: 2026-02-02
description: "Les principes qui séparent un pipeline fragile d'un pipeline fiable. Inspiré du Zen of Python : lisibilité, explicité, simplicité, pragmatisme."
categories: ["fundamentals"]
tags: ["bonnes-pratiques", "data-engineering", "principes", "qualité-code", "zen-of-python"]
keywords: []
image: "/images/og-default.svg"
draft: false
---

## Pourquoi cet article ?

J’ai passé deux jours à traquer une duplication silencieuse en production. Le pipeline tournait, les logs étaient verts, les chiffres étaient faux. Quand j’ai fini par trouver la cause — une absence de contrôle d’unicité à l’insertion — je me suis demandé combien de mes pipelines avaient le même défaut. C’est ce genre de moment qui m’a poussé à formaliser les principes que j’applique maintenant systématiquement. Ils sont largement inspirés du Zen of Python.

## Explicit is better than implicit

Chaque pipeline doit rendre visible :

- **Ce qu'il consomme** : quelles sources, quels schémas attendus
- **Ce qu'il produit** : quelles tables, quels fichiers
- **Ses hypothèses** : partitions attendues, volumes normaux, format des dates

Un pipeline dont on comprend le comportement en lisant le code, sans lancer de test ni consulter les logs, est un pipeline bien écrit.

Pas de convention cachée. Pas de variable d'environnement non documentée. Pas de dépendance implicite entre DAGs.

## Readability counts

Le code data le plus courant n'est pas du Python sophistiqué — c'est du SQL de transformation et du Python de plomberie. Les deux doivent être lisibles.

```sql
-- Lisible
WITH daily_orders AS (
    SELECT order_date, customer_id, SUM(amount) AS total
    FROM orders
    WHERE order_date = :execution_date
    GROUP BY order_date, customer_id
)
SELECT * FROM daily_orders WHERE total > 0

-- Illisible
SELECT * FROM (SELECT order_date,customer_id,SUM(amount) t FROM orders WHERE order_date=:d GROUP BY 1,2) x WHERE t>0
```

Les deux requêtes font la même chose. La première se débugue en 2 minutes. La seconde en 20.

Lisibilité > concision. Toujours.

## Errors should never pass silently

Un pipeline silencieux est un pipeline dangereux. Toujours préférer un crash bruyant à une exécution bancale.

- Vérifier les schémas en entrée avant de transformer
- Poser des assertions sur les volumes (pas de table vide sans alerte)
- Remonter les erreurs clairement, avec contexte

```python
if df.empty:
    raise ValueError(f"Aucune donnée reçue pour {execution_date}")

if df["order_id"].duplicated().any():
    raise ValueError(f"{df['order_id'].duplicated().sum()} doublons détectés")
```

Un pipeline qui échoue avec un message clair se répare en minutes. Un pipeline qui corrompt des données silencieusement se répare en semaines.

## Simple is better than complex

Le piège classique : abstraire trop tôt.

```python
# Trop abstrait
pipeline = PipelineFactory.create(
    strategy=IncrementalMergeStrategy(),
    validator=SchemaValidator(strict=True),
    sink=WarehouseSink(mode="upsert")
)

# Clair
df = read_source("orders", date=execution_date)
df = clean_orders(df)
df = compute_metrics(df)
write_to_warehouse(df, table="mart_orders", mode="overwrite")
```

Le code data n'a pas besoin de design patterns sophistiqués. Il a besoin d'être lisible par quelqu'un qui le découvre pour la première fois.

Si l'implémentation est difficile à expliquer, c'est une mauvaise idée. Si elle est facile à expliquer, c'est probablement la bonne.

## Practicality beats purity

L'architecture parfaite n'existe pas. Le pipeline parfait non plus. Ce qui existe, c'est le pipeline qui tourne, qui est fiable et que l'équipe sait maintenir.

- Pas besoin de streaming si le batch suffit
- Pas besoin de microservices si un script fait le travail
- Pas besoin de Kubernetes si Docker Compose convient

Le pragmatisme bat la pureté architecturale. Livrer un pipeline fonctionnel en 2 jours vaut mieux qu'un pipeline parfait en 2 mois.

## Now is better than never

Mieux vaut un pipeline imparfait en production qu'un pipeline parfait dans la tête.

- Livrer un premier flux simple, mesurer, itérer
- Poser les tests de base maintenant, pas "quand on aura le temps"
- Documenter les décisions au moment où on les prend

La dette technique s'accumule quand on repousse. Le monitoring, les tests, la documentation : c'est maintenant ou jamais.

## Idempotent par défaut

Un pipeline idempotent produit le même résultat qu'on le lance 1 fois ou 5 fois. C'est la propriété la plus importante en data engineering.

- Utiliser `MERGE` (PostgreSQL ≥ 15) ou `DELETE + INSERT` par partition au lieu d'`INSERT INTO` brut
- Partitionner par date et écraser la partition à chaque run
- Ne jamais dépendre de l'état du run précédent

Si un pipeline n'est pas idempotent, chaque incident nécessite une intervention manuelle. Ce n'est pas tenable.

## Tester ce qui compte

Tout tester est irréaliste. Tester ce qui casse le plus :

- **Schéma** : les colonnes attendues existent-elles ?
- **Volume** : le nombre de lignes est-il cohérent ?
- **Unicité** : les clés primaires sont-elles uniques ?
- **Fraîcheur** : la dernière partition date-t-elle de moins de 24h ?

Ces 4 tests couvrent 80 % des incidents data.

## Résumé

| Principe (Zen of Python)          | Application data                                  |
| --------------------------------- | ------------------------------------------------- |
| Explicit is better than implicit  | Entrées/sorties/hypothèses visibles               |
| Readability counts                | SQL formaté, nommage clair, pas de `GROUP BY 1,2` |
| Errors should never pass silently | Assertions, checks de schéma, alertes             |
| Simple is better than complex     | Pas d'abstraction prématurée                      |
| Practicality beats purity         | Livrer, itérer, ne pas sur-architecturer          |
| Now is better than never          | Tests, monitoring et docs dès le jour 1           |

Le code data n'a pas besoin d'être élégant. Il a besoin d'être fiable, lisible, et réparable.
