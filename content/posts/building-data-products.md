---
title: "Data products : penser produit quand on est data engineer"
slug: building-data-products
date: 2026-01-31
description: "Un data engineer qui pense produit crée plus de valeur. Comment passer de la livraison technique à la résolution de vrais problèmes métier."
categories: ["product-data"]
tags: ["data-products", "product-thinking", "data-engineering", "stakeholder-management"]
keywords: []
image: "/images/og-default.svg"
draft: false
---

## Pourquoi cet article ?

J’ai livré un pipeline dont personne ne s’est servi. Trois jours de développement, une architecture propre, zéro utilisateur. Le problème n’était pas technique. Je n’avais pas posé la bonne question au départ. C’est ce raté qui m’a fait basculer vers une approche produit : commencer par le problème métier, pas par la donnée disponible. Cet article retrace ce changement de perspective.

## Qu’est-ce qu’un data product ?

Un data product est un livrable basé sur la donnée qui résout un problème précis pour un utilisateur défini. Ce n'est pas juste une table ou un dashboard.

Il y a 4 niveaux de maturité :
- **Niveau 1** : accès brut (tables exposées, exports)
- **Niveau 2** : données curées (tables propres, documentées, validées)
- **Niveau 3** : produits analytiques (dashboards self-service, métriques)
- **Niveau 4** : produits de décision (alertes, recommandations, automatisations)

La majorité des équipes restent au niveau 1-2. L'approche produit pousse vers le 3-4.

## Partir du problème, pas de la donnée

L'erreur classique : "On a des données de clics, construisons un dashboard de clickstream."

L'approche produit : "Le marketing ne peut pas mesurer l'efficacité de ses campagnes. De quoi ont-ils besoin pour y arriver ?"

Avant de coder, répondre à :
- **Qui** utilise ce produit ? (rôle, fréquence, niveau technique)
- **Quel problème** résout-il ? (en une phrase)
- **Comment mesurer** le succès ? (adoption, impact business)
- **Quelle fraîcheur** est nécessaire ? (temps réel, quotidien, hebdo)

## Un exemple concret

Contexte : une équipe commerciale demande "un dashboard des ventes".

**Approche pipeline** : extraction des transactions, agrégation par jour, dashboard Metabase. Livré en 3 jours, jamais consulté.

**Approche product** : on s'assoit avec les commerciaux. Le vrai besoin : savoir chaque matin quels comptes sont en baisse pour prioriser les appels. Le livrable : un email automatique avec les 10 comptes à risque, trié par enjeu financier. Livré en 5 jours, utilisé tous les matins.

La différence n'est pas technique. C'est la question de départ.

## Les 3 métriques de succès

1. **Adoption** : combien de personnes l'utilisent chaque semaine ?
2. **Engagement** : à quelle fréquence reviennent-ils ?
3. **Impact** : est-ce que ça change quelque chose ? (temps gagné, revenus, décisions améliorées)

Sans ces métriques définies avant le développement, on ne peut pas savoir si le produit fonctionne. Et un produit sans mesure de succès est un projet sans fin.

## Les anti-patterns

- **Le shelfware** : construit sans utilisateur défini, jamais adopté
- **Le dashboard de vanité** : joli mais personne ne prend de décision avec
- **La sur-ingénierie** : architecture parfaite, mais le problème métier a changé entretemps
- **Le data swamp** : tout centraliser sans réfléchir à qui consomme quoi

## Le cycle produit data

En pratique, un bon data product suit ce cycle :
1. Identifier un problème métier concret
2. Définir l'utilisateur et ses critères de succès
3. Livrer un MVP en 2-4 semaines (pas 6 mois)
4. Mesurer l'adoption
5. Itérer ou pivoter

Le MVP n'a pas besoin d'être beau. Il a besoin de prouver que le besoin existe. Si personne ne l'utilise après 2 semaines, le problème n'est pas technique — c'est le cadrage.

## Pourquoi ça change tout pour le data engineer

Le data engineer qui adopte cette approche ne monte pas seulement en compétence technique. Il devient l'interlocuteur qui comprend le métier, propose des solutions pragmatiques et mesure leur impact.

C'est la différence entre "j'ai livré un pipeline" et "j'ai résolu un problème business". La seconde phrase vaut plus, en entretien comme sur le terrain.
