import requests
import json

def get_overpass_query(lat: float, lon: float, infra_type: str, radius: int = 1000) -> str:
    """Génère la requête Overpass QL selon le type d'infrastructure."""
    queries = {
        "hospital": f"""
            node(around:{radius},{lat},{lon})["amenity"="hospital"];
            way(around:{radius},{lat},{lon})["amenity"="hospital"];
            relation(around:{radius},{lat},{lon})["amenity"="hospital"];
            node(around:{radius},{lat},{lon})["amenity"="clinic"];
        """,
        "water": f"""
            node(around:{radius},{lat},{lon})["emergency"="fire_hydrant"];
            node(around:{radius},{lat},{lon})["amenity"="drinking_water"];
            node(around:{radius},{lat},{lon})["waterway"];
        """,
        "road": f"""
            way(around:{radius},{lat},{lon})["highway"~"^(motorway|trunk|primary|secondary|tertiary)$"];
        """,
        "building": f"""
            way(around:{radius},{lat},{lon})["building"];
        """,
        "store": f"""
            node(around:{radius},{lat},{lon})["shop"~"^(supermarket|convenience|bakery|butcher|pharmacy)$"];
            way(around:{radius},{lat},{lon})["shop"~"^(supermarket|convenience|bakery|butcher|pharmacy)$"];
            node(around:{radius},{lat},{lon})["amenity"="pharmacy"];
        """
    }
    
    query_body = queries.get(infra_type)
    if not query_body:
        return None
        
    return f"""
    [out:json][timeout:25];
    (
      {query_body}
    );
    out center;
    """

def search_infrastructure(lat: float, lon: float, infra_type: str, radius: int = 1000) -> str:
    """
    Interroge l'API Overpass pour trouver des infrastructures autour d'un point.
    """
    if lat is None or lon is None:
        return json.dumps({"error": "Latitude et longitude requises."})
        
    query = get_overpass_query(lat, lon, infra_type, radius)
    if not query:
         return json.dumps({"error": f"Type d'infrastructure inconnu: {infra_type}. Types supportés: hospital, water, road, building, store."})

    url = "https://overpass-api.de/api/interpreter"
    headers = {"User-Agent": "ClaudeCode-EmergencyBot/1.0"}
    try:
        response = requests.post(url, data={'data': query}, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        elements = data.get("elements", [])
        results = []
        for el in elements[:20]: # Limiter à 20 résultats pour ne pas surcharger la réponse du LLM
            tags = el.get("tags", {})
            name = tags.get("name", "Inconnu")
            el_type = tags.get("amenity") or tags.get("shop") or tags.get("highway") or tags.get("emergency") or tags.get("building") or "N/A"
            
            # Récupérer les coordonnées (pour les ways, on utilise out center pour avoir lat/lon)
            el_lat = el.get("lat") or el.get("center", {}).get("lat")
            el_lon = el.get("lon") or el.get("center", {}).get("lon")
            
            item = {
                "id": el.get("id"),
                "name": name,
                "type": el_type,
            }
            if el_lat and el_lon:
                item["lat"] = el_lat
                item["lon"] = el_lon
                
            results.append(item)
            
        return json.dumps({
            "count": len(elements),
            "returned": len(results),
            "results": results
        }, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": f"Erreur lors de la requête Overpass : {str(e)}"})

if __name__ == "__main__":
    # Test avec la Tour Eiffel
    print(search_infrastructure(48.8584, 2.2945, "hospital", 2000))
