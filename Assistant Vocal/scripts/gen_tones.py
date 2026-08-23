#!/usr/bin/env python3
"""
Génère beep.wav (invite à parler) et siren.wav (alerte rouge).
Stdlib uniquement — pas de sox ni de ffmpeg à installer sur le boîtier.
"""
import math
import os
import struct
import sys
import wave

RATE = 22050  # même fréquence que la sortie Piper, évite un rééchantillonnage


def ecrire(path, echantillons):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767))
                               for s in echantillons))


def enveloppe(i, total, montee=0.01):
    """Fondu aux extrémités : sans lui, chaque clip claque dans le haut-parleur."""
    n = int(RATE * montee)
    if i < n:
        return i / n
    if i > total - n:
        return max(0.0, (total - i) / n)
    return 1.0


def bip(freq=880.0, duree=0.18, volume=0.5):
    total = int(RATE * duree)
    return [volume * enveloppe(i, total) * math.sin(2 * math.pi * freq * i / RATE)
            for i in range(total)]


def sirene(duree=2.5, bas=520.0, haut=1180.0, periode=0.6, volume=0.55):
    """Balayage montant-descendant : porte mieux dans le bruit qu'un ton fixe."""
    total = int(RATE * duree)
    out, phase = [], 0.0
    for i in range(total):
        t = i / RATE
        # triangle 0->1->0 sur chaque période
        x = (t % periode) / periode
        ratio = 2 * x if x < 0.5 else 2 * (1 - x)
        freq = bas + (haut - bas) * ratio
        phase += 2 * math.pi * freq / RATE
        out.append(volume * enveloppe(i, total, 0.03) * math.sin(phase))
    return out


def main():
    dossier = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(dossier, exist_ok=True)
    ecrire(os.path.join(dossier, "beep.wav"), bip())
    ecrire(os.path.join(dossier, "siren.wav"), sirene())
    print("  beep.wav         bip court avant enregistrement")
    print("  siren.wav        sirène d'alerte rouge")


if __name__ == "__main__":
    main()
