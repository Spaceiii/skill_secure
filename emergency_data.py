import argparse
import sys
import json
from api_ban import geocode
from api_osm import search_infrastructure
from api_meteo import get_weather

def main():
    parser = argparse.ArgumentParser(description="Outil de collecte de données pour les urgences territoriales.")
    parser.add_argument("action", choices=["geocode", "infra", "weather"], help="Action à effectuer.")
    parser.add_argument("--address", type=str, help="Adresse à géocoder (requis pour 'geocode').")
    parser.add_argument("--lat", type=float, help="Latitude (requis pour 'infra' et 'weather').")
    parser.add_argument("--lon", type=float, help="Longitude (requis pour 'infra' et 'weather').")
    parser.add_argument("--type", type=str, choices=["hospital", "water", "road", "building"], help="Type d'infrastructure (requis pour 'infra').")
    parser.add_argument("--radius", type=int, default=1000, help="Rayon de recherche en mètres pour 'infra' (défaut: 1000).")
    
    args = parser.parse_args()
    
    try:
        if args.action == "geocode":
            if not args.address:
                print(json.dumps({"error": "Paramètre --address requis pour l'action geocode."}))
                sys.exit(1)
            print(geocode(args.address))
            
        elif args.action == "infra":
            if args.lat is None or args.lon is None or not args.type:
                print(json.dumps({"error": "Paramètres --lat, --lon et --type requis pour l'action infra."}))
                sys.exit(1)
            print(search_infrastructure(args.lat, args.lon, args.type, args.radius))
            
        elif args.action == "weather":
            if args.lat is None or args.lon is None:
                print(json.dumps({"error": "Paramètres --lat et --lon requis pour l'action weather."}))
                sys.exit(1)
            print(get_weather(args.lat, args.lon))
            
    except Exception as e:
        print(json.dumps({"error": f"Erreur inattendue : {str(e)}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
