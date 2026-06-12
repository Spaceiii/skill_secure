# Urgence Territoriale

Ce projet est une boîte à outils conçue pour répondre aux besoins d'information d'urgence et de survie à l'échelle territoriale. Il permet de récupérer et d'agréger des données essentielles en temps réel pour assister la prise de décision.

## Fonctionnalités

Le système offre quatre services principaux :

- **Géolocalisation (Géocodage) :** Conversion d'une adresse textuelle en coordonnées géographiques (latitude et longitude).
- **Météorologie et Alertes :** Obtention des conditions météorologiques actuelles et des éventuelles alertes climatiques sur une zone définie.
- **Infrastructures Critiques :** Recherche ciblée autour d'un point d'intérêt pour identifier :
  - Hôpitaux et cliniques
  - Points d'eau (bornes incendie, accès à l'eau potable)
  - Axes routiers principaux
  - Magasins de première nécessité (alimentation, supermarchés, pharmacies)
- **Carburant :** Localisation des stations-service les plus proches d'une adresse et comparaison des prix en temps réel selon le type de carburant.

## Utilisation

Le projet propose plusieurs interfaces d'utilisation selon vos besoins technologiques :

### 1. Assistant Virtuel Interactif (`langchain_agent.py`)
Un chatbot intelligent propulsé par des modèles d'intelligence artificielle (Gemini ou Mistral). Il comprend les requêtes en langage naturel, pose des questions de clarification si nécessaire, et interroge automatiquement les différentes sources de données pour vous répondre.

**Prérequis :**
Assurez-vous d'avoir configuré vos clés d'API dans un fichier `.env` à la racine (`GOOGLE_API_KEY` ou `MISTRAL_API_KEY`).

**Lancement :**
```bash
python langchain_agent.py
```

### 2. Interface en Ligne de Commande (`emergency_data.py`)
Un outil CLI pour interroger directement les modules spécifiques de manière déterministe, sans passer par l'assistant virtuel.

**Exemples d'utilisation :**
```bash
# Géocoder une adresse
python emergency_data.py geocode --address "Paris"

# Trouver des magasins dans un rayon de 2000m
python emergency_data.py infra --lat 48.85 --lon 2.35 --type store --radius 2000

# Obtenir la météo locale
python emergency_data.py weather --lat 48.85 --lon 2.35

# Trouver les stations-service les moins chères (ex: Gazole)
python emergency_data.py fuel --address "Paris" --fuel gazole --limit 5
```

### 3. Intégration Claude Code (`urgence_territoriale.SKILL.md`)
Un fichier de définition de compétence (Skill) est fourni. Il permet à l'outil Claude Code d'exploiter nativement l'ensemble de ces outils de manière autonome depuis votre terminal.

## Données et Dépendances

Les données sont récupérées de manière dynamique auprès d'API publiques fiables (OpenStreetMap/Overpass, Base Adresse Nationale, données du gouvernement français, etc.).

L'assistant IA repose sur l'écosystème LangChain et nécessite les paquets Python documentés, notamment `langchain`, `langchain-google-genai`, `langchain-mistralai`, et `requests`.
