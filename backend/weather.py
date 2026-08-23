"""Client Open-Meteo avec cache local — Partie B.8.

Si le WiFi tombe pendant le pitch, la demo doit survivre : chaque
appel reussi est mis en cache sur disque, et un echec retombe sur le
dernier cache connu pour ce point (ou 0 mm si aucun cache n'existe).
"""
import json
import os

import requests

CACHE_PATH = os.path.join(os.path.dirname(__file__), "data", "weather_cache.json")
TIMEOUT_S = 3


def _load_cache():
    if not os.path.exists(CACHE_PATH):
        return {}
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def pluie_24h_mm(lat, lng, point_id):
    """Cumul de precipitations sur les dernieres 24h pour (lat, lng)."""
    cache = _load_cache()
    key = point_id

    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lng,
                "hourly": "precipitation",
                "forecast_days": 3,
            },
            timeout=TIMEOUT_S,
        )
        resp.raise_for_status()
        data = resp.json()
        hourly_precip = data.get("hourly", {}).get("precipitation", [])
        total = round(sum(hourly_precip[-24:]), 1) if hourly_precip else 0.0

        cache[key] = {"pluie_24h_mm": total}
        _save_cache(cache)
        return total
    except (requests.RequestException, ValueError, KeyError):
        cached = cache.get(key)
        return cached["pluie_24h_mm"] if cached else 0.0
