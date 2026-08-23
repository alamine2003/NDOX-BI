import type { Point, PointType, Level } from "../types";

export const COLOR: Record<Level | "bleu", string> = {
  vert: "#1D9E75",
  jaune: "#EF9F27",
  rouge: "#E24B4A",
  bleu: "#0C447C",
};

export const TYPE_LABEL: Record<PointType, string> = {
  A: "Ruissellement",
  B: "Obstruction",
  C: "Cuvette sans exutoire",
  D: "Nappe",
};

export const CURAGE_UTILE: Record<PointType, boolean> = {
  A: true,
  B: true,
  C: false,
  D: false,
};

export const TYPE_PARAMS: Record<PointType, { decay: number; floorFactor: number }> = {
  A: { decay: 0.55, floorFactor: 0.15 },
  B: { decay: 0.70, floorFactor: 0.35 },
  C: { decay: 0.92, floorFactor: 0.75 },
  D: { decay: 0.95, floorFactor: 0.80 },
};

export const BASE_DATE = new Date("2026-08-23T14:32:00Z");

/** Seed Jour 0 — Partie A.6 du cahier des charges (8 points de démonstration). */
export const SEED_POINTS: Point[] = [
  { id: "P01", name: "Yeumbeul Nord — Rue 12", lat: 14.7761, lng: -17.3612, population_exposee: 1400,
    water_cm: 10, temp_c: 28.0, stagnation_days: 0, flood_index: 0.19, flood_level: "vert",
    malaria_index: 0.08, malaria_level: "vert", days_to_emergence: null, type: "A",
    drain_rate_cmh: 3.0, drain_rate_baseline_cmh: 3.0, advice_key: "flood_clear",
    updated_at: "2026-08-23T14:32:05Z" },

  { id: "P02", name: "Keur Massar — Marché", lat: 14.7789, lng: -17.3204, population_exposee: 2100,
    water_cm: 12, temp_c: 29.0, stagnation_days: 3, flood_index: 0.23, flood_level: "vert",
    malaria_index: 0.35, malaria_level: "jaune", days_to_emergence: 5.0, type: "B",
    drain_rate_cmh: 1.8, drain_rate_baseline_cmh: 3.0, advice_key: "malaria_watch",
    updated_at: "2026-08-23T14:32:05Z" },

  { id: "P03", name: "Thiaroye — École Élém. 3", lat: 14.7550, lng: -17.3670, population_exposee: 900,
    water_cm: 6, temp_c: 27.5, stagnation_days: 0, flood_index: 0.12, flood_level: "vert",
    malaria_index: 0.05, malaria_level: "vert", days_to_emergence: null, type: "B",
    drain_rate_cmh: 3.0, drain_rate_baseline_cmh: 3.0, advice_key: "flood_clear",
    updated_at: "2026-08-23T14:32:05Z" },

  { id: "P04", name: "Guédiawaye — Cité Sotiba", lat: 14.7742, lng: -17.3945, population_exposee: 1800,
    water_cm: 22, temp_c: 29.8, stagnation_days: 9, flood_index: 0.42, flood_level: "jaune",
    malaria_index: 0.68, malaria_level: "rouge", days_to_emergence: 3.2, type: "D",
    drain_rate_cmh: 0.4, drain_rate_baseline_cmh: 0.4, advice_key: "malaria_alert",
    updated_at: "2026-08-23T14:32:05Z" },

  { id: "P05", name: "Pikine — Poste de santé", lat: 14.7550, lng: -17.3910, population_exposee: 1100,
    water_cm: 19, temp_c: 29.5, stagnation_days: 8, flood_index: 0.37, flood_level: "jaune",
    malaria_index: 0.55, malaria_level: "jaune", days_to_emergence: 4.5, type: "D",
    drain_rate_cmh: 0.5, drain_rate_baseline_cmh: 0.5, advice_key: "malaria_watch",
    updated_at: "2026-08-23T14:32:05Z" },

  { id: "P06", name: "Malika — Bas-fond Est", lat: 14.7930, lng: -17.3350, population_exposee: 600,
    water_cm: 33, temp_c: 28.9, stagnation_days: 6, flood_index: 0.63, flood_level: "rouge",
    malaria_index: 0.48, malaria_level: "jaune", days_to_emergence: 2.8, type: "C",
    drain_rate_cmh: 0.3, drain_rate_baseline_cmh: 0.3, advice_key: "flood_red",
    updated_at: "2026-08-23T14:32:05Z" },

  { id: "P07", name: "Keur Massar — Rue 12", lat: 14.7801, lng: -17.3180, population_exposee: 1200,
    water_cm: 42.5, temp_c: 29.4, stagnation_days: 0, flood_index: 0.81, flood_level: "rouge",
    malaria_index: 0.10, malaria_level: "vert", days_to_emergence: null, type: "A",
    drain_rate_cmh: 3.1, drain_rate_baseline_cmh: 3.0, advice_key: "flood_red",
    updated_at: "2026-08-23T14:32:05Z" },

  { id: "P08", name: "Yeumbeul Sud — Canal", lat: 14.7690, lng: -17.3560, population_exposee: 1500,
    water_cm: 16, temp_c: 28.2, stagnation_days: 3, flood_index: 0.31, flood_level: "jaune",
    malaria_index: 0.30, malaria_level: "jaune", days_to_emergence: 6.0, type: "B",
    drain_rate_cmh: 1.5, drain_rate_baseline_cmh: 3.0, advice_key: "malaria_watch",
    updated_at: "2026-08-23T14:32:05Z" },
];

/** Scénario scripté pour P07, le point vedette de la démo (Partie A.7). */
export const P07_TIMELINE: Record<number, Partial<Point>> = {
  0: { water_cm: 42.5, temp_c: 29.4, stagnation_days: 0, flood_index: 0.81, flood_level: "rouge", malaria_index: 0.10, malaria_level: "vert", days_to_emergence: null, advice_key: "flood_red" },
  1: { water_cm: 29, temp_c: 29.2, stagnation_days: 0, flood_index: 0.56, flood_level: "jaune", malaria_index: 0.12, malaria_level: "vert", days_to_emergence: null, advice_key: "flood_yellow" },
  2: { water_cm: 11, temp_c: 29.0, stagnation_days: 0, flood_index: 0.21, flood_level: "vert", malaria_index: 0.15, malaria_level: "vert", days_to_emergence: null, advice_key: "flood_clear" },
  3: { water_cm: 9, temp_c: 28.8, stagnation_days: 2, flood_index: 0.17, flood_level: "vert", malaria_index: 0.30, malaria_level: "jaune", days_to_emergence: 5.4, advice_key: "malaria_watch" },
  4: { water_cm: 8, temp_c: 29.0, stagnation_days: 4, flood_index: 0.15, flood_level: "vert", malaria_index: 0.55, malaria_level: "jaune", days_to_emergence: 3.2, advice_key: "malaria_alert" },
  5: { water_cm: 8, temp_c: 29.1, stagnation_days: 5, flood_index: 0.15, flood_level: "vert", malaria_index: 0.63, malaria_level: "rouge", days_to_emergence: 2.1, advice_key: "malaria_alert" },
  6: { water_cm: 7, temp_c: 28.5, stagnation_days: 0, flood_index: 0.13, flood_level: "vert", malaria_index: 0.14, malaria_level: "vert", days_to_emergence: null, advice_key: "treated" },
  7: { water_cm: 6, temp_c: 28.0, stagnation_days: 1, flood_index: 0.12, flood_level: "vert", malaria_index: 0.16, malaria_level: "vert", days_to_emergence: null, advice_key: "treated" },
  8: { water_cm: 6, temp_c: 27.8, stagnation_days: 2, flood_index: 0.12, flood_level: "vert", malaria_index: 0.18, malaria_level: "vert", days_to_emergence: null, advice_key: "treated" },
  9: { water_cm: 5, temp_c: 27.6, stagnation_days: 3, flood_index: 0.10, flood_level: "vert", malaria_index: 0.19, malaria_level: "vert", days_to_emergence: null, advice_key: "treated" },
  10: { water_cm: 5, temp_c: 27.5, stagnation_days: 4, flood_index: 0.10, flood_level: "vert", malaria_index: 0.21, malaria_level: "vert", days_to_emergence: null, advice_key: "treated" },
};
