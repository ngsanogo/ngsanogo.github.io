---
title: "Gestion des erreurs dans les pipelines data"
slug: error-handling-pipelines
date: 2026-02-19
description: "Comment gérer les erreurs dans les pipelines data. Retry, modes de défaillance, alertes et dégradation gracieuse pour des pipelines résilients."
categories: ["data-engineering"]
tags: ["fiabilité", "gestion-erreurs", "pipelines", "bonnes-pratiques"]
draft: false
---

## Les pipelines cassent tout le temps

Rate limits d'API. Timeouts de base de données. Fichiers source manquants. Schémas qui changent sans prévenir. Mémoire insuffisante. Réseau instable.

La question n'est pas "est-ce que mon pipeline va échouer ?" mais "quand il échoue, que se passe-t-il ?"

## Les 3 niveaux de gestion d'erreur

### Niveau 1 — Retry automatique

La majorité des erreurs sont transitoires. Un retry suffit.

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, max=60))
def fetch_api_data(endpoint):
    response = requests.get(endpoint, timeout=30)
    response.raise_for_status()
    return response.json()
```

Règles :
- backoff exponentiel (pas de retry immédiat)
- nombre de tentatives limité
- timeout sur chaque appel

### Niveau 2 — Isolation des erreurs

Une erreur sur un enregistrement ne doit pas bloquer les milliers d'autres. Isoler les cas problématiques :

```python
success, errors = [], []
for record in records:
    try:
        result = transform(record)
        success.append(result)
    except ValidationError as e:
        errors.append({"record": record, "error": str(e)})

load(success)
quarantine(errors)
```

Les enregistrements en erreur sont mis en quarantaine pour analyse, pas perdus.

### Niveau 3 — Dégradation gracieuse

Quand une source est indisponible, le pipeline peut parfois continuer avec les données disponibles plutôt que de tout arrêter.

Exemple : un pipeline qui enrichit des commandes avec des données météo. Si l'API météo est down, les commandes sont quand même chargées — la colonne météo sera `NULL` et complétée au prochain run.

## Alertes : le minimum vital

Un pipeline qui échoue silencieusement est pire qu'un pipeline qui n'existe pas.

À alerter systématiquement :
- échec après tous les retries
- volume anormalement bas (possible perte de données)
- durée anormalement longue (possible blocage)
- taux d'erreur au-dessus du seuil

L'alerte doit contenir : quel pipeline, quelle étape, quel message d'erreur, un lien vers les logs.

## Circuit breaker

Quand une source externe échoue systématiquement, ne pas continuer à la marteler. Après N échecs consécutifs, couper l'appel et alerter. Tester périodiquement si la source est revenue.

## En résumé

| Stratégie | Quand l'utiliser |
|---|---|
| Retry + backoff | Erreurs réseau, API, timeouts |
| Quarantaine | Enregistrements invalides |
| Dégradation gracieuse | Sources non critiques indisponibles |
| Circuit breaker | Sources systématiquement en erreur |
| Alertes | Toujours |

Un pipeline fiable n'est pas un pipeline qui ne casse jamais. C'est un pipeline qui gère ses erreurs proprement et prévient quand quelque chose ne va pas.

---

**Vous avez un projet data similaire ? Parlons-en → [isdataconsulting.com](https://isdataconsulting.com)**
