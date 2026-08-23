#!/bin/bash
# Bascule le boîtier entre l'assistant EVA et la Borne Yëgle NDOX BI.
# Les deux se partagent le même micro et le même haut-parleur : un seul
# des deux peut tourner à la fois.
#
#   sudo bash switch_mode.sh borne    -> NDOX BI démarre au boot, EVA non
#   sudo bash switch_mode.sh eva      -> retour à EVA
#   bash switch_mode.sh status        -> qui est actif, qui démarre au boot
set -u

EVA_SVC=eva.service
BORNE_SVC=ndox-borne.service

statut() {
    printf '%-22s %-12s %s\n' "SERVICE" "MAINTENANT" "AU DÉMARRAGE"
    for s in "$BORNE_SVC" "$EVA_SVC"; do
        printf '%-22s %-12s %s\n' "$s" \
            "$(systemctl is-active  "$s" 2>/dev/null)" \
            "$(systemctl is-enabled "$s" 2>/dev/null)"
    done
    echo
    echo "Portail EVA : $(systemctl is-active eva_portal.service 2>/dev/null) (laissé actif dans les deux modes)"
}

case "${1:-status}" in
  borne)
    [ "$(id -u)" -eq 0 ] || { echo "Lance avec sudo."; exit 1; }
    echo "▸ Passage en mode BORNE YËGLE"
    # On arrête EVA d'abord : elle tient le micro et l'enceinte.
    systemctl disable --now "$EVA_SVC" 2>/dev/null
    sleep 2
    systemctl enable --now "$BORNE_SVC"
    sleep 3
    echo
    statut
    ;;
  eva)
    [ "$(id -u)" -eq 0 ] || { echo "Lance avec sudo."; exit 1; }
    echo "▸ Retour en mode EVA"
    systemctl disable --now "$BORNE_SVC" 2>/dev/null
    sleep 2
    systemctl enable --now "$EVA_SVC"
    sleep 3
    echo
    statut
    ;;
  status)
    statut
    ;;
  *)
    echo "Usage : $0 [borne|eva|status]"
    exit 1
    ;;
esac
