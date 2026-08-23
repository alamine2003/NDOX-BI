"""Scenario simule "keur_massar_j0_j10" — Partie A.7 / B.12.

11 jours de donnees pre-generees pour P07 qui rejouent la timeline de
demo : crue (J0), decrue (J2), fenetre d'or paludisme (J4),
traitement (J6), retour au calme (J7-J10).

POST /simulate rejoue les jours 0..day dans l'ordre pour reconstruire
un etat coherent (stagnation, degres-jours cumules, etc.) plutot que
de sauter directement au jour demande.
"""

# day, pluie_24h_mm, water_cm, temp_c, treatment (larvicide applique ce jour-la)
KEUR_MASSAR_J0_J10 = [
    {"day": 0, "pluie_24h_mm": 55.0, "water_cm": 42.5, "temp_c": 29.4, "treatment": False},
    {"day": 1, "pluie_24h_mm": 5.0, "water_cm": 15.0, "temp_c": 28.0, "treatment": False},
    {"day": 2, "pluie_24h_mm": 0.0, "water_cm": 11.0, "temp_c": 28.2, "treatment": False},
    {"day": 3, "pluie_24h_mm": 0.0, "water_cm": 9.0, "temp_c": 29.0, "treatment": False},
    {"day": 4, "pluie_24h_mm": 0.0, "water_cm": 8.0, "temp_c": 29.4, "treatment": False},
    {"day": 5, "pluie_24h_mm": 0.0, "water_cm": 7.0, "temp_c": 29.0, "treatment": False},
    {"day": 6, "pluie_24h_mm": 0.0, "water_cm": 0.0, "temp_c": 28.5, "treatment": True},
    {"day": 7, "pluie_24h_mm": 0.0, "water_cm": 0.0, "temp_c": 28.0, "treatment": False},
    {"day": 8, "pluie_24h_mm": 0.0, "water_cm": 2.0, "temp_c": 27.5, "treatment": False},
    {"day": 9, "pluie_24h_mm": 0.0, "water_cm": 2.0, "temp_c": 27.5, "treatment": False},
    {"day": 10, "pluie_24h_mm": 0.0, "water_cm": 3.0, "temp_c": 27.0, "treatment": False},
]

SCENARIOS = {
    "keur_massar_j0_j10": {
        "point_id": "P07",
        "days": KEUR_MASSAR_J0_J10,
    }
}
