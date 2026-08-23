"""Etat en memoire des points + journal des lectures.

Pas de PostgreSQL/Docker/Firebase (Partie B.11) : tout tient dans un
dict Python en memoire. Chaque lecture recue est journalisee sur
disque (readings.jsonl) pour garder une trace, mais l'etat courant
des points est recalcule au demarrage a partir du seed.
"""
import json
import os
from datetime import datetime, timedelta, timezone

import engine
import weather
from content import advice_key_for
from seed import POINTS_SEED
from simulate import SCENARIOS

SCENARIO_BASE_DATE = datetime(2026, 8, 23, 14, 0, tzinfo=timezone.utc)  # J0 14h, cf Partie A.7

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
READINGS_LOG = os.path.join(DATA_DIR, "readings.jsonl")

WATER_PRESENT_CM = 0.5


def _parse_ts(ts):
    if isinstance(ts, datetime):
        return ts
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def _now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class Store:
    def __init__(self):
        self.points = {}
        self.reports = []  # historique brut des signalements citoyens
        self.curage_sessions = {}  # point_id -> before_cmh en attente
        self.sim_day = 0
        self._init_points()

    def reset(self):
        """Reinitialise l'etat en place (utilise par les tests)."""
        self.points = {}
        self.reports = []
        self.curage_sessions = {}
        self.sim_day = 0
        self._init_points()

    def _init_points(self):
        for seed in POINTS_SEED:
            pid = seed["id"]
            static = seed["static_params"]
            initial = seed["initial"]
            self.points[pid] = {
                "id": pid,
                "name": seed["name"],
                "lat": seed["lat"],
                "lng": seed["lng"],
                "population_exposee": seed["population_exposee"],
                "static": static,
                "water_cm": initial["water_cm"],
                "temp_c": initial["temp_c"],
                "battery_v": 4.0,
                "drain_rate_cmh": initial["drain_rate_cmh"],
                "drain_rate_baseline_cmh": static["vidange_reference"],
                "prev_water_cm": None,
                "prev_ts": None,
                "historique": [],  # [(date_str, temp_c), ...] jours stagnants consecutifs
                "historique_dates": set(),
                "presence_dates": set(),
                "stagnation_days": 0,
                "dj_cumules": 0.0,
                "flood_index": 0.0,
                "flood_level": "vert",
                "malaria_index": 0.0,
                "malaria_level": "vert",
                "days_to_emergence": None,
                "type": seed["type_reel"],
                "curage_utile": engine.curage_utile(seed["type_reel"]),
                "advice_key": "all_clear",
                "updated_at": _now_iso(),
                "reported": False,
            }
            self._recompute(pid, pluie_24h_mm=0.0, vitesse_montee_cmh=0.0, ts=datetime.now(timezone.utc))

    def _recompute(self, point_id, pluie_24h_mm, vitesse_montee_cmh, ts):
        p = self.points[point_id]
        static = p["static"]

        p["flood_index"] = engine.indice_inondation(
            p["water_cm"], static["seuil_cm"], pluie_24h_mm, vitesse_montee_cmh, static["vulnerabilite"]
        )
        p["flood_level"] = engine.flood_level_from_index(p["flood_index"])

        date_str = ts.date().isoformat()
        water_present = p["water_cm"] > WATER_PRESENT_CM
        stagnant_today = water_present and p["water_cm"] <= static["seuil_cm"]

        if stagnant_today:
            if date_str not in p["historique_dates"]:
                p["historique_dates"].add(date_str)
                p["historique"].append((date_str, p["temp_c"]))
        else:
            p["historique"] = []
            p["historique_dates"] = set()
        p["stagnation_days"] = len(p["historique"])
        p["dj_cumules"] = round(engine.maturation(p["historique"]), 1)

        if water_present:
            p["presence_dates"].add(date_str)
        else:
            p["presence_dates"] = set()
        duree_jours = len(p["presence_dates"])

        p["malaria_index"] = engine.indice_palu(
            p["stagnation_days"], p["dj_cumules"], static["surface_m2"], static["presence_dechets"]
        )
        p["malaria_level"] = engine.malaria_level_from_index(p["malaria_index"])

        if p["stagnation_days"] >= 1:
            temp_moy = sum(t for _, t in p["historique"]) / len(p["historique"])
            p["days_to_emergence"] = engine.jours_avant_emergence(p["dj_cumules"], temp_moy)
        else:
            p["days_to_emergence"] = None

        p["type"] = engine.classifier(
            p["drain_rate_cmh"], static["vidange_reference"], static["monte_sans_pluie"], duree_jours
        )
        p["curage_utile"] = engine.curage_utile(p["type"])
        p["advice_key"] = advice_key_for(p["flood_level"], p["malaria_level"])
        p["updated_at"] = ts.isoformat().replace("+00:00", "Z") if ts.tzinfo else ts.isoformat() + "Z"

    def record_reading(self, point_id, water_cm, temp_c, battery_v, ts, source="sensor"):
        if point_id not in self.points:
            raise KeyError(point_id)
        p = self.points[point_id]
        ts_dt = _parse_ts(ts)

        vitesse_montee_cmh = 0.0
        if p["prev_ts"] is not None and p["prev_water_cm"] is not None:
            dt_h = (ts_dt - p["prev_ts"]).total_seconds() / 3600.0
            if dt_h > 0:
                delta = water_cm - p["prev_water_cm"]
                vitesse_montee_cmh = max(delta / dt_h, 0.0)
                if delta < 0:
                    drain_speed = -delta / dt_h
                    p["drain_rate_cmh"] = round(0.5 * p["drain_rate_cmh"] + 0.5 * drain_speed, 2)

        pluie = weather.pluie_24h_mm(p["lat"], p["lng"], point_id)

        p["water_cm"] = water_cm
        p["temp_c"] = temp_c
        if battery_v is not None:
            p["battery_v"] = battery_v

        self._recompute(point_id, pluie_24h_mm=pluie, vitesse_montee_cmh=vitesse_montee_cmh, ts=ts_dt)

        p["prev_water_cm"] = water_cm
        p["prev_ts"] = ts_dt

        self._log_reading(point_id, water_cm, temp_c, battery_v, ts, source)
        return self.public_point(point_id)

    def apply_scenario_day(self, point_id, water_cm, temp_c, pluie_24h_mm, ts_dt, force_reset=False):
        p = self.points[point_id]

        vitesse_montee_cmh = 0.0
        if p["prev_ts"] is not None and p["prev_water_cm"] is not None:
            dt_h = (ts_dt - p["prev_ts"]).total_seconds() / 3600.0
            if dt_h > 0:
                delta = water_cm - p["prev_water_cm"]
                vitesse_montee_cmh = max(delta / dt_h, 0.0)
                if delta < 0:
                    drain_speed = -delta / dt_h
                    p["drain_rate_cmh"] = round(0.5 * p["drain_rate_cmh"] + 0.5 * drain_speed, 2)

        p["water_cm"] = water_cm
        p["temp_c"] = temp_c

        self._recompute(point_id, pluie_24h_mm=pluie_24h_mm, vitesse_montee_cmh=vitesse_montee_cmh, ts=ts_dt)

        if force_reset:
            # Traitement larvicide : on casse le cycle de maturation.
            p["historique"] = []
            p["historique_dates"] = set()
            p["stagnation_days"] = 0
            p["dj_cumules"] = 0.0
            p["malaria_index"] = 0.0
            p["malaria_level"] = "vert"
            p["days_to_emergence"] = None
            p["advice_key"] = advice_key_for(p["flood_level"], p["malaria_level"])

        p["prev_water_cm"] = water_cm
        p["prev_ts"] = ts_dt

    def public_point(self, point_id):
        p = self.points[point_id]
        return {
            "id": p["id"],
            "name": p["name"],
            "lat": p["lat"],
            "lng": p["lng"],
            "population_exposee": p["population_exposee"],
            "water_cm": p["water_cm"],
            "temp_c": p["temp_c"],
            "stagnation_days": p["stagnation_days"],
            "flood_index": p["flood_index"],
            "flood_level": p["flood_level"],
            "malaria_index": p["malaria_index"],
            "malaria_level": p["malaria_level"],
            "days_to_emergence": p["days_to_emergence"],
            "type": p["type"],
            "curage_utile": p["curage_utile"],
            "drain_rate_cmh": p["drain_rate_cmh"],
            "drain_rate_baseline_cmh": p["drain_rate_baseline_cmh"],
            "advice_key": p["advice_key"],
            "updated_at": p["updated_at"],
        }

    def all_public_points(self):
        return [self.public_point(pid) for pid in self.points]

    def register_report(self, borne_id, point_id, kind, duration_s, has_voice):
        if point_id not in self.points:
            raise KeyError(point_id)
        now = datetime.now(timezone.utc)

        recent_same_borne = [
            r for r in self.reports
            if r["borne_id"] == borne_id and r["point_id"] == point_id
            and (now - r["ts"]).total_seconds() < engine.ANTI_REBOND_MIN * 60
        ]
        accepted = len(recent_same_borne) == 0

        if accepted:
            weight = 1.0
            point = self.points[point_id]
            if weather.pluie_24h_mm(point["lat"], point["lng"], point_id) == 0.0 and point["water_cm"] < 1.0:
                weight = 0.1
            self.reports.append({
                "borne_id": borne_id, "point_id": point_id, "kind": kind,
                "duration_s": duration_s, "has_voice": has_voice,
                "ts": now, "weight": weight,
            })

        window_start = now - timedelta(hours=engine.FENETRE_H)
        effective = sum(
            r["weight"] for r in self.reports
            if r["point_id"] == point_id and r["ts"] >= window_start
        )
        if effective >= engine.QUORUM:
            self.points[point_id]["reported"] = True

        return {
            "ok": True,
            "accepted": accepted,
            "quorum": round(effective, 1),
            "quorum_needed": engine.QUORUM,
        }

    def run_scenario(self, scenario_name, day):
        if scenario_name not in SCENARIOS:
            raise KeyError(scenario_name)
        scen = SCENARIOS[scenario_name]
        point_id = scen["point_id"]
        days = scen["days"]
        max_day = max(0, min(day, days[-1]["day"]))

        p = self.points[point_id]
        p["prev_water_cm"] = None
        p["prev_ts"] = None
        p["historique"] = []
        p["historique_dates"] = set()
        p["presence_dates"] = set()

        for entry in days:
            if entry["day"] > max_day:
                break
            ts_dt = SCENARIO_BASE_DATE + timedelta(days=entry["day"])
            self.apply_scenario_day(
                point_id, entry["water_cm"], entry["temp_c"], entry["pluie_24h_mm"],
                ts_dt, force_reset=entry.get("treatment", False),
            )

        self.sim_day = max_day
        return self.public_point(point_id)

    def curage_before(self, point_id, before_cmh=None):
        if point_id not in self.points:
            raise KeyError(point_id)
        value = before_cmh if before_cmh is not None else self.points[point_id]["drain_rate_cmh"]
        self.curage_sessions[point_id] = value
        return {"ok": True, "phase": "before", "before_cmh": value}

    def curage_after(self, point_id, after_cmh=None):
        if point_id not in self.points:
            raise KeyError(point_id)
        before_cmh = self.curage_sessions.pop(point_id, self.points[point_id]["drain_rate_cmh"])
        value = after_cmh if after_cmh is not None else self.points[point_id]["drain_rate_cmh"]
        self.points[point_id]["drain_rate_cmh"] = value
        return engine.certificat(before_cmh, value)

    def _log_reading(self, point_id, water_cm, temp_c, battery_v, ts, source):
        os.makedirs(DATA_DIR, exist_ok=True)
        entry = {
            "point_id": point_id, "water_cm": water_cm, "temp_c": temp_c,
            "battery_v": battery_v, "ts": ts if isinstance(ts, str) else str(ts),
            "source": source, "logged_at": _now_iso(),
        }
        try:
            with open(READINGS_LOG, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError:
            pass  # la demo continue meme si le disque est plein/verrouille


STATE = Store()
