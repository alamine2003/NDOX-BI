"""Seed des 8 points de demonstration — Partie A.6.

static_params alimente le moteur (engine.py) : seuils, vulnerabilite,
reference de vidange, surface de la nappe d'eau stagnante, etc.
Ces valeurs sont calibrees pour la demo (voir simulate.py pour le
scenario keur_massar_j0_j10 qui pilote P07).
"""

POINTS_SEED = [
    {
        "id": "P01", "name": "Yeumbeul Nord — Rue 12",
        "lat": 14.7761, "lng": -17.3612, "population_exposee": 1400,
        "type_reel": "A",
        "static_params": {
            "seuil_cm": 30, "vulnerabilite": 0.3, "vidange_reference": 3.0,
            "surface_m2": 80, "presence_dechets": True, "monte_sans_pluie": False,
        },
        "initial": {"water_cm": 4.0, "temp_c": 27.0, "drain_rate_cmh": 3.0},
    },
    {
        "id": "P02", "name": "Keur Massar — Marché",
        "lat": 14.7789, "lng": -17.3204, "population_exposee": 2100,
        "type_reel": "B",
        "static_params": {
            "seuil_cm": 35, "vulnerabilite": 0.4, "vidange_reference": 2.5,
            "surface_m2": 120, "presence_dechets": True, "monte_sans_pluie": False,
        },
        "initial": {"water_cm": 6.0, "temp_c": 27.5, "drain_rate_cmh": 1.0},
    },
    {
        "id": "P03", "name": "Thiaroye — École Élém. 3",
        "lat": 14.7550, "lng": -17.3670, "population_exposee": 900,
        "type_reel": "B",
        "static_params": {
            "seuil_cm": 25, "vulnerabilite": 0.9, "vidange_reference": 2.0,
            "surface_m2": 60, "presence_dechets": False, "monte_sans_pluie": False,
        },
        "initial": {"water_cm": 3.0, "temp_c": 27.0, "drain_rate_cmh": 0.8},
    },
    {
        "id": "P04", "name": "Guédiawaye — Cité Sotiba",
        "lat": 14.7742, "lng": -17.3945, "population_exposee": 1800,
        "type_reel": "D",
        "static_params": {
            "seuil_cm": 20, "vulnerabilite": 0.5, "vidange_reference": 1.5,
            "surface_m2": 150, "presence_dechets": False, "monte_sans_pluie": True,
        },
        "initial": {"water_cm": 15.0, "temp_c": 27.0, "drain_rate_cmh": 0.3},
    },
    {
        "id": "P05", "name": "Pikine — Poste de santé",
        "lat": 14.7550, "lng": -17.3910, "population_exposee": 1100,
        "type_reel": "D",
        "static_params": {
            "seuil_cm": 20, "vulnerabilite": 0.9, "vidange_reference": 1.5,
            "surface_m2": 100, "presence_dechets": False, "monte_sans_pluie": True,
        },
        "initial": {"water_cm": 14.0, "temp_c": 27.0, "drain_rate_cmh": 0.3},
    },
    {
        "id": "P06", "name": "Malika — Bas-fond Est",
        "lat": 14.7930, "lng": -17.3350, "population_exposee": 600,
        "type_reel": "C",
        "static_params": {
            "seuil_cm": 40, "vulnerabilite": 0.3, "vidange_reference": 4.0,
            "surface_m2": 200, "presence_dechets": True, "monte_sans_pluie": False,
        },
        "initial": {"water_cm": 10.0, "temp_c": 27.5, "drain_rate_cmh": 0.1},
    },
    {
        "id": "P07", "name": "Keur Massar — Rue 12",
        "lat": 14.7801, "lng": -17.3180, "population_exposee": 1200,
        "type_reel": "A",
        "static_params": {
            "seuil_cm": 30, "vulnerabilite": 0.4, "vidange_reference": 3.0,
            "surface_m2": 90, "presence_dechets": True, "monte_sans_pluie": False,
        },
        "initial": {"water_cm": 3.0, "temp_c": 27.0, "drain_rate_cmh": 3.0},
    },
    {
        "id": "P08", "name": "Yeumbeul Sud — Canal",
        "lat": 14.7690, "lng": -17.3560, "population_exposee": 1500,
        "type_reel": "B",
        "static_params": {
            "seuil_cm": 35, "vulnerabilite": 0.35, "vidange_reference": 2.8,
            "surface_m2": 100, "presence_dechets": True, "monte_sans_pluie": False,
        },
        "initial": {"water_cm": 5.0, "temp_c": 27.0, "drain_rate_cmh": 1.0},
    },
]
