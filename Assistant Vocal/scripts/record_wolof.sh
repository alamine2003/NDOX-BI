#!/bin/bash
# Enregistreur guidé des 18 clips wolof de la Borne Yëgle.
#
# Pour chaque clé : affiche le texte français à traduire, enregistre pendant
# que tu parles, nettoie, te fait réécouter, et te laisse refaire.
# Les placeholders français sont sauvegardés avant d'être écrasés.
#
#   bash scripts/record_wolof.sh            # les 18, dans l'ordre
#   bash scripts/record_wolof.sh intro outro    # seulement ces clés
#
# À lancer dans un vrai terminal SSH (il attend tes touches).
set -u

NDOX_DIR="${NDOX_DIR:-/home/eva/ndox}"
AUDIO="$NDOX_DIR/borne/audio"
BACKUP="$NDOX_DIR/borne/audio_fr"
TOOLS="$NDOX_DIR/scripts/audio_tools.py"
MIC="${NDOX_MIC:-default}"
LECTURE="${NDOX_PLAY:-pulse}"
TMP=/tmp/ndox_rec.wav

# Les 18 clés du contrat, avec le texte source à traduire en wolof.
CLES=(
"intro|Bonjour. Voici les nouvelles de l'eau dans votre quartier."
"flood_green|L'eau ne pose pas de problème aujourd'hui."
"flood_yellow|L'eau monte doucement. Faites attention."
"flood_red|Attention ! L'eau monte vite."
"action_evacuate|Éloignez les enfants. Ne traversez pas la rue."
"action_lift|Surélevez vos matelas et vos affaires."
"malaria_yellow|L'eau est là depuis plusieurs jours. Les moustiques vont arriver."
"action_empty|Videz les bassines, les vieux pneus et les récipients dans votre cour."
"malaria_red|Il y a beaucoup de moustiques. Dormez sous la moustiquaire."
"action_children|Protégez surtout les enfants et les femmes enceintes."
"health_post|Le poste de santé est ouvert. La route est praticable."
"health_blocked|La route du poste de santé est coupée. Passez par l'autre côté."
"press_to_report|Appuyez sur le bouton rouge et parlez pour signaler de l'eau."
"thanks|Merci. Votre message a été reçu."
"too_short|Je n'ai pas entendu. Recommencez et parlez plus fort."
"offline|Je n'ai pas de réseau. Voici les dernières nouvelles connues."
"ivr_menu|Tapez 1 pour votre quartier. Tapez 2 pour signaler de l'eau. Tapez 3 pour le poste de santé."
"outro|Merci. Revenez demain."
)

texte_de() {
    for e in "${CLES[@]}"; do
        [ "${e%%|*}" = "$1" ] && { echo "${e#*|}"; return; }
    done
}

# ── Préparation ────────────────────────────────────────────────────────────

if [ "$(systemctl is-active ndox-borne.service 2>/dev/null)" = "active" ]; then
    echo "▸ La borne tourne et occupe l'audio — je l'arrête le temps des enregistrements."
    sudo systemctl stop ndox-borne.service
    RELANCER=1
else
    RELANCER=0
fi

mkdir -p "$AUDIO"
if [ ! -d "$BACKUP" ]; then
    echo "▸ Sauvegarde des placeholders français dans audio_fr/"
    mkdir -p "$BACKUP"
    cp "$AUDIO"/*.wav "$BACKUP"/ 2>/dev/null
fi

echo
echo "════════════════════════════════════════════════════════════"
echo "  Enregistrement des clips wolof — Borne Yëgle"
echo "════════════════════════════════════════════════════════════"
echo "  micro   : $MIC        (change avec NDOX_MIC=...)"
echo "  lecture : $LECTURE"
echo
echo "  Conseils : parle à 20 cm du micro, ton posé mais net."
echo "  Pour les messages ROUGES, mets l'urgence dans la voix —"
echo "  c'est ce qu'aucune synthèse ne sait faire."
echo "════════════════════════════════════════════════════════════"
echo

# Liste à traiter : arguments, ou tout
if [ $# -gt 0 ]; then
    LISTE=("$@")
else
    LISTE=()
    for e in "${CLES[@]}"; do LISTE+=("${e%%|*}"); done
fi

TOTAL=${#LISTE[@]}
N=0
FAITS=0

for cle in "${LISTE[@]}"; do
    N=$((N + 1))
    txt=$(texte_de "$cle")
    if [ -z "$txt" ]; then
        echo "⚠ clé inconnue : $cle (ignorée)"
        continue
    fi

    while true; do
        echo "────────────────────────────────────────────────────────────"
        printf '  [%2d/%d]  %s\n' "$N" "$TOTAL" "$cle"
        echo
        echo "  À dire en WOLOF :"
        echo "    « $txt »"
        echo
        printf '  Entrée = démarrer  ·  s = passer  ·  q = quitter : '
        read -r choix
        case "$choix" in
            s|S) echo "  → passé"; break ;;
            q|Q) echo "  → arrêt"; N=$TOTAL; break 2 ;;
        esac

        echo
        echo "  ● ENREGISTREMENT — parle maintenant."
        printf '    Appuie sur Entrée quand tu as fini... '
        rm -f "$TMP"
        arecord -D "$MIC" -f S16_LE -r 44100 -c 1 -t wav "$TMP" >/dev/null 2>&1 &
        REC=$!
        read -r _
        kill "$REC" 2>/dev/null
        wait "$REC" 2>/dev/null
        echo

        if [ ! -s "$TMP" ]; then
            echo "  ✗ rien n'a été enregistré — micro introuvable ?"
            echo "    Micros disponibles :"
            arecord -l 2>/dev/null | grep -e "^card" | sed 's/^/      /'
            echo "    Relance avec : NDOX_MIC=plughw:1,0 bash $0"
            printf '  Entrée = réessayer · s = passer : '
            read -r r
            [ "$r" = "s" ] && break
            continue
        fi

        echo "  ▸ nettoyage (silences + volume)"
        python3 "$TOOLS" clean "$TMP" "$TMP.clean" && mv "$TMP.clean" "$TMP" \
            || echo "    (nettoyage sauté)"

        echo "  ▸ réécoute"
        aplay -D "$LECTURE" "$TMP" >/dev/null 2>&1

        echo
        printf '  Entrée = GARDER  ·  r = refaire  ·  s = passer : '
        read -r verdict
        case "$verdict" in
            r|R) echo; continue ;;
            s|S) echo "  → passé"; break ;;
            *)
                cp "$TMP" "$AUDIO/$cle.wav"
                echo "  ✓ enregistré → audio/$cle.wav"
                FAITS=$((FAITS + 1))
                echo
                break
                ;;
        esac
    done
done

# ── Bilan ──────────────────────────────────────────────────────────────────

echo
echo "════════════════════════════════════════════════════════════"
echo "  $FAITS clip(s) enregistré(s) en wolof"
echo
echo "  État de tous les clips :"
python3 "$TOOLS" info "$AUDIO"/*.wav 2>/dev/null | sed 's/^/    /'
echo "════════════════════════════════════════════════════════════"
echo
echo "  Réécouter une séquence complète :"
echo "     cd $NDOX_DIR/borne && python3 borne.py --say intro flood_red action_evacuate outro"
echo
echo "  Revenir aux placeholders français :"
echo "     cp $BACKUP/*.wav $AUDIO/"

if [ "$RELANCER" = "1" ]; then
    echo
    echo "▸ Redémarrage de la borne"
    sudo systemctl start ndox-borne.service
fi
