#!/bin/bash
# Génère tous les clips en FRANÇAIS avec Piper, comme placeholders.
# Le cahier des charges impose du wolof enregistré par un locuteur natif :
# ces fichiers évitent de rester bloqué en attendant. Il suffira d'écraser
# les .wav par les enregistrements, les noms de clés sont identiques.
#
#   bash scripts/gen_audio_fr.sh
set -e

NDOX_DIR="${NDOX_DIR:-/home/eva/ndox}"
AUDIO="$NDOX_DIR/borne/audio"
PIPER="${PIPER_BIN:-/home/eva/eva/models/tts/piper/piper}"
MODEL="${PIPER_MODEL:-/home/eva/eva/models/tts/fr_FR-siwis-medium.onnx}"

[ -x "$PIPER" ] || { echo "✗ piper introuvable : $PIPER"; exit 1; }
[ -f "$MODEL" ] || { echo "✗ modèle introuvable : $MODEL"; exit 1; }
mkdir -p "$AUDIO"

dire() {
    local cle="$1"; shift
    printf '%s' "$*" | "$PIPER" --model "$MODEL" --output_file "$AUDIO/$cle.wav" 2>/dev/null
    printf '  %-32s %s\n' "$cle" "$*"
}

echo "▸ Structure de l'annonce"
dire intro            "Bonjour. Voici les nouvelles de l'eau dans votre quartier."
dire outro            "Merci. Revenez demain."
dire offline          "Je n'ai pas de réseau. Voici les dernières nouvelles connues."
dire press_to_report  "Appuyez sur le bouton rouge et parlez pour signaler de l'eau."
dire thanks           "Merci. Votre message a été reçu."
dire too_short        "Je n'ai pas entendu. Recommencez et parlez plus fort."

echo "▸ Phase 1 — Anticipation (J-1, avant la pluie)"
dire weather_alert_24h "Une forte pluie arrive demain. Préparez votre quartier maintenant."
dire prevent_drain     "Dégagez les caniveaux et videz vos récipients avant ce soir."

echo "▸ Phase 2 — Montée progressive de l'eau"
dire flood_vigilance_50 "L'eau atteint 50 centimètres. Restez informés."
dire flood_alert_65     "L'eau approche du seuil dangereux. Préparez-vous à agir."
dire flood_urgent_70    "Il reste peu de temps. Évacuez les zones basses maintenant."
dire flood_critical_80  "Alerte maximale. L'eau dépasse 80 centimètres. Cette zone est inondée."

echo "▸ Phase 2 bis — Estimation prédictive (clips auto-suffisants par tranche)"
dire flood_predictive_15 "Au rythme actuel, l'eau atteindra le seuil critique dans moins d'un quart d'heure."
dire flood_predictive_30 "Au rythme actuel, l'eau atteindra le seuil critique dans moins d'une demi-heure."
dire flood_predictive_60 "Au rythme actuel, l'eau atteindra le seuil critique dans moins d'une heure."

echo "▸ Phase 3 — Sécurité immédiate"
dire action_evacuate    "Évacuez immédiatement enfants et personnes âgées."
dire action_no_wade     "Ne traversez jamais l'eau à pied, même peu profonde."
dire action_electricity "Coupez le courant si l'eau approche des installations électriques."

echo "▸ Phase 4 — Canal bouché / déchets"
dire blockage_detected "Ce canal semble bloqué. Un technicien a été prévenu."
dire action_no_dump    "Ne jetez pas de déchets dans le canal. Ils bloquent l'écoulement."

echo "▸ Phase 5 — Décrue : l'âge de l'eau"
dire stagnation_started "La grosse eau est partie, mais une flaque reste. Nous la surveillons."
dire stagnation_day4    "Cette eau est là depuis quatre jours. Même petite, elle devient dangereuse."

echo "▸ Phase 6 — Fenêtre d'or paludisme"
# Version sans chiffre (repli) puis version en deux morceaux encadrant le nombre.
dire malaria_window_open   "Cette eau stagne depuis plusieurs jours. Les moustiques arrivent bientôt."
dire malaria_window_open_a "Cette eau stagne depuis"
dire malaria_window_open_b "jours. Les moustiques arrivent bientôt."
dire malaria_emergence_countdown   "Il reste très peu de jours avant l'apparition des moustiques. Agissez maintenant."
dire malaria_emergence_countdown_a "Il reste"
dire malaria_emergence_countdown_b "jours avant l'apparition des moustiques. Agissez maintenant."
dire action_empty_now      "Videz cette eau tout de suite, avant qu'il ne soit trop tard."

echo "▸ Phase 7 — Seuil critique paludisme"
dire malaria_critical "Cette eau stagne depuis plus de sept jours. Le danger est maximum."
dire action_net_now   "Dormez sous une moustiquaire imprégnée dès ce soir, sans exception."

echo "▸ Phase 8 — Résolution"
dire treatment_done "Ce point a été traité. Le risque est écarté."

echo "▸ Nombres (insérés au milieu des phrases de la phase 6)"
for n in 1 2 3 4 5 6 7 8 9 10; do
    case $n in
        1) mot="un" ;;  2) mot="deux" ;;   3) mot="trois" ;; 4) mot="quatre" ;;
        5) mot="cinq" ;; 6) mot="six" ;;   7) mot="sept" ;;  8) mot="huit" ;;
        9) mot="neuf" ;; 10) mot="dix" ;;
    esac
    dire "num_$n" "$mot"
done

echo "▸ Sons non parlés"
python3 "$NDOX_DIR/scripts/gen_tones.py" "$AUDIO"

echo
echo "✓ $(ls -1 "$AUDIO"/*.wav 2>/dev/null | wc -l) clips dans $AUDIO"
