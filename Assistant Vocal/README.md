# NDOX BI — Borne Yëgle (rôle P3)

Borne vocale de quartier pour le hackathon UNIPRO TECH CLUB 2026.
Elle dit l'état de l'eau et laisse les habitants signaler un problème à la voix.

## Installation sur le boîtier

```bash
sudo bash scripts/install_borne.sh          # dépendances, audio, service — ne bascule rien
cd /home/eva/ndox/borne && python3 borne.py --keyboard   # test immédiat
```

L'installation **ne change pas** le programme qui démarre au boot. La bascule est
une commande séparée et réversible :

```bash
sudo bash scripts/switch_mode.sh borne   # NDOX BI démarre au boot, EVA non
sudo bash scripts/switch_mode.sh eva     # retour à EVA
bash scripts/switch_mode.sh status       # qui tourne, qui démarre au boot
```

EVA et la borne ne peuvent pas tourner ensemble : elles se partagent le micro et
l'enceinte Bluetooth. Le service déclare `Conflicts=eva.service`, systemd fait
donc respecter l'exclusion même si les deux sont lancés à la main.

## Commandes utiles

```bash
python3 borne.py                    # GPIO si présent, sinon clavier
python3 borne.py --keyboard         # force clavier + carrés colorés terminal
python3 borne.py --once             # un cycle puis sortie (test)
python3 borne.py --say intro flood_red action_evacuate    # joue une séquence
```

Au clavier : `B` = écouter, `R` = signaler, `Q` = quitter.

## La règle absolue (B.7)

La borne ne plante jamais faute de réseau. `GET /points` est encadré avec un
timeout de 3 s ; en cas de succès `cache.json` est réécrit, en cas d'échec il est
relu. Sans réseau **et** sans cache, elle parle quand même en repli local.

`cache.json` est livré pré-rempli avec les 8 points au jour J0 : la borne parle
dès la première seconde, avant même que le backend de P2 existe.

Manip de démo : appuyer sur bleu → elle parle ; couper le WiFi → la LED bleue
s'allume ; réappuyer → elle parle encore.

## Audio

Les 18 clips sont générés en **français** par Piper comme placeholders :

```bash
bash scripts/gen_audio_fr.sh
```

Pour passer au wolof, écraser chaque `.wav` de `borne/audio/` par
l'enregistrement du locuteur natif, **en gardant le même nom de fichier**. Aucun
changement de code. Le cahier des charges interdit le TTS wolof automatique.

`beep.wav` et `siren.wav` sont synthétisés par `scripts/gen_tones.py` (stdlib).

## Matériel et repli

| Élément | GPIO | Repli si absent |
|---|---|---|
| Bouton bleu (Écouter) | 17 | touche `B` |
| Bouton rouge (Parler) | 27 | touche `R` |
| LED verte / jaune / rouge | 22 / 23 / 24 | 3 carrés colorés dans le terminal |
| LED bleue (hors ligne) | 25 | mention `HORS LIGNE` |

`gpiozero` est optionnel. Sans lui, le programme est **exactement le même** :
c'est le repli prévu au B.4, le jury voit la même information.

## Limite connue

Sous systemd, l'entrée clavier n'existe pas (stdin est vide). Sans boutons GPIO
câblés, le service assure la surveillance et les **alertes rouges automatiques**,
mais les deux boutons demandent soit du GPIO, soit un lancement manuel dans un
terminal. Pour la démo au clavier, lancer `python3 borne.py --keyboard` à la main.

## Configuration

`borne/config.json` — l'essentiel : `api_base` (l'URL de P2), `point_id` (le point
surveillé par cette borne), `aplay_device` (`pulse` pour passer par le Bluetooth).
