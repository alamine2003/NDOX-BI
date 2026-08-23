#!/usr/bin/env python3
"""
Nettoyage des clips enregistrés : coupe les silences aux extrémités et
égalise le volume.

Indispensable ici : une séquence de la borne enchaîne 5 à 7 clips bout à
bout. Sans rognage, chaque clip apporte son blanc de début et de fin, et
l'annonce devient hachée. Sans normalisation, un clip enregistré plus loin
du micro passe inaperçu au milieu des autres.

Stdlib uniquement — rien à installer sur le boîtier.

    python3 audio_tools.py clean entree.wav sortie.wav
    python3 audio_tools.py info fichier.wav
"""
import array
import os
import sys
import wave

SEUIL_RELATIF = 0.02      # 2 % du pic = début de la parole
SEUIL_PLANCHER = 250      # ...mais jamais en dessous du bruit de fond
PAD_AVANT_MS = 80         # on garde un peu d'air avant l'attaque
PAD_APRES_MS = 180        # et after, sinon la dernière syllabe est coupée
PIC_CIBLE = 0.89          # normalisation sans saturer


def lire(path):
    with wave.open(path, "rb") as w:
        if w.getsampwidth() != 2:
            raise ValueError(f"{path} : seul le 16 bits est géré")
        params = w.getparams()
        brut = w.readframes(w.getnframes())
    ech = array.array("h")
    ech.frombytes(brut[: len(brut) - (len(brut) % 2)])
    return ech, params


def ecrire(path, ech, params):
    with wave.open(path, "wb") as w:
        w.setnchannels(params.nchannels)
        w.setsampwidth(2)
        w.setframerate(params.framerate)
        w.writeframes(ech.tobytes())


def rogner(ech, framerate, canaux):
    if not ech:
        return ech, False
    pic = max(abs(s) for s in ech)
    if pic == 0:
        return ech, False
    seuil = max(int(pic * SEUIL_RELATIF), SEUIL_PLANCHER)

    debut = 0
    while debut < len(ech) and abs(ech[debut]) < seuil:
        debut += 1
    fin = len(ech) - 1
    while fin > debut and abs(ech[fin]) < seuil:
        fin -= 1
    if debut >= fin:
        return ech, False  # que du silence : on ne touche à rien

    pad_a = int(framerate * PAD_AVANT_MS / 1000) * canaux
    pad_b = int(framerate * PAD_APRES_MS / 1000) * canaux
    debut = max(0, debut - pad_a)
    fin = min(len(ech) - 1, fin + pad_b)
    # Rester aligné sur une trame complète en stéréo
    debut -= debut % canaux
    return ech[debut:fin + 1], True


def normaliser(ech):
    if not ech:
        return ech
    pic = max(abs(s) for s in ech)
    if pic == 0:
        return ech
    gain = (PIC_CIBLE * 32767) / pic
    if 0.95 < gain < 1.05:
        return ech  # déjà au bon niveau, inutile de retoucher
    return array.array("h", [
        max(-32768, min(32767, int(s * gain))) for s in ech
    ])


def duree(ech, params):
    if params.framerate == 0 or params.nchannels == 0:
        return 0.0
    return len(ech) / float(params.framerate * params.nchannels)


def cmd_clean(entree, sortie):
    ech, params = lire(entree)
    avant = duree(ech, params)
    ech, rogne = rogner(ech, params.framerate, params.nchannels)
    ech = normaliser(ech)
    apres = duree(ech, params)
    ecrire(sortie, ech, params)
    note = "" if rogne else "  (aucune parole détectée, non rogné)"
    print(f"  {avant:.2f}s -> {apres:.2f}s{note}")
    return 0 if rogne else 1


def cmd_info(path):
    ech, params = lire(path)
    pic = max((abs(s) for s in ech), default=0)
    print(f"{os.path.basename(path):20} {duree(ech, params):5.2f}s  "
          f"{params.framerate} Hz  {params.nchannels} canal/aux  "
          f"pic {100 * pic / 32767:.0f}%")
    return 0


def main():
    if len(sys.argv) >= 4 and sys.argv[1] == "clean":
        return cmd_clean(sys.argv[2], sys.argv[3])
    if len(sys.argv) >= 3 and sys.argv[1] == "info":
        for p in sys.argv[2:]:
            try:
                cmd_info(p)
            except Exception as e:
                print(f"  {os.path.basename(p)} : illisible ({e})")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
