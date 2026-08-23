"""NDOX BI — API backend (Partie B, cahier des charges Responsable Backend).

Lancement :
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from content import voice_payload
from models import CurageIn, ReadingIn, ReportIn, SimulateIn
from storage import STATE

app = FastAPI(title="NDOX BI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@app.post("/api/v1/readings")
def post_reading(reading: ReadingIn):
    try:
        point = STATE.record_reading(
            reading.point_id, reading.water_cm, reading.temp_c,
            reading.battery_v, reading.ts, reading.source,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"point_id inconnu: {reading.point_id}")
    return {"ok": True, "point_id": point["id"], "flood_level": point["flood_level"]}


@app.get("/api/v1/points")
def get_points():
    return {
        "generated_at": _now_iso(),
        "sim_day": STATE.sim_day,
        "points": STATE.all_public_points(),
    }


@app.get("/api/v1/points/{point_id}/voice")
def get_point_voice(point_id: str):
    if point_id not in STATE.points:
        raise HTTPException(status_code=404, detail=f"point_id inconnu: {point_id}")
    return voice_payload(STATE.public_point(point_id))


@app.post("/api/v1/reports")
def post_report(report: ReportIn):
    try:
        return STATE.register_report(
            report.borne_id, report.point_id, report.kind,
            report.duration_s, report.has_voice,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail=f"point_id inconnu: {report.point_id}")


@app.post("/api/v1/simulate")
def post_simulate(payload: SimulateIn):
    try:
        point = STATE.run_scenario(payload.scenario, payload.day)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"scenario inconnu: {payload.scenario}")
    return {
        "ok": True,
        "scenario": payload.scenario,
        "sim_day": STATE.sim_day,
        "point": point,
    }


@app.post("/api/v1/curage")
def post_curage(payload: CurageIn):
    if payload.point_id not in STATE.points:
        raise HTTPException(status_code=404, detail=f"point_id inconnu: {payload.point_id}")
    if payload.phase == "before":
        return STATE.curage_before(payload.point_id, payload.before_cmh)
    if payload.phase == "after":
        return STATE.curage_after(payload.point_id, payload.after_cmh)
    raise HTTPException(status_code=400, detail="phase doit etre 'before' ou 'after'")
