---
title: "Docker pour les data engineers : lancer ses pipelines partout"
slug: docker-for-data-engineers
date: 2024-12-02
description: "Docker expliqué pour les data engineers : ce que c'est, pourquoi l'utiliser, et comment s'en servir pour des pipelines reproductibles."
categories: ["tools"]
tags: ["docker", "conteneurs", "data-engineering"]
draft: false
---

## Le problème que Docker résout

"Ça marche sur ma machine." Cette phrase résume le problème. L'environnement de dev, le serveur de staging et la prod ont des versions différentes de Python, des dépendances qui conflictent, des configs qui divergent.

Docker met l'application entière (code, dépendances, config) dans un conteneur qui tourne à l'identique partout.

## Les concepts clés

### Image

Une image est un snapshot figé de tout ce qu'il faut pour exécuter une application. Code, librairies, système d'exploitation minimal.

### Conteneur

Un conteneur est une instance vivante d'une image. Il tourne de manière isolée, avec ses propres fichiers et processus.

### Dockerfile

La recette qui décrit comment construire une image :

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "pipeline.py"]
```

### Docker Compose

Quand un pipeline a besoin de plusieurs services (base de données, queue, API), Compose les orchestre ensemble :

```yaml
services:
  pipeline:
    build: .
    depends_on:
      - postgres
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: data
```

## Pourquoi c'est utile en data engineering

### Reproductibilité

Le même conteneur tourne en dev, en CI et en prod. Fini les bugs liés à l'environnement.

### Isolation

Chaque pipeline a ses propres dépendances. Pas de conflit entre la version de pandas du pipeline A et celle du pipeline B.

### Déploiement simple

Un `docker pull` + `docker run` et le pipeline tourne. Pas d'installation, pas de configuration manuelle.

### Tests locaux

Besoin d'une base PostgreSQL pour tester ? `docker run postgres:16`. Besoin d'un MinIO local ? `docker run minio/minio`. En quelques secondes, l'environnement de test est prêt.

## Bonnes pratiques

**Images légères.** Utiliser des images `slim` ou `alpine`. Une image de 2 Go pour un script Python de 50 lignes, c'est un signal d'alarme.

**Multi-stage builds.** Séparer la phase de build (compilation, installation) de l'image finale pour réduire la taille.

**Ne pas stocker de données dans les conteneurs.** Utiliser des volumes pour la persistance.

**Un seul process par conteneur.** Ne pas mettre le pipeline, la base et le scheduler dans le même conteneur.

## Quand ne pas utiliser Docker

Pour des scripts ponctuels en local qui n'ont pas vocation à tourner ailleurs. Pour du prototypage rapide en notebook. L'overhead de Docker n'en vaut pas la peine si le pipeline n'a pas besoin de reproductibilité.

## En résumé

Docker est un outil indispensable pour les data engineers qui travaillent en équipe ou qui déploient en production. La courbe d'apprentissage est courte, le gain en reproductibilité est immédiat. Commencez par conteneuriser un pipeline existant, puis étendez avec Compose quand les besoins grandissent.

---

**Vous avez un projet data similaire ? Parlons-en → [isdataconsulting.com](https://isdataconsulting.com)**
