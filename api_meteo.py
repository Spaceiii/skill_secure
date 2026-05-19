import requests
import json

def get_weather(lat: float, lon: float) -> str:
    """
    Interroge l'API OpenMeteo pour obtenir les conditions actuelles et alertes potentielles.
    """
    if lat is None or lon is None:
        return json.dumps({"error": "Latitude et longitude requises pour la météo."})
        
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,windspeed_10m,precipitation&forecast_days=1"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        current = data.get("current_weather", {})
        hourly = data.get("hourly", {})
        
        # Analyser rapidement les précipitations et vents pour détecter des alertes
        wind_speeds = hourly.get("windspeed_10m", [])
        precipitations = hourly.get("precipitation", [])
        
        max_wind = max(wind_speeds) if wind_speeds else 0
        total_precip = sum(precipitations) if precipitations else 0
        
        alerts = []
        if max_wind > 60:
            alerts.append(f"Vents forts prévus ({max_wind} km/h)")
        if total_precip > 20:
            alerts.append(f"Fortes précipitations prévues ({total_precip} mm)")
            
        result = {
            "current_temperature_c": current.get("temperature"),
            "current_windspeed_kmh": current.get("windspeed"),
            "alerts": alerts,
            "forecast_24h_max_wind": max_wind,
            "forecast_24h_total_precip_mm": round(total_precip, 2)
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": f"Erreur lors de la requête OpenMeteo : {str(e)}"})

if __name__ == "__main__":
    # Test Paris
    print(get_weather(48.8584, 2.2945))
