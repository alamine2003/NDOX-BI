"""Schemas Pydantic — miroir exact du contrat d'API (Partie A.5)."""
from typing import Optional

from pydantic import BaseModel


class ReadingIn(BaseModel):
    device_id: str
    point_id: str
    ts: str
    water_cm: float
    temp_c: float
    battery_v: Optional[float] = None
    source: str = "sensor"


class ReportIn(BaseModel):
    borne_id: str
    point_id: str
    kind: str
    duration_s: float
    has_voice: bool = False


class SimulateIn(BaseModel):
    scenario: str
    day: int


class CurageIn(BaseModel):
    point_id: str
    phase: str  # "before" | "after"
    before_cmh: Optional[float] = None
    after_cmh: Optional[float] = None
