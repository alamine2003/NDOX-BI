#!/bin/bash
# Installe la Borne Yëgle sur le boîtier. Idempotent.
#   sudo bash scripts/install_borne.sh
set -e

[ "$(id -u)" -eq 0 ] || { echo "Lance avec sudo."; exit 1; }

NDOX_DIR="${NDOX_DIR:-/home/eva/ndox}"
EVA_USER="${EVA_USER:-eva}"

echo "▸ Vérification des outils audio"
for outil in aplay arecord pactl python3; do
    command -v "$outil" >/dev/null || echo "  ⚠ $outil manquant"
done

echo "▸ Droits sur $NDOX_DIR"
chown -R "$EVA_USER:$EVA_USER" "$NDOX_DIR"
chmod +x "$NDOX_DIR"/scripts/*.sh

echo "▸ Génération des clips audio français (placeholders)"
if [ -d "$NDOX_DIR/borne/audio" ] && [ -n "$(ls -A "$NDOX_DIR/borne/audio" 2>/dev/null)" ]; then
    echo "  audio/ déjà rempli — génération sautée (relancer gen_audio_fr.sh pour refaire)"
else
    sudo -u "$EVA_USER" NDOX_DIR="$NDOX_DIR" bash "$NDOX_DIR/scripts/gen_audio_fr.sh"
fi

echo "▸ Réglages persistants"
cat > /etc/default/ndox-borne <<EOF
# Adresse de l'enceinte Bluetooth de la borne
NDOX_BT_MAC=B2:31:6E:50:92:9D
NDOX_BT_VOLUME=85%
EOF

echo "▸ Service systemd"
install -m 644 "$NDOX_DIR/ndox-borne.service" /etc/systemd/system/ndox-borne.service
systemctl daemon-reload

echo "▸ gpiozero (boutons et LED physiques) — facultatif"
python3 -c "import gpiozero" 2>/dev/null \
    && echo "  ✓ gpiozero présent" \
    || echo "  gpiozero absent : la borne tournera au clavier (apt install python3-gpiozero)"

echo
echo "✓ Installé — RIEN n'a encore été basculé, EVA démarre toujours au boot."
echo
echo "  Test sans rien changer :"
echo "     cd $NDOX_DIR/borne && python3 borne.py --keyboard"
echo
echo "  Quand tu es prêt à faire de NDOX BI le programme principal :"
echo "     sudo bash $NDOX_DIR/scripts/switch_mode.sh borne"
echo "  Et pour revenir à EVA :"
echo "     sudo bash $NDOX_DIR/scripts/switch_mode.sh eva"
