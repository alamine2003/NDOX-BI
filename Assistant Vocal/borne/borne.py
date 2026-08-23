#!/usr/bin/env python3
"""
NDOX BI — Borne Yëgle
Borne vocale de quartier : elle dit en wolof l'état de l'eau et laisse
les habitants signaler un problème à la voix.

RÈGLE ABSOLUE (cahier des charges B.7) : la borne ne doit JAMAIS planter
parce que le réseau est absent. Tout appel HTTP est encadré, un cache.json
est écrit à chaque succès et relu à chaque échec.

Zéro dépendance externe : urllib de la stdlib, aplay/arecord pour l'audio,
gpiozero seulement s'il est présent (sinon clavier + affichage terminal).

    python3 borne.py              # boutons GPIO si dispo, sinon clavier
    python3 borne.py --keyboard   # force le mode clavier
    python3 borne.py --once       # un cycle puis sortie (test)
"""

import argparse
import array
import json
import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import wave
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_CONFIG = {
    "api_base": "http://localhost:8000/api/v1",
    "point_id": "P07",
    "borne_id": "BORNE-01",
    "poll_seconds": 30,
    "http_timeout": 3,
    "alert_cooldown_min": 15,
    "report_cooldown_min": 15,
    "record_seconds": 5,
    "min_report_seconds": 1.5,
    "silence_rms_threshold": 300,
    "aplay_device": "pulse",
    "arecord_device": "default",
    "audio_dir": "audio",
    "gpio": {
        "btn_blue": 17,
        "btn_red": 27,
        "led_green": 22,
        "led_yellow": 23,
        "led_red": 24,
        "led_blue": 25,
    },
}

# ── Journal ────────────────────────────────────────────────────────────────

def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


# ── Configuration ──────────────────────────────────────────────────────────

def load_config():
    cfg = dict(DEFAULT_CONFIG)
    path = os.path.join(BASE_DIR, "config.json")
    try:
        with open(path, encoding="utf-8") as f:
            user = json.load(f)
        gpio = dict(cfg["gpio"])
        gpio.update(user.pop("gpio", {}) or {})
        cfg.update(user)
        cfg["gpio"] = gpio
    except FileNotFoundError:
        log("config.json absent — valeurs par défaut")
    except Exception as e:
        log(f"config.json illisible ({e}) — valeurs par défaut")
    return cfg


# ── Audio ──────────────────────────────────────────────────────────────────

class Audio:
    """Lecture de clips pré-enregistrés. Zéro TTS, zéro synthèse (B.5)."""

    def __init__(self, cfg):
        self.dir = os.path.join(BASE_DIR, cfg["audio_dir"])
        self.device = cfg["aplay_device"]
        # Un seul son à la fois : sans ce verrou, une alerte automatique peut
        # se superposer à un appui sur le bouton bleu et rendre les deux
        # messages inaudibles.
        self.lock = threading.Lock()

    def _clip(self, key):
        return os.path.join(self.dir, f"{key}.wav")

    def existe(self, key):
        """Le moteur de messages s'en sert pour choisir entre la version
        chiffrée d'une phrase et son repli sans chiffre."""
        return os.path.isfile(self._clip(key))

    def play(self, key):
        path = self._clip(key)
        if not os.path.isfile(path):
            log(f"  ⚠ clip manquant : {key}.wav")
            return False
        cmd = ["aplay"]
        if self.device:
            cmd += ["-D", self.device]
        cmd.append(path)
        try:
            subprocess.run(cmd, capture_output=True, timeout=30)
            return True
        except Exception as e:
            log(f"  ⚠ lecture impossible ({key}) : {e}")
            return False

    def play_sequence(self, keys):
        with self.lock:
            log(f"🔊 {' + '.join(keys)}")
            for k in keys:
                self.play(k)

    def beep(self):
        self.play("beep")


# ── Sorties visuelles : GPIO réel ou repli terminal ────────────────────────

class Leds:
    """
    Trois LED de niveau + une LED « hors ligne ».
    Si le GPIO n'est pas disponible, on affiche trois gros carrés colorés
    dans le terminal : le jury voit exactement la même information (B.4).
    """

    ANSI = {
        "vert": "\033[42m", "jaune": "\033[43m",
        "rouge": "\033[41m", "off": "\033[100m",
    }

    def __init__(self, cfg, force_terminal=False):
        self.pins = cfg["gpio"]
        self.devices = None
        self.level = None
        self.offline = False
        if not force_terminal:
            self._try_gpio()

    def _try_gpio(self):
        try:
            from gpiozero import LED  # type: ignore
            self.devices = {
                "vert": LED(self.pins["led_green"]),
                "jaune": LED(self.pins["led_yellow"]),
                "rouge": LED(self.pins["led_red"]),
                "bleu": LED(self.pins["led_blue"]),
            }
            log("✓ LED GPIO actives")
        except Exception as e:
            log(f"GPIO indisponible ({e.__class__.__name__}) — affichage terminal")
            self.devices = None

    def set(self, level, offline=False):
        if level == self.level and offline == self.offline:
            return
        self.level, self.offline = level, offline
        if self.devices:
            for name, dev in self.devices.items():
                if name == "bleu":
                    dev.on() if offline else dev.off()
                else:
                    dev.on() if name == level else dev.off()
        # Toujours afficher, même quand le GPIO répond : sur un Pi où gpiozero
        # est installé mais où aucune LED n'est câblée, LED(22) réussit sans
        # rien allumer. Sans cet affichage, la démo ne montrerait rien.
        self._draw()

    def _draw(self):
        blocks = []
        for name in ("vert", "jaune", "rouge"):
            on = (name == self.level)
            color = self.ANSI[name] if on else self.ANSI["off"]
            blocks.append(f"{color}        \033[0m")
        etat = "HORS LIGNE" if self.offline else "en ligne"
        print(f"\n  {' '.join(blocks)}   [{(self.level or '?').upper()}] — {etat}\n",
              flush=True)

    def close(self):
        if self.devices:
            for dev in self.devices.values():
                try:
                    dev.close()
                except Exception:
                    pass


# ── Accès au backend ───────────────────────────────────────────────────────

class Api:
    def __init__(self, cfg):
        self.base = cfg["api_base"].rstrip("/")
        self.timeout = cfg["http_timeout"]
        self.cache_path = os.path.join(BASE_DIR, "cache.json")

    def _get(self, path):
        url = f"{self.base}{path}"
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return json.loads(r.read().decode("utf-8"))

    def _post(self, path, payload):
        url = f"{self.base}{path}"
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data, method="POST",
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return json.loads(r.read().decode("utf-8"))

    def get_state(self):
        """Renvoie (données, en_ligne). Ne lève jamais d'exception."""
        try:
            data = self._get("/points")
            try:
                with open(self.cache_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                log(f"  ⚠ cache non écrit : {e}")
            return data, True
        except Exception as e:
            log(f"  réseau absent ({e.__class__.__name__}) → cache local")
            try:
                with open(self.cache_path, encoding="utf-8") as f:
                    return json.load(f), False
            except Exception:
                return None, False

    def get_voice(self, point_id):
        """Séquence audio dictée par le backend, ou None si hors ligne."""
        try:
            return self._get(f"/points/{point_id}/voice")
        except Exception:
            return None

    def send_report(self, borne_id, point_id, duration_s, has_voice):
        try:
            return self._post("/reports", {
                "borne_id": borne_id,
                "point_id": point_id,
                "kind": "water",
                "duration_s": round(duration_s, 1),
                "has_voice": has_voice,
            })
        except Exception as e:
            log(f"  ⚠ signalement non transmis ({e.__class__.__name__}) — mis en attente")
            return None


# ── Choix des messages ─────────────────────────────────────────────────────

def find_point(data, point_id):
    if not data:
        return None
    for p in data.get("points", []):
        if p.get("id") == point_id:
            return p
    points = data.get("points") or []
    return points[0] if points else None


SEUILS = {
    "eau_vigilance": 50, "eau_alerte": 65, "eau_urgence": 70, "eau_critique": 80,
    "pluie_24h_mm": 40, "stagnation_alerte_j": 4, "stagnation_critique_j": 7,
    "compte_a_rebours_j": 3,
}

# Tranches de temps pour l'estimation prédictive. Chaque tranche est un clip
# AUTO-SUFFISANT : on ne colle pas un nombre au milieu d'une phrase, parce que
# des chiffres rapportés sonnent exactement comme la synthèse vocale qu'on
# refuse. La borne arrondit à la tranche supérieure.
TRANCHES_TEMPS = [(15, "flood_predictive_15"),
                  (30, "flood_predictive_30"),
                  (60, "flood_predictive_60")]


def _nb(valeur, defaut=0.0):
    try:
        return float(valeur)
    except (TypeError, ValueError):
        return defaut


def _avec_nombre(prefixe, n, suffixe, repli, existe):
    """
    Rend [prefixe, num_N, suffixe] si les trois clips existent, sinon [repli].
    Permet d'enregistrer d'abord la version sans chiffre et d'ajouter les
    nombres plus tard sans toucher au code.
    """
    n = int(round(n))
    parts = [prefixe, f"num_{n}", suffixe]
    if existe and all(existe(p) for p in parts):
        return parts
    return [repli]


def build_sequence(point, online, existe=None, rise_rate_cmh=None):
    """
    Moteur de sélection des messages — les 8 phases du scénario.

    Utilisé quand /points/{id}/voice est injoignable, et c'est le cas nominal
    hors ligne. Quand le backend répond, sa séquence a la priorité : c'est lui
    qui détient la météo et l'état des traitements.

    L'ordre n'est pas décoratif : on parle d'abord de ce qui tue aujourd'hui
    (l'eau qui monte), ensuite de ce qui tuera dans huit jours (les moustiques).
    """
    p = point or {}
    seq = ["intro"]
    if not online:
        seq.append("offline")

    eau = _nb(p.get("water_cm"))
    stagnation = _nb(p.get("stagnation_days"))
    pluie24 = _nb(p.get("rain_forecast_24h_mm"))
    emergence = p.get("days_to_emergence")
    montee = _nb(p.get("rise_rate_cmh"), _nb(rise_rate_cmh))

    # ── Phase 8 — Résolution. Court-circuite tout : si le point est traité,
    #    l'annoncer et s'arrêter là, c'est la punchline de la démo.
    if p.get("treated"):
        return seq + ["treatment_done", "outro"]

    # ── Phase 1 — Anticipation (J-1). Seulement tant que l'eau n'est pas là :
    #    « préparez-vous » n'a aucun sens quand on a déjà les pieds dedans.
    if pluie24 >= SEUILS["pluie_24h_mm"] and eau < SEUILS["eau_vigilance"]:
        seq += ["weather_alert_24h", "prevent_drain"]

    # ── Phase 2 — Montée progressive. Un seul palier annoncé, le plus haut.
    if eau >= SEUILS["eau_critique"]:
        seq.append("flood_critical_80")
    elif eau >= SEUILS["eau_urgence"]:
        seq.append("flood_urgent_70")
    elif eau >= SEUILS["eau_alerte"]:
        seq.append("flood_alert_65")
    elif eau >= SEUILS["eau_vigilance"]:
        seq.append("flood_vigilance_50")

    # Estimation prédictive : uniquement dans la fenêtre où elle a du sens,
    # entre le seuil d'alerte et le seuil critique, et si l'eau monte vraiment.
    if SEUILS["eau_alerte"] <= eau < SEUILS["eau_critique"] and montee > 0.1:
        minutes = (SEUILS["eau_critique"] - eau) / montee * 60.0
        for plafond, cle in TRANCHES_TEMPS:
            if minutes <= plafond:
                seq.append(cle)
                break

    # ── Phase 3 — Sécurité immédiate, du plus grave au moins grave.
    if eau >= SEUILS["eau_urgence"]:
        seq.append("action_evacuate")
    if eau >= SEUILS["eau_alerte"]:
        seq.append("action_electricity")
    if eau >= SEUILS["eau_vigilance"]:
        seq.append("action_no_wade")

    # ── Phase 4 — Canal bouché. Le type B, c'est la vidange anormalement lente.
    debit = _nb(p.get("drain_rate_cmh"))
    debit_ref = _nb(p.get("drain_rate_baseline_cmh"))
    bouche = p.get("blockage_confirmed")
    if bouche is None:
        bouche = p.get("type") == "B" and debit_ref > 0 and debit < 0.5 * debit_ref
    if bouche:
        seq.append("blockage_detected")
    elif eau < SEUILS["eau_vigilance"] and p.get("flood_level") == "vert":
        # Message préventif : c'est en période calme qu'on peut être entendu
        # sur les déchets, pas au milieu d'une inondation.
        seq.append("action_no_dump")

    # ── Phase 5 — Décrue : l'âge de l'eau. Actif même sur une flaque de 2 cm,
    #    c'est tout l'insight du projet.
    if stagnation >= SEUILS["stagnation_critique_j"]:
        # ── Phase 7 — Seuil critique paludisme
        seq += ["malaria_critical", "action_net_now"]
    else:
        if stagnation >= SEUILS["stagnation_alerte_j"]:
            seq.append("stagnation_day4")
        elif stagnation >= 1:
            seq.append("stagnation_started")

        # ── Phase 6 — Fenêtre d'or
        if p.get("malaria_level") == "jaune":
            seq += _avec_nombre("malaria_window_open_a", stagnation,
                                "malaria_window_open_b",
                                "malaria_window_open", existe)
        if emergence is not None and 0 < _nb(emergence) <= SEUILS["compte_a_rebours_j"]:
            seq += _avec_nombre("malaria_emergence_countdown_a", _nb(emergence),
                                "malaria_emergence_countdown_b",
                                "malaria_emergence_countdown", existe)
            seq.append("action_empty_now")

    seq += ["press_to_report", "outro"]
    return seq


# ── Enregistrement d'un signalement ────────────────────────────────────────

def wav_rms(path):
    """RMS d'un wav 16 bits. audioop a disparu en Python 3.13, on le fait ici."""
    try:
        with wave.open(path, "rb") as w:
            if w.getsampwidth() != 2:
                return None
            frames = w.readframes(w.getnframes())
        if not frames:
            return 0
        samples = array.array("h")
        samples.frombytes(frames[: len(frames) - (len(frames) % 2)])
        if not samples:
            return 0
        total = sum(float(s) * s for s in samples)
        return int((total / len(samples)) ** 0.5)
    except Exception:
        return None


def wav_duration(path):
    try:
        with wave.open(path, "rb") as w:
            return w.getnframes() / float(w.getframerate() or 1)
    except Exception:
        return 0.0


# ── La borne ───────────────────────────────────────────────────────────────

class Borne:
    def __init__(self, cfg, force_terminal=False):
        self.cfg = cfg
        self.audio = Audio(cfg)
        self.leds = Leds(cfg, force_terminal)
        self.api = Api(cfg)
        self.point = None
        self.online = False
        self.last_alert = 0.0
        self.last_report = 0.0
        self.busy = threading.Lock()
        self.stop = threading.Event()
        # Historique (instant, hauteur) pour calculer la vitesse de montée
        # quand le backend ne la fournit pas. Sans elle, pas d'estimation
        # prédictive « l'eau atteindra le seuil dans X minutes ».
        self.historique = []
        self.montee = None

    def _vitesse_montee_cmh(self, eau_cm):
        """cm/h sur les 10 dernières minutes. None si trop peu de recul."""
        now = time.time()
        self.historique.append((now, eau_cm))
        self.historique = [(t, v) for t, v in self.historique if now - t <= 600]
        if len(self.historique) < 2:
            return None
        t0, v0 = self.historique[0]
        dt = now - t0
        if dt < 60:  # moins d'une minute de recul : le bruit domine la pente
            return None
        return (eau_cm - v0) / (dt / 3600.0)

    # -- cycle de rafraîchissement --

    def refresh(self):
        data, online = self.api.get_state()
        self.online = online
        point = find_point(data, self.cfg["point_id"])
        if point:
            self.point = point
            self.montee = self._vitesse_montee_cmh(_nb(point.get("water_cm")))
            level = point.get("flood_level", "vert")
            self.leds.set(level, offline=not online)
            log(f"  {point.get('id')} · eau {point.get('water_cm')} cm · "
                f"inondation {level} · paludisme {point.get('malaria_level')} "
                f"· stagnation {point.get('stagnation_days')} j"
                + (f" · montée {self.montee:+.1f} cm/h" if self.montee else "")
                + ("" if online else "  (cache)"))
            self.maybe_alert(level)
        else:
            self.leds.set(None, offline=not online)
            log("  aucun point exploitable (ni réseau ni cache)")

    def maybe_alert(self, level):
        """Alerte automatique en rouge, au plus une fois par quart d'heure."""
        if level != "rouge":
            return
        cooldown = self.cfg["alert_cooldown_min"] * 60
        if time.time() - self.last_alert < cooldown:
            return
        self.last_alert = time.time()
        log("🚨 niveau ROUGE → annonce automatique")
        self.speak(["siren"] + build_sequence(self.point, self.online,
                                        existe=self.audio.existe,
                                        rise_rate_cmh=self.montee))

    # -- actions --

    def speak(self, seq):
        self.audio.play_sequence(seq)

    def on_blue(self):
        """Bouton Écouter : que le réseau soit là ou non, elle parle."""
        if not self.busy.acquire(blocking=False):
            log("  (déjà en train de parler)")
            return
        try:
            log("🔵 bouton ÉCOUTER")
            seq = None
            if self.online:
                voice = self.api.get_voice(self.cfg["point_id"])
                if voice and voice.get("audio_sequence"):
                    seq = list(voice["audio_sequence"])
            if not seq:
                seq = build_sequence(self.point, self.online,
                                        existe=self.audio.existe,
                                        rise_rate_cmh=self.montee)
            self.speak(seq)
        finally:
            self.busy.release()

    def on_red(self):
        """Bouton Parler : l'habitant signale de l'eau à la voix."""
        if not self.busy.acquire(blocking=False):
            log("  (occupée)")
            return
        try:
            cooldown = self.cfg["report_cooldown_min"] * 60
            if time.time() - self.last_report < cooldown:
                reste = int((cooldown - (time.time() - self.last_report)) / 60)
                log(f"🔴 anti-rebond : encore {reste} min")
                self.speak(["thanks"])
                return

            log("🔴 bouton PARLER — enregistrement")
            self.audio.beep()
            path = "/tmp/ndox_report.wav"
            secs = self.cfg["record_seconds"]
            try:
                subprocess.run(
                    ["arecord", "-D", self.cfg["arecord_device"],
                     "-d", str(secs), "-f", "cd", "-t", "wav", path],
                    capture_output=True, timeout=secs + 10)
            except Exception as e:
                log(f"  ⚠ micro indisponible : {e}")
                self.speak(["too_short"])
                return

            dur = wav_duration(path)
            rms = wav_rms(path)
            # Il faut PARLER, pas seulement appuyer (filtre 4 du dossier §10.2).
            trop_court = dur < self.cfg["min_report_seconds"]
            silence = rms is not None and rms < self.cfg["silence_rms_threshold"]
            if trop_court or silence:
                log(f"  rejeté (durée {dur:.1f}s, rms {rms}) → too_short")
                self.speak(["too_short"])
                return

            log(f"  accepté (durée {dur:.1f}s, rms {rms})")
            r = self.api.send_report(self.cfg["borne_id"], self.cfg["point_id"],
                                     dur, True)
            if r:
                log(f"  quorum {r.get('quorum')}/{r.get('quorum_needed')}")
            self.last_report = time.time()
            self.speak(["thanks"])
        finally:
            self.busy.release()

    # -- entrées --

    def wire_gpio(self):
        try:
            from gpiozero import Button  # type: ignore
            pins = self.cfg["gpio"]
            # hold_time : appui long de 2 s, les enfants s'en lassent (§10.2).
            self.btn_blue = Button(pins["btn_blue"], hold_time=0.05)
            self.btn_red = Button(pins["btn_red"], hold_time=0.05)
            self.btn_blue.when_pressed = lambda: threading.Thread(
                target=self.on_blue, daemon=True).start()
            self.btn_red.when_pressed = lambda: threading.Thread(
                target=self.on_red, daemon=True).start()
            log("✓ boutons GPIO actifs")
            return True
        except Exception as e:
            log(f"boutons GPIO indisponibles ({e.__class__.__name__}) — clavier")
            return False

    def keyboard_loop(self):
        log("Clavier : [B] écouter · [R] signaler · [Q] quitter")
        for line in sys.stdin:
            key = line.strip().lower()
            if key == "b":
                threading.Thread(target=self.on_blue, daemon=True).start()
            elif key == "r":
                threading.Thread(target=self.on_red, daemon=True).start()
            elif key == "q":
                self.stop.set()
                return

    # -- boucle principale --

    def run(self, once=False, force_keyboard=False):
        log("═══ NDOX BI — Borne Yëgle ═══")
        log(f"point surveillé : {self.cfg['point_id']} · api {self.cfg['api_base']}")

        if force_keyboard or not self.wire_gpio():
            threading.Thread(target=self.keyboard_loop, daemon=True).start()

        try:
            while not self.stop.is_set():
                self.refresh()
                if once:
                    break
                self.stop.wait(self.cfg["poll_seconds"])
        except KeyboardInterrupt:
            pass
        finally:
            self.leds.close()
            log("arrêt propre")


def main():
    ap = argparse.ArgumentParser(description="NDOX BI — Borne Yëgle")
    ap.add_argument("--keyboard", action="store_true",
                    help="force le clavier même si le GPIO est présent")
    ap.add_argument("--once", action="store_true",
                    help="un seul cycle puis sortie (test)")
    ap.add_argument("--say", metavar="CLE", nargs="+",
                    help="joue une séquence de clips puis sort")
    args = ap.parse_args()

    cfg = load_config()

    if args.say:
        Audio(cfg).play_sequence(args.say)
        return

    Borne(cfg, force_terminal=args.keyboard).run(
        once=args.once, force_keyboard=args.keyboard)


if __name__ == "__main__":
    main()
