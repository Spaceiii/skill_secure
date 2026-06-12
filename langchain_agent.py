from __future__ import annotations

import os
from typing import Literal

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI
from pydantic import BaseModel, ConfigDict, Field, SecretStr, ValidationError

from api_ban import geocode as api_geocode
from api_osm import search_infrastructure as api_search_infra
from api_meteo import get_weather as api_weather
from api_carburant import search_cheapest_fuel as api_fuel


class AppSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    backend_llm: Literal["genai", "mistral"] = Field(default="genai", alias="BACKEND_LLM")
    google_api_key: str | None = Field(default=None, alias="GOOGLE_API_KEY")
    mistral_api_key: str | None = Field(default=None, alias="MISTRAL_API_KEY")
    model_name: str | None = Field(default=None, alias="LLM_MODEL")
    temperature: float = Field(default=0.2, alias="LLM_TEMPERATURE")


def load_settings() -> AppSettings:
    load_dotenv()
    settings = AppSettings.model_validate(os.environ)

    if settings.backend_llm == "genai" and not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY is required when BACKEND_LLM=genai.")

    if settings.backend_llm == "mistral" and not settings.mistral_api_key:
        raise ValueError("MISTRAL_API_KEY is required when BACKEND_LLM=mistral.")

    return settings


def build_chat_model(settings: AppSettings):
    if settings.backend_llm == "genai":
        return ChatGoogleGenerativeAI(
            model=settings.model_name or "gemini-2.5-flash",
            temperature=settings.temperature,
            google_api_key=settings.google_api_key,
        )

    return ChatMistralAI(
        model_name=settings.model_name or "mistral-large-latest",
        temperature=settings.temperature,
        api_key=SecretStr(settings.mistral_api_key or ""),
    )


@tool
def geocode(address: str) -> str:
    """Trouve les coordonnées géographiques (latitude et longitude) d'une adresse."""
    return api_geocode(address)


@tool
def get_weather(lat: float, lon: float) -> str:
    """Obtient les conditions météorologiques et alertes pour une position donnée (latitude et longitude)."""
    return api_weather(lat, lon)


@tool
def search_infrastructure(lat: float, lon: float, infra_type: str, radius: int = 1000) -> str:
    """
    Recherche des infrastructures critiques autour d'un point géographique.
    Les types supportés sont : 'hospital', 'water', 'road', 'building', 'store'.
    """
    return api_search_infra(lat, lon, infra_type, radius)


@tool
def search_fuel(address: str, fuel: str = "all", radius: int = 1000, limit: int = 5) -> str:
    """
    Recherche les stations-service les moins chères autour d'une adresse.
    Carburants supportés: 'gazole', 'sp95', 'sp98', 'e10', 'e85', 'gplc', 'all'.
    """
    return api_fuel(address, fuel=fuel, radius=radius, limit=limit)


def build_agent_executor(chat_model):
    tools = [geocode, get_weather, search_infrastructure, search_fuel]
    
    system_prompt = (
        "Tu es un assistant spécialisé dans les urgences territoriales et la survie. "
        "Tu as accès à quatre outils pour aider l'utilisateur :\n"
        "1. 'geocode' : Obtenir les coordonnées géographiques d'une adresse.\n"
        "2. 'get_weather' : Obtenir la météo et les alertes pour une zone (nécessite latitude et longitude).\n"
        "3. 'search_infrastructure' : Trouver des infrastructures critiques (hôpitaux, points d'eau, routes, bâtiments, magasins d'alimentation/pharmacies) via leurs coordonnées.\n"
        "4. 'search_fuel' : Trouver les stations-service les moins chères autour d'une adresse.\n\n"
        "RÈGLES IMPORTANTES :\n"
        "- Si l'utilisateur demande une tâche qui ne fait pas partie de ces 4 fonctionnalités, dis-lui poliment que tu ne peux pas l'aider sur ce sujet.\n"
        "- Si l'utilisateur ne fournit pas assez de détails (par exemple le type d'infrastructure ou la localisation), pose-lui des questions pour obtenir ces informations avant d'appeler les outils.\n"
        "- Tu peux utiliser tes outils de manière combinée (ex: utiliser 'geocode' pour trouver les coordonnées d'une ville, puis 'search_infrastructure' avec ces coordonnées).\n"
        "Sois précis, clair et professionnel dans tes réponses."
    )
    
    return create_agent(model=chat_model, tools=tools, system_prompt=system_prompt)


def main() -> int:
    try:
        settings = load_settings()
    except ValidationError as exc:
        print(f"Erreur de configuration : {exc}")
        return 1
    except ValueError as exc:
        print(f"Erreur de configuration : {exc}")
        return 1

    agent_executor = build_agent_executor(build_chat_model(settings))
    chat_history = []
    
    print("=== ASSISTANT URGENCE TERRITORIALE ===")
    print("Je suis à votre disposition pour vos besoins en géolocalisation, météo, infrastructures et carburant.")
    print("Posez-moi vos questions ou tapez 'quit' pour quitter.")
    
    while True:
        try:
            user_input = input("\nVous: ")
            if user_input.strip().lower() in ["quit", "exit", "q"]:
                print("Au revoir !")
                break
            
            if not user_input.strip():
                continue
                
            response = agent_executor.invoke({
                "messages": chat_history + [("user", user_input)]
            })
            
            output_content = response["messages"][-1].content
            if isinstance(output_content, dict) and "text" in output_content:
                output = output_content["text"]
            elif isinstance(output_content, list):
                output = "\n".join([str(b.get("text", b)) if isinstance(b, dict) else str(b) for b in output_content])
            else:
                output = str(output_content)
                
            print(f"\nAssistant: {output}")
            
            # Mise à jour de l'historique pour garder le contexte
            chat_history.append(("user", user_input))
            chat_history.append(("assistant", output_content))
            
        except KeyboardInterrupt:
            print("\nAu revoir !")
            break
        except Exception as e:
            print(f"\nErreur lors de l'exécution : {e}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())