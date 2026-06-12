import argparse
import json
import math
from typing import Any, Dict, List, Optional

import requests

from api_ban import geocode

DATASET_URL = "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/records"
USER_AGENT = "SkillSecure-FuelSearch/1.0"

PRICE_FIELDS = {
    "gazole": "gazole_prix",
    "sp95": "sp95_prix",
    "sp98": "sp98_prix",
    "e10": "e10_prix",
    "e85": "e85_prix",
    "gplc": "gplc_prix",
}

PRICE_LABELS = {
    "gazole": "Gazole",
    "sp95": "SP95",
    "sp98": "SP98",
    "e10": "E10",
    "e85": "E85",
    "gplc": "GPLc",
}


def _safe_json_loads(value: Any) -> Optional[Dict[str, Any]]:
    if isinstance(value, dict):
        return value
    if not value:
        return None
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else None
    except Exception:
        return None


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_earth_m = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    return 2 * radius_earth_m * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _normalize_fuel(fuel: Optional[str]) -> str:
    if not fuel:
        return "all"
    fuel = fuel.strip().lower()
    return fuel if fuel in PRICE_FIELDS or fuel == "all" else ""


def _station_label(record: Dict[str, Any]) -> str:
    address = record.get("adresse") or "Adresse inconnue"
    city = record.get("ville") or "Ville inconnue"
    return f"{address}, {city}"


def _extract_offers(record: Dict[str, Any], target_lat: float, target_lon: float, fuel_filter: str) -> List[Dict[str, Any]]:
    geom = record.get("geom") or {}
    station_lat = geom.get("lat")
    station_lon = geom.get("lon")
    if station_lat is None or station_lon is None:
        return []

    station_lat = float(station_lat)
    station_lon = float(station_lon)
    distance_m = int(round(_haversine_m(target_lat, target_lon, station_lat, station_lon)))

    offers: List[Dict[str, Any]] = []
    for fuel_key, field_name in PRICE_FIELDS.items():
        if fuel_filter != "all" and fuel_filter != fuel_key:
            continue
        price = record.get(field_name)
        if price is None:
            continue
        offers.append(
            {
                "station_id": record.get("id"),
                "station": _station_label(record),
                "fuel": PRICE_LABELS[fuel_key],
                "price_eur_l": round(float(price), 3),
                "distance_m": distance_m,
                "latitude": round(station_lat, 6),
                "longitude": round(station_lon, 6),
                "cp": record.get("cp"),
                "city": record.get("ville"),
                "address": record.get("adresse"),
                "automate_24_24": record.get("horaires_automate_24_24"),
                "services": record.get("services_service") or [],
            }
        )
    return offers


def _fetch_candidates(lat: float, lon: float, fetch_limit: int) -> List[Dict[str, Any]]:
    params = {
        "limit": fetch_limit,
        "order_by": f"distance(geom,geom'POINT({lon} {lat})')",
    }
    response = requests.get(DATASET_URL, params=params, headers={"User-Agent": USER_AGENT}, timeout=30)
    response.raise_for_status()
    payload = response.json()
    return payload.get("results", [])


def search_cheapest_fuel(address: str, fuel: str = "all", radius: int = 5000, limit: int = 5) -> str:
    if not address:
        return json.dumps({"error": "L'adresse est requise."}, ensure_ascii=False, indent=2)

    geocode_result = _safe_json_loads(geocode(address))
    if not geocode_result or geocode_result.get("error"):
        return json.dumps(
            {
                "error": geocode_result.get("error") if geocode_result else "Impossible de géocoder l'adresse.",
                "query": {"address": address},
            },
            ensure_ascii=False,
            indent=2,
        )

    fuel_filter = _normalize_fuel(fuel)
    if not fuel_filter:
        return json.dumps(
            {
                "error": "Carburant invalide.",
                "supported_fuels": ["gazole", "sp95", "sp98", "e10", "e85", "gplc", "all"],
            },
            ensure_ascii=False,
            indent=2,
        )

    latitude = float(geocode_result["latitude"])
    longitude = float(geocode_result["longitude"])
    fetch_limit = max(50, min(200, limit * 10))

    try:
        candidates = _fetch_candidates(latitude, longitude, fetch_limit)
    except Exception as exc:
        return json.dumps(
            {
                "error": f"Erreur lors de la requête carburant: {exc}",
                "query": {"address": address, "fuel": fuel_filter, "radius_m": radius, "limit": limit},
            },
            ensure_ascii=False,
            indent=2,
        )

    offers: List[Dict[str, Any]] = []
    for record in candidates:
        offers.extend(_extract_offers(record, latitude, longitude, fuel_filter))

    offers.sort(key=lambda item: (item["price_eur_l"], item["distance_m"], item["station"]))
    within_radius = [offer for offer in offers if offer["distance_m"] <= radius]
    selected_offers = within_radius if within_radius else offers
    selected_offers = selected_offers[:limit]

    result: Dict[str, Any] = {
        "query": {
            "address": address,
            "fuel": fuel_filter,
            "radius_m": radius,
            "limit": limit,
        },
        "location": {
            "label": geocode_result.get("label"),
            "latitude": latitude,
            "longitude": longitude,
            "city": geocode_result.get("city"),
            "postcode": geocode_result.get("postcode"),
        },
        "count": {
            "candidates": len(candidates),
            "offers_found": len(offers),
            "offers_within_radius": len(within_radius),
            "returned": len(selected_offers),
        },
        "cheapest": selected_offers[0] if selected_offers else None,
        "offers": selected_offers,
        "source": {
            "dataset": "prix-des-carburants-en-france-flux-instantane-v2",
            "provider": "data.economie.gouv.fr",
            "records_api": DATASET_URL,
        },
    }

    if not within_radius and offers:
        result["warning"] = "Aucune station trouvée dans le rayon demandé; les offres retournées sont les plus proches disponibles."
    if not selected_offers:
        result["error"] = "Aucune offre carburant disponible pour cette adresse."

    return json.dumps(result, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Trouver le carburant le moins cher à proximité d'une adresse.")
    parser.add_argument("address", type=str, help="Adresse à géocoder.")
    parser.add_argument("--fuel", type=str, default="all", help="Carburant ciblé: gazole, sp95, sp98, e10, e85, gplc, all.")
    parser.add_argument("--radius", type=int, default=5000, help="Rayon de recherche en mètres.")
    parser.add_argument("--limit", type=int, default=5, help="Nombre maximal d'offres à retourner.")

    args = parser.parse_args()
    print(search_cheapest_fuel(args.address, fuel=args.fuel, radius=args.radius, limit=args.limit))


if __name__ == "__main__":
    main()
