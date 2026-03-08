---
title: "Apache Airflow : orchestrer ses pipelines data"
slug: apache-airflow-orchestration
date: 2024-12-03
description: "Comment Airflow planifie et supervise vos pipelines data. Les concepts clés, les pièges courants et les bonnes pratiques pour l'utiliser efficacement."
categories: ["tools"]
tags: ["airflow", "orchestration", "data-pipelines", "data-engineering"]
draft: false
---

## Ce que fait Airflow

Airflow planifie et supervise vos pipelines data. Vous lui dites : "lance ce pipeline tous les jours à 2h du matin, retry 3 fois en cas d'échec, alerte-moi si ça échoue toujours." Airflow gère le reste.

Ce n'est pas un outil de traitement de données. C'est un orchestrateur : il déclenche, enchaîne et surveille des tâches.

## Les concepts essentiels

### DAG (Directed Acyclic Graph)

Un DAG décrit un workflow : quelles tâches exécuter, dans quel ordre, avec quelles dépendances.

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

with DAG("pipeline_ventes", start_date=datetime(2024, 1, 1), schedule="@daily"):
    extract = PythonOperator(task_id="extract", python_callable=extract_data)
    transform = PythonOperator(task_id="transform", python_callable=transform_data)
    load = PythonOperator(task_id="load", python_callable=load_data)
    extract >> transform >> load
```

### Operators

Les opérateurs définissent ce qu'une tâche fait concrètement :
- `PythonOperator` : exécuter une fonction Python
- `BashOperator` : lancer une commande shell
- `SqlOperator` : exécuter une requête SQL

### Schedule

Airflow propose des presets (`@daily`, `@hourly`) ou des expressions cron pour contrôler la fréquence d'exécution.

## Les pièges courants

**Trop de logique dans les DAGs.** Le DAG doit orchestrer, pas transformer. Gardez la logique métier dans des modules Python séparés.

**Des DAGs monolithiques.** Un DAG de 50 tâches est ingérable. Découpez par domaine métier.

**Ignorer l'idempotence.** Si un task échoue et qu'on le relance, le résultat doit être identique. Utilisez des `MERGE` ou `INSERT OVERWRITE`, pas des `INSERT INTO`.

**Pas de monitoring.** Airflow fournit des alertes email, des SLA, et une UI de suivi. Utilisez-les.

## Quand utiliser Airflow

Airflow est le bon choix quand :
- vous avez des workflows avec dépendances entre tâches
- vous avez besoin de planification, retry et alertes
- vos pipelines tournent en batch (pas en streaming)

Pour du streaming temps réel, regardez Kafka ou Flink. Pour des workflows simples sans dépendances, un cron suffit.

## Structure recommandée

```text
dags/
  pipeline_ventes.py
  pipeline_clients.py
plugins/
  extractors/
  transformers/
  loaders/
```

Séparez l'orchestration (DAGs) de la logique métier (plugins/modules).

## En résumé

Airflow est l'outil standard d'orchestration data. Sa force : la planification, le monitoring et la gestion des dépendances. Sa faiblesse : la courbe d'apprentissage et la tentation d'y mettre trop de logique.

Gardez vos DAGs simples. Mettez la logique métier dans des modules Python séparés, testables indépendamment. Un DAG doit se lire comme une table des matières, pas comme un roman.

Si vous démarrez : un DAG, 3 tâches, un schedule quotidien. Itérez à partir de là.

---

**Vous avez un projet data similaire ? Parlons-en → [isdataconsulting.com](https://isdataconsulting.com)**
