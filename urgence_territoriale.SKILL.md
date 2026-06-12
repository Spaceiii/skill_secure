---
name: urgence_territoriale
description: Outil multi-fonctions pour les situations d'urgence. Permet de : 1) Géocoder une adresse (action "geocode", nécessite "address") pour obtenir ses coordonnées. 2) Trouver des infrastructures critiques comme les hôpitaux, points d'eau, bâtiments ou routes autour d'un point (action "infra", nécessite "lat", "lon", "type", et optionnellement "radius"). 3) Obtenir les conditions météorologiques et alertes (action "weather", nécessite "lat", "lon"). 4) Rechercher les stations-service les moins chères (action "fuel", nécessite "address", et optionnellement "fuel", "limit", "radius"). Si une adresse est donnée, commencez toujours par l'action "geocode" pour obtenir les coordonnées géographiques (sauf pour "fuel" qui accepte une adresse directement), puis utilisez ces coordonnées pour les actions "infra" ou "weather".
allowed-tools:
  - bash
parameters:
  action:
    type: string
    description: "L'action à effectuer. Choix possibles : 'geocode' (trouver les coordonnées d'une adresse), 'infra' (chercher des infrastructures), 'weather' (obtenir la météo et les alertes), 'fuel' (rechercher des stations-service)."
    required: true
  address:
    type: string
    description: "L'adresse textuelle à géocoder ou utiliser (requis pour action='geocode' et action='fuel'). Ex: '15 rue de la Paix, Paris'."
  lat:
    type: number
    description: "Latitude (requise pour action='infra' et action='weather')."
  lon:
    type: number
    description: "Longitude (requise pour action='infra' et action='weather')."
  type:
    type: string
    description: "Type d'infrastructure à rechercher (requis uniquement si action='infra'). Choix : 'hospital' (hôpitaux, cliniques), 'water' (points d'eau, bornes incendie), 'road' (routes principales), 'building' (bâtiments), 'store' (magasins d'alimentation, pharmacies)."
  radius:
    type: number
    description: "Rayon de recherche en mètres (optionnel, utilisé pour action='infra' et action='fuel'). Par défaut: 1000."
  fuel:
    type: string
    description: "Type de carburant (optionnel, utilisé pour action='fuel'). Choix : 'gazole', 'sp95', 'sp98', 'e10', 'e85', 'gplc', 'all'. Par défaut: 'all'."
  limit:
    type: number
    description: "Nombre maximal d'offres à retourner (optionnel, utilisé pour action='fuel'). Par défaut: 5."
---

# Instructions

Vous allez exécuter le script Python `emergency_data.py` pour récupérer les informations demandées par l'utilisateur.
Si un environnement virtuel `.venv` est présent dans le répertoire, utilisez-le pour exécuter le script.

Construisez la commande CLI en fonction de l'action choisie. Les arguments non fournis ne doivent pas être inclus dans la ligne de commande ou doivent être gérés intelligemment.

Voici un exemple de construction de la commande :
- Pour geocode: `.venv/Scripts/python emergency_data.py geocode --address "{address}"` (Windows) ou `.venv/bin/python emergency_data.py ...` (Linux/Mac)
- Pour infra: `.venv/Scripts/python emergency_data.py infra --lat {lat} --lon {lon} --type {type} --radius {radius}`
- Pour weather: `.venv/Scripts/python emergency_data.py weather --lat {lat} --lon {lon}`
- Pour fuel: `.venv/Scripts/python emergency_data.py fuel --address "{address}" --fuel {fuel} --limit {limit} --radius {radius}`

<tool_call>
{"tool_name": "bash", "parameters": {"command": "python emergency_data.py {action} ${address:+--address \"$address\"} ${lat:+--lat $lat} ${lon:+--lon $lon} ${type:+--type $type} ${radius:+--radius $radius} ${fuel:+--fuel $fuel} ${limit:+--limit $limit}"}}
</tool_call>

*Note : La syntaxe bash ci-dessus avec `${var:+...}` permet d'ajouter dynamiquement les paramètres s'ils sont définis. Sinon, vous pouvez utiliser un bloc de code Python ou bash pour construire la commande exacte et l'exécuter via bash.*
