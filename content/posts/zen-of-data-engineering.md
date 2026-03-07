---
title: "Écrire du code data qui dure"
slug: zen-of-data-engineering
date: 2026-02-02
description: "Les principes qui séparent un pipeline fragile d'un pipeline fiable. Lisibilité, idempotence, simplicité : l'essentiel pour du code data maintenable."
categories: ["fundamentals"]
tags: ["bonnes-pratiques", "data-engineering", "principes", "qualité-code"]
draft: false
---

## Le problème

La plupart des pipelines data ne cassent pas parce qu'ils sont mal codés. Ils cassent parce qu'ils sont mal pensés : trop complexes, trop couplés, trop implicites.

Le code data est lu bien plus souvent qu'il n'est écrit. Un pipeline tourne pendant des mois. Quand il casse à 3h du matin, ce n'est jamais son auteur qui le débugue.

Voici les principes qui font la différence entre un pipeline fragile et un pipeline fiable.

## Explicite plutôt qu'implicite

Chaque pipeline doit rendre visible :
- **Ce qu'il consomme** : quelles sources, quels schémas attendus
- **Ce qu'il produit** : quelles tables, quels fichiers
- **Ses hypothèses** : partitions attendues, volumes normaux, format des dates

Un pipeline dont on comprend le comportement en lisant le code, sans lancer de test ni regarder les logs, est un pipeline bien écrit.

## Idempotence par défaut

Un pipeline idempotent produit le même résultat qu'on le lance 1 fois ou 5 fois. C'est la propriété la plus importante en data engineering.

En pratique :
- Utiliser `INSERT OVERWRITE` ou `MERGE` au lieu de `INSERT INTO`
- Partitionner par date et écraser la partition à chaque run
- Ne jamais dépendre de l'état du run précédent

Si un pipeline n'est pas idempotent, chaque incident nécessite une intervention manuelle. Ce n'est pas tenable.

## Échouer fort et vite

Un pipeline silencieux est un pipeline dangereux. Toujours préférer un crash bruyant à une exécution bancale.

- Vérifier les schémas en entrée avant de transformer
- Poser des assertions sur les volumes (pas de table vide sans alerte)
- Remonter les erreurs clairement, avec contexte

Un pipeline qui échoue avec un message clair se répare en minutes. Un pipeline qui corrompt des données silencieusement se répare en semaines.

## Simple d'abord

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

## Tester ce qui compte

Tout tester est irréaliste dans un contexte data. Tester ce qui casse le plus :

- **Schéma** : les colonnes attendues existent-elles ?
- **Volume** : le nombre de lignes est-il cohérent ?
- **Unicité** : les clés primaires sont-elles uniques ?
- **Fraîcheur** : la dernière partition date-t-elle de moins de 24h ?

Ces 4 tests couvrent 80 % des incidents data.

## Documenter les décisions, pas le code

Les commentaires utiles expliquent le **pourquoi**, pas le **quoi**.

```sql
-- On exclut les commandes test (préfixe TEST_) car le système
-- de paiement les génère automatiquement en staging
WHERE order_id NOT LIKE 'TEST_%'
```

Documenter aussi les choix d'architecture : pourquoi batch et pas streaming, pourquoi cette granularité, pourquoi ce modèle de données.

## Résumé

| Principe | En pratique |
|---|---|
| Explicite > implicite | Rendre les entrées/sorties/hypothèses visibles |
| Idempotent par défaut | `OVERWRITE` / `MERGE`, pas d'état implicite |
| Échouer fort | Assertions, checks de schéma, alertes |
| Simple d'abord | Pas d'abstraction prématurée |
| Tester ce qui casse | Schéma, volume, unicité, fraîcheur |
| Documenter le pourquoi | Pas le quoi |

Le code data n'a pas besoin d'être élégant. Il a besoin d'être fiable, lisible, et réparable.

---

**Vous avez un projet data similaire ? Parlons-en → [isdataconsulting.com](https://isdataconsulting.com)**
