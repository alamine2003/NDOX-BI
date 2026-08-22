"""Contenu de la borne vocale — squelette pour GET /points/{id}/voice.

Les textes wolof definitifs sont un livrable de P3 (jalon T+1:30 /
T+3:00, cf Partie A.9). Ici on fournit une structure conforme au
contrat pour ne pas bloquer l'integration ; les "text_wo" marques
TODO doivent etre remplaces par les phrases validees par un locuteur
natif (Partie D.4).
"""

ADVICE = {
    "flood_red": {
        "audio_sequence": ["intro", "flood_red", "action_evacuate", "outro"],
        "text_fr": "Attention. L'eau monte {name}. Éloignez les enfants.",
        "text_wo": "TODO_WOLOF: alerte eau rouge",
    },
    "flood_yellow": {
        "audio_sequence": ["intro", "flood_yellow", "action_watch", "outro"],
        "text_fr": "Vigilance. L'eau monte doucement {name}. Restez attentifs.",
        "text_wo": "TODO_WOLOF: vigilance eau jaune",
    },
    "malaria_alert": {
        "audio_sequence": ["intro", "malaria_yellow", "action_larvicide", "outro"],
        "text_fr": "L'eau stagne {name} depuis plusieurs jours. Risque de moustiques, traitez le point d'eau.",
        "text_wo": "TODO_WOLOF: alerte paludisme fenetre d'or",
    },
    "all_clear": {
        "audio_sequence": ["intro", "all_clear", "outro"],
        "text_fr": "Rien à signaler {name}. Merci de votre vigilance.",
        "text_wo": "TODO_WOLOF: tout va bien",
    },
}


def advice_key_for(flood_level, malaria_level):
    if flood_level == "rouge":
        return "flood_red"
    if flood_level == "jaune":
        return "flood_yellow"
    if malaria_level in ("jaune", "rouge"):
        return "malaria_alert"
    return "all_clear"


def voice_payload(point):
    advice_key = point["advice_key"]
    content = ADVICE[advice_key]
    level = point["flood_level"] if advice_key.startswith("flood") else point["malaria_level"]
    return {
        "point_id": point["id"],
        "level": level,
        "audio_sequence": content["audio_sequence"],
        "text_fr": content["text_fr"].format(name=point["name"]),
        "text_wo": content["text_wo"],
    }
