#!/bin/bash
# Importe les enregistrements wolof dans la Borne Yëgle.
# Convertit n'importe quel format vers le WAV attendu, rogne les silences,
# égalise le volume, et installe sous le bon nom.
#
#   bash scripts/import_wolof.sh /home/eva/wolof_in          # importe
#   bash scripts/import_wolof.sh /home/eva/wolof_in --check  # simule, n'installe rien
#
# Les noms de fichiers doivent porter la clé : intro.m4a, 01_flood_red.mp3, etc.
set -u

SRC_DIR="${1:-}"
MODE="${2:-}"
NDOX_DIR="${NDOX_DIR:-/home/eva/ndox}"
AUDIO="$NDOX_DIR/borne/audio"
BACKUP="$NDOX_DIR/borne/audio_fr"
TOOLS="$NDOX_DIR/scripts/audio_tools.py"

[ -n "$SRC_DIR" ] || { echo "Usage : $0 <dossier> [--check]"; exit 1; }
[ -d "$SRC_DIR" ] || { echo "✗ dossier introuvable : $SRC_DIR"; exit 1; }

CLES="intro outro offline press_to_report thanks too_short \
weather_alert_24h prevent_drain \
flood_vigilance_50 flood_alert_65 flood_urgent_70 flood_critical_80 \
flood_predictive_15 flood_predictive_30 flood_predictive_60 \
action_evacuate action_no_wade action_electricity \
blockage_detected action_no_dump \
stagnation_started stagnation_day4 \
malaria_window_open malaria_window_open_a malaria_window_open_b \
malaria_emergence_countdown malaria_emergence_countdown_a \
malaria_emergence_countdown_b action_empty_now \
malaria_critical action_net_now treatment_done \
num_1 num_2 num_3 num_4 num_5 num_6 num_7 num_8 num_9 num_10"

# Clés facultatives : leur absence est normale, on ne la signale pas comme un
# manque. Les _a/_b et les nombres n'ont d'intérêt que si on veut les chiffres
# parlés ; sans eux la borne joue la version sans chiffre.
FACULTATIVES="malaria_window_open_a malaria_window_open_b \
malaria_emergence_countdown_a malaria_emergence_countdown_b \
num_1 num_2 num_3 num_4 num_5 num_6 num_7 num_8 num_9 num_10"

est_une_cle() {
    for c in $CLES; do [ "$c" = "$1" ] && return 0; done
    return 1
}

# ── Conversion ─────────────────────────────────────────────────────────────

if ! command -v ffmpeg >/dev/null; then
    echo "▸ ffmpeg absent — installation"
    sudo apt-get install -y ffmpeg || {
        echo "✗ ffmpeg indispensable pour convertir les enregistrements."
        echo "  Sans internet : réenregistre directement en WAV mono 44100 Hz 16 bits."
        exit 1
    }
fi

if [ "$MODE" != "--check" ] && [ ! -d "$BACKUP" ]; then
    echo "▸ Sauvegarde des placeholders français dans audio_fr/"
    mkdir -p "$BACKUP"
    cp "$AUDIO"/*.wav "$BACKUP"/ 2>/dev/null
fi

echo
echo "════════════════════════════════════════════════════════════"
echo "  Import des enregistrements wolof"
[ "$MODE" = "--check" ] && echo "  MODE SIMULATION — rien ne sera installé"
echo "════════════════════════════════════════════════════════════"
echo

IMPORTES=""
N_OK=0
N_KO=0

for f in "$SRC_DIR"/*; do
    [ -f "$f" ] || continue
    base=$(basename "$f")
    case "$base" in *.md|*.txt|*.MD) continue ;; esac

    # nom sans extension, sans préfixe numérique (01_, 01-, 1.), en minuscules
    cle=$(basename "$base" | sed -e 's/\.[^.]*$//' \
                                 -e 's/^[0-9]\+[-_. ]*//' \
                                 -e 's/[[:space:]]*$//' \
                          | tr '[:upper:]' '[:lower:]')

    if ! est_une_cle "$cle"; then
        printf '  ✗ %-28s clé inconnue « %s » — ignoré\n' "$base" "$cle"
        N_KO=$((N_KO + 1))
        continue
    fi

    tmp="/tmp/ndox_import_$cle.wav"
    # Mono 44100 Hz 16 bits : le format que la borne et aplay attendent.
    if ! ffmpeg -y -i "$f" -ac 1 -ar 44100 -sample_fmt s16 "$tmp" >/dev/null 2>&1; then
        printf '  ✗ %-28s conversion impossible (fichier corrompu ?)\n' "$base"
        N_KO=$((N_KO + 1))
        continue
    fi

    infos=$(python3 "$TOOLS" clean "$tmp" "$tmp.clean" 2>/dev/null)
    if [ -s "$tmp.clean" ]; then
        mv "$tmp.clean" "$tmp"
    fi

    if [ "$MODE" != "--check" ]; then
        cp "$tmp" "$AUDIO/$cle.wav"
    fi
    rm -f "$tmp"
    printf '  ✓ %-28s -> %s.wav %s\n' "$base" "$cle" "$(echo "$infos" | tr -s ' ')"
    IMPORTES="$IMPORTES $cle"
    N_OK=$((N_OK + 1))
done

# ── Bilan ──────────────────────────────────────────────────────────────────

echo
echo "  $N_OK importé(s), $N_KO ignoré(s)"

MANQUANTS=""
for c in $CLES; do
    case " $IMPORTES " in *" $c "*) ;; *) MANQUANTS="$MANQUANTS $c" ;; esac
done

# ── Cohérence linguistique ─────────────────────────────────────────────────
# Le moteur préfère la version chiffrée d'une phrase dès que ses trois morceaux
# existent. Si la version simple vient d'être fournie en wolof mais que _a/_b ou
# les nombres sont restés des placeholders français, la borne dirait une phrase
# moitié wolof moitié française. On retire donc les restes d'un groupe incomplet.
if [ "$MODE" != "--check" ]; then
    a_ete_importe() { case " $IMPORTES " in *" $1 "*) return 0 ;; *) return 1 ;; esac; }

    NUM_WOLOF=0
    for i in 1 2 3 4 5 6 7 8 9 10; do
        a_ete_importe "num_$i" && NUM_WOLOF=1
    done

    NETTOYES=""
    for groupe in malaria_window_open malaria_emergence_countdown; do
        if a_ete_importe "$groupe" \
           && ! { a_ete_importe "${groupe}_a" && a_ete_importe "${groupe}_b"; }; then
            for reste in "${groupe}_a" "${groupe}_b"; do
                [ -f "$AUDIO/$reste.wav" ] && { rm -f "$AUDIO/$reste.wav"; NETTOYES="$NETTOYES $reste"; }
            done
        fi
    done
    if [ "$NUM_WOLOF" = "0" ]; then
        for i in 1 2 3 4 5 6 7 8 9 10; do
            [ -f "$AUDIO/num_$i.wav" ] && { rm -f "$AUDIO/num_$i.wav"; NETTOYES="$NETTOYES num_$i"; }
        done
    fi
    if [ -n "$NETTOYES" ]; then
        echo
        echo "  ▸ Placeholders français retirés pour éviter les phrases mixtes :"
        echo "     $(echo $NETTOYES)"
        echo "    (la borne joue la version wolof sans chiffre — sauvegarde dans audio_fr/)"
    fi
fi

ESSENTIELS=""
OPTIONNELS=""
for c in $MANQUANTS; do
    case " $FACULTATIVES " in
        *" $c "*) OPTIONNELS="$OPTIONNELS $c" ;;
        *)        ESSENTIELS="$ESSENTIELS $c" ;;
    esac
done

if [ -n "$ESSENTIELS" ]; then
    echo
    echo "  Encore en français (placeholder Piper) :"
    for c in $ESSENTIELS; do echo "     $c"; done
    echo
    echo "  Ce n'est pas bloquant : la borne fonctionne, ces messages sont"
    echo "  simplement encore dits en français."
else
    echo
    echo "  ✓ Tous les messages essentiels sont en wolof."
fi

if [ -n "$OPTIONNELS" ]; then
    echo
    echo "  Facultatifs non fournis (chiffres parlés) — la borne joue"
    echo "  automatiquement la version sans chiffre, c'est prévu :"
    echo "    $(echo $OPTIONNELS | tr ' ' ' ')"
fi

echo
echo "════════════════════════════════════════════════════════════"
if [ "$MODE" = "--check" ]; then
    echo "  Simulation terminée. Relance sans --check pour installer."
else
    echo "  Réécoute la séquence d'alerte J0 :"
    echo "     cd $NDOX_DIR/borne && python3 borne.py --say intro flood_urgent_70 \\"
    echo "         flood_predictive_30 action_evacuate action_electricity action_no_wade outro"
    echo
    echo "  Revenir aux placeholders français :"
    echo "     cp $BACKUP/*.wav $AUDIO/"
fi
echo "════════════════════════════════════════════════════════════"
