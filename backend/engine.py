"""Moteur d'indices NDOX BI — Partie B.4 a B.7 du cahier des charges.

Chaque fonction est volontairement simple et explicable ligne par ligne
(pas de boite noire) pour pouvoir etre presentee au jury.
"""

SEUIL_EMERGENCE = 105.0  # degres-jours cumules pour qu'un adulte emerge
T_BASE = 16.0            # seuil sous lequel la larve ne se developpe pas

FLOOD_VERT_MAX = 0.35
FLOOD_JAUNE_MAX = 0.65

PALU_VERT_MAX = 0.30
PALU_JAUNE_MAX = 0.60

QUORUM = 3
FENETRE_H = 6
ANTI_REBOND_MIN = 15


def indice_inondation(water_cm, seuil_cm, pluie_24h_mm, vitesse_montee_cmh, vulnerabilite):
    a = min(water_cm / seuil_cm, 1.0)
    b = min(pluie_24h_mm / 30.0, 1.0)
    c = min(vitesse_montee_cmh / 10.0, 1.0)
    d = vulnerabilite  # 0..1 : ecole, poste de sante, densite
    return round(0.4 * a + 0.3 * b + 0.2 * c + 0.1 * d, 2)


def flood_level_from_index(indice):
    if indice < FLOOD_VERT_MAX:
        return "vert"
    if indice <= FLOOD_JAUNE_MAX:
        return "jaune"
    return "rouge"


def maturation(historique):
    # historique = [(jour, temp_c), ...] pour les jours ou l'eau etait presente
    return sum(max(t - T_BASE, 0) for _, t in historique)


def jours_avant_emergence(dj_cumules, temp_moy):
    reste = SEUIL_EMERGENCE - dj_cumules
    if reste <= 0:
        return 0
    return round(reste / max(temp_moy - T_BASE, 1), 1)


def indice_palu(stagnation_days, dj_cumules, surface_m2, presence_dechets):
    if stagnation_days < 1:
        return 0.0
    p = min(dj_cumules / SEUIL_EMERGENCE, 1.0) * 0.60
    p += min(surface_m2 / 200.0, 1.0) * 0.25
    p += 0.15 if presence_dechets else 0.0
    return round(min(p, 1.0), 2)


def malaria_level_from_index(indice):
    if indice < PALU_VERT_MAX:
        return "vert"
    if indice <= PALU_JAUNE_MAX:
        return "jaune"
    return "rouge"


def classifier(vitesse_vidange, vidange_reference, monte_sans_pluie, duree_jours):
    if monte_sans_pluie or duree_jours > 21:
        return "D"  # remontee de nappe
    if vitesse_vidange < 0.2:
        return "C"  # pas d'exutoire
    if vitesse_vidange < 0.5 * vidange_reference:
        return "B"  # obstruction
    return "A"  # ruissellement


def curage_utile(type_):
    return type_ in ("A", "B")


def certificat(before_cmh, after_cmh):
    gain = (after_cmh - before_cmh) / max(before_cmh, 0.1) * 100
    return {
        "before_cmh": before_cmh,
        "after_cmh": after_cmh,
        "gain_pct": round(gain),
        "verdict": "CONFORME" if gain >= 100 else "NON CONFORME",
    }
