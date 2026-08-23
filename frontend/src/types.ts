export type Level = "vert" | "jaune" | "rouge";
export type PointType = "A" | "B" | "C" | "D";
export type ScreenId = "dashboard" | "ivr" | "compare";

export interface Point {
  id: string;
  name: string;
  lat: number;
  lng: number;
  population_exposee: number;
  water_cm: number;
  temp_c: number;
  stagnation_days: number;
  flood_index: number;
  flood_level: Level;
  malaria_index: number;
  malaria_level: Level;
  days_to_emergence: number | null;
  type: PointType;
  drain_rate_cmh: number;
  drain_rate_baseline_cmh: number;
  advice_key: string;
  updated_at: string;
}

export interface PointsResponse {
  generated_at: string;
  sim_day: number;
  points: Point[];
}

export interface VoiceResponse {
  point_id: string;
  level: Level;
  audio_sequence: string[];
  text_fr: string;
  text_wo: string;
}

export interface ReportResponse {
  ok: boolean;
  accepted: boolean;
  quorum: number;
  quorum_needed: number;
}

export interface CurageResponse {
  before_cmh: number;
  after_cmh: number;
  gain_pct: number;
  verdict: "CONFORME" | "NON CONFORME";
}
