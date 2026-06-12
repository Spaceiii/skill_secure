---
name: carburant_moins_cher
description: Outil pour trouver le carburant le moins cher à proximité d'une adresse. Utilise le géocodage BAN, puis l'API officielle des prix des carburants pour comparer les stations-service proches et renvoyer un JSON clair, compact et strictement exploitable. Mots-clés: carburant, essence, diesel, gazole, SP95, SP98, E10, E85, GPLc, station-service, adresse, proximité, moins cher, JSON.
allowed-tools:
  - run_command
parameters:
  address:
    type: string
    description: "Adresse à géocoder avant la recherche."
    required: true
  fuel:
    type: string
    description: "Carburant ciblé: gazole, sp95, sp98, e10, e85, gplc, all. Par défaut: all."
  radius:
    type: number
    description: "Rayon de recherche en mètres. Par défaut: 5000."
  limit:
    type: number
    description: "Nombre maximal d'offres à retourner. Par défaut: 5."
---

# Instructions

Vous devez exécuter `emergency_data.py fuel` pour obtenir les stations-service et les prix autour de l'adresse fournie.

Règles:
- Géocoder d'abord l'adresse avec BAN.
- Rechercher les stations les plus proches dans le dataset officiel `prix-des-carburants-en-france-flux-instantane-v2`.
- Classer les offres par prix croissant, puis par distance croissante.
- Si `fuel` vaut `all`, retourner la meilleure offre toutes catégories confondues.
- Si `fuel` est précisé, ne garder que ce carburant.
- Renvoyer uniquement du JSON valide, sans texte autour.
- Utiliser `ensure_ascii=false` et des prix arrondis à 3 décimales.
- Si rien n'est trouvé, renvoyer un JSON d'erreur clair.

Schéma de sortie minimal attendu:
```json
{
  "query": {
    "address": "...",
    "fuel": "all",
    "radius_m": 5000,
    "limit": 5
  },
  "location": {
    "label": "...",
    "latitude": 0,
    "longitude": 0
  },
  "cheapest": {
    "station": "...",
    "fuel": "E85",
    "price_eur_l": 0.759,
    "distance_m": 1234
  },
  "offers": []
}
```
