import requests
import json
import urllib.parse

def geocode(address: str) -> str:
    """
    Interroge l'API Base Adresse Nationale (BAN) pour obtenir les coordonnées d'une adresse.
    """
    if not address:
        return json.dumps({"error": "L'adresse est requise pour le géocodage."})
        
    url = f"https://api-adresse.data.gouv.fr/search/?q={urllib.parse.quote(address)}&limit=1"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get("features") and len(data["features"]) > 0:
            feature = data["features"][0]
            geometry = feature["geometry"]["coordinates"] # [lon, lat]
            properties = feature["properties"]
            
            result = {
                "longitude": geometry[0],
                "latitude": geometry[1],
                "label": properties.get("label"),
                "city": properties.get("city"),
                "postcode": properties.get("postcode"),
                "context": properties.get("context"),
                "score": properties.get("score")
            }
            return json.dumps(result, indent=2, ensure_ascii=False)
        else:
            return json.dumps({"error": f"Aucun résultat trouvé pour l'adresse : {address}"})
            
    except Exception as e:
        return json.dumps({"error": f"Erreur lors de la requête BAN : {str(e)}"})

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(geocode(sys.argv[1]))
    else:
        print(geocode("15 rue de la paix paris"))
