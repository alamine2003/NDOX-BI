#!/bin/bash
# Prépare la sortie audio de la borne : casque/enceinte Bluetooth en A2DP,
# volume forcé à un niveau audible.
#
# Le volume est forcé parce que l'« absolute volume » A2DP recopie le volume
# matériel de l'enceinte dans PulseAudio : au retour de veille il revient
# souvent à 0 %, et la borne parle alors dans le vide.
#
# Sort toujours en 0 : une enceinte absente ne doit pas empêcher la borne de
# démarrer — elle bascule simplement sur la sortie jack.

MAC="${NDOX_BT_MAC:-B2:31:6E:50:92:9D}"
VOLUME="${NDOX_BT_VOLUME:-85%}"
CARD="bluez_card.$(echo "$MAC" | tr ':' '_')"
SINK="bluez_sink.$(echo "$MAC" | tr ':' '_').a2dp_sink"

echo "🔊 Préparation audio (Bluetooth $MAC)"

if ! pactl info >/dev/null 2>&1; then
    echo "  ⚠ PulseAudio absent — la borne utilisera la sortie ALSA par défaut"
    exit 0
fi

# Renégociation A2DP fraîche : sans la déconnexion préalable, BlueZ garde le
# profil HFP mono de la session précédente.
bluetoothctl disconnect "$MAC" >/dev/null 2>&1
sleep 2

for i in 1 2 3; do
    bluetoothctl connect "$MAC" >/dev/null 2>&1
    sleep 4
    for j in 1 2 3 4 5 6; do
        if pactl list cards 2>/dev/null | grep -A 25 "$CARD" | grep -q "a2dp_sink.*available: yes"; then
            pactl set-card-profile "$CARD" a2dp_sink 2>/dev/null
            sleep 1
            break
        fi
        sleep 1
    done
    if pactl list sinks short 2>/dev/null | grep -q "a2dp"; then
        pactl set-default-sink "$SINK" 2>/dev/null
        pactl set-sink-mute "$SINK" 0 2>/dev/null
        pactl set-sink-volume "$SINK" "$VOLUME" 2>/dev/null
        echo "  ✓ enceinte Bluetooth prête, volume $VOLUME"
        exit 0
    fi
    echo "  tentative $i/3..."
done

echo "  ⚠ Bluetooth indisponible — sortie audio par défaut"
exit 0
