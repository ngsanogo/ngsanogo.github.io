---
title: "Qualité des données en santé : pourquoi c'est plus difficile qu'ailleurs"
slug: data-quality-healthcare-why-harder
date: 2026-03-02
description: "La qualité des données en santé est un défi unique : systèmes fragmentés, réglementation stricte, risque clinique. Un cadre pratique pour la fiabiliser."
categories: ["data-quality"]
tags: ["santé", "qualité-données", "gouvernance", "pipelines"]
keywords: []
image: "/images/og-default.svg"
format: "article"
draft: false
---

## Pourquoi cet article ?

Pendant mes quatre ans à l’AP-HP puis à l’Institut Jérôme Lejeune, j’ai appris que la qualité des données en santé est un problème à part. Un identifiant patient mal rattaché ne se corrige pas comme une erreur de montant. Les systèmes sont fragmentés, la réglementation interdit l’improvisation, et la tolérance à l’erreur est proche de zéro sur certains flux. Cet article pose le cadre que j’applique depuis, et que j’aurais aimé trouver documenté quand j’ai commencé.

## Ce qui rend la santé différente

### 1. Systèmes fragmentés

Les données vivent dans des dizaines de systèmes : DPI (dossier patient informatisé), LIMS (labo), imagerie, pharmacie, RH. Chacun a son propre schéma, ses propres identifiants, ses propres conventions.

Résultat : des doublons patients, des identifiants qui ne matchent pas, des données incomplètes à chaque interface.

### 2. Réglementation stricte

RGPD, hébergement HDS, consentement patient, traçabilité des accès. Chaque manipulation de données doit être justifiable et auditable. On ne peut pas simplement "corriger" une donnée sans trace.

### 3. Risque clinique

Un montant de facture erroné se corrige. Un résultat de labo mal rattaché à un patient peut avoir des conséquences graves. La tolérance à l'erreur est quasi nulle sur certains flux.

## Cadre pratique

### Classifier les flux par criticité

Tous les flux data n'ont pas le même niveau de risque. Distinguer :
- **Critique** : données patients, résultats cliniques, prescriptions
- **Important** : données de recherche, échantillons biologiques
- **Standard** : données RH, finances, reporting opérationnel

La rigueur des contrôles qualité doit suivre cette classification.

### Contrats de données à chaque interface

Entre chaque système source et la plateforme data, un contrat explicite :
- schéma attendu
- règles de validation
- format d'identifiant patient
- fréquence de livraison

Toute déviation déclenche une alerte, pas un chargement silencieux.

### Quarantaine avant publication

Les enregistrements qui échouent aux validations ne sont pas supprimés. Ils sont isolés en quarantaine avec un code raison. Les équipes métier peuvent les corriger à la source.

### Lignage et audit

Chaque donnée publiée doit pouvoir répondre à : d'où vient cette valeur, quand a-t-elle été chargée, par quel pipeline ?

Sans traçabilité, impossible de passer un audit ou de débugger un incident.

## Les erreurs classiques en santé

**Faire confiance au DPI.** Les systèmes sources hospitaliers ont souvent des problèmes de qualité. Ne jamais charger sans valider.

**Ignorer les doublons patients.** L'identité patient est le problème numéro un. Investir dans le matching et la déduplication dès le départ.

**Construire sans les métiers.** En santé, le data engineer seul ne peut pas définir les règles de qualité. Impliquer médecins, biologistes, pharmaciens dans la définition des contrôles.

## En résumé

La qualité des données en santé exige plus de rigueur, plus de traçabilité et plus de collaboration avec les métiers. Le cadre technique (tests, quarantaine, lignage) est le même qu'ailleurs — mais le niveau d'exigence et les conséquences d'un échec sont d'un autre ordre.
