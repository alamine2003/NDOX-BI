"""Capteur Teew de secours — filet de securite pour la demo (Partie D.2).

Envoie de vraies requetes POST /readings vers le backend, avec le
meme format JSON que le firmware ESP32 reel, pour que le dashboard
reagisse en direct meme si la simulation Wokwi ne cooperepas.

Usage:
    python mock_sensor.py                       # cible localhost:8000
    python mock_sensor.py --url https://xxx.ngrok-free.dev
"""
import argparse
import random
import time
from datetime import datetime, timezone

import requests

POINT_ID = "P07"
DEVICE_ID = "TEEW-07-SIM"  # suffixe SIM : on ne pretend pas etre le vrai capteur
SEUIL_JAUNE_CM = 10
SEUIL_ROUGE_CM = 30
CYCLE_S = 3


def level_for(water_cm):
    if water_cm < SEUIL_JAUNE_CM:
        return "VERT"
    if water_cm <= SEUIL_ROUGE_CM:
        return "JAUNE"
    return "ROUGE"


def next_water_cm(current):
    # Marche aleatoire douce, bornee, pour un mouvement credible a l'ecran.
    step = random.uniform(-2.5, 2.5)
    return max(0.0, min(45.0, current + step))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://localhost:8000/api/v1/readings")
    parser.add_argument("--start-water-cm", type=float, default=5.0)
    args = parser.parse_args()

    water_cm = args.start_water_cm
    print(f"[MOCK TEEW-07] Cible : {args.url}")
    print(f"[MOCK TEEW-07] Cycle : {CYCLE_S}s (Ctrl+C pour arreter)\n")

    while True:
        water_cm = next_water_cm(water_cm)
        temp_c = round(random.uniform(26.5, 29.5), 1)
        level = level_for(water_cm)
        ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        payload = {
            "device_id": DEVICE_ID,
            "point_id": POINT_ID,
            "ts": ts,
            "water_cm": round(water_cm, 1),
            "temp_c": temp_c,
            "battery_v": 3.92,
            "source": "sensor",
        }

        print(f"water_cm={water_cm:.1f} temp={temp_c:.1f} level={level}", end=" ")
        try:
            resp = requests.post(args.url, json=payload, timeout=5)
            if resp.ok:
                print(f"-> POST {resp.status_code} OK ({resp.json().get('flood_level')})")
            else:
                print(f"-> POST {resp.status_code} {resp.text[:100]}")
        except requests.RequestException as e:
            print(f"-> POST FAILED ({e})")

        time.sleep(CYCLE_S)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[MOCK TEEW-07] Arrete.")
