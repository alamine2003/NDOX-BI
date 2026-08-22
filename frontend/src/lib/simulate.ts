import type { Level, Point } from "../types";
import { P07_TIMELINE, SEED_POINTS, TYPE_PARAMS } from "../data/seed";

const round1 = (x: number) => Math.round(x * 10) / 10;
const round2 = (x: number) => Math.round(x * 100) / 100;
const clamp = (x: number, a: number, b: number) => Math.max(a, Math.min(b, x));

function levelFromIndex(index: number, high: number, mid: number): Level {
  return index >= high ? "rouge" : index >= mid ? "jaune" : "vert";
}

function evolveGeneric(seed: Point, day: number): Point {
  const params = TYPE_PARAMS[seed.type];
  const water0 = seed.water_cm;
  const floor = water0 * params.floorFactor;
  const water = floor + (water0 - floor) * Math.pow(params.decay, day);
  const index = clamp(water / 52, 0, 1);
  const level = levelFromIndex(index, 0.6, 0.25);

  let stagnation: number;
  if (seed.type === "A" || seed.type === "B") {
    stagnation = water <= water0 * 0.4 ? Math.round(day * 0.6) : 0;
  } else {
    stagnation = Math.min(14, Math.round(day + seed.stagnation_days * 0.5));
  }

  const tempC = round1(seed.temp_c - day * 0.05);
  const malariaIndex = clamp(0.05 + stagnation * 0.07 + Math.max(0, tempC - 25) * 0.01, 0, 1);
  const malariaLevel = levelFromIndex(malariaIndex, 0.6, 0.3);
  const daysToEmergence = malariaIndex >= 0.3 ? Math.max(0.5, round1(8 - stagnation * 0.7)) : null;

  return {
    ...seed,
    water_cm: round1(water),
    flood_index: round2(index),
    flood_level: level,
    stagnation_days: stagnation,
    malaria_index: round2(malariaIndex),
    malaria_level: malariaLevel,
    days_to_emergence: daysToEmergence,
    temp_c: tempC,
    updated_at: new Date().toISOString(),
  };
}

/**
 * Repli hors-ligne (Partie B.8) : si /simulate et /points sont injoignables,
 * on rejoue localement l'évolution des points pour que le curseur temporel
 * continue de changer réellement l'affichage.
 */
export function computeLocalStateForDay(day: number, curagedP02: boolean): Point[] {
  return SEED_POINTS.map((seed) => {
    const point =
      seed.id === "P07" && P07_TIMELINE[day]
        ? { ...seed, ...P07_TIMELINE[day], updated_at: new Date().toISOString() }
        : evolveGeneric(seed, day);
    if (point.id === "P02" && curagedP02) {
      return { ...point, drain_rate_cmh: 8.6 };
    }
    return point;
  });
}

export function textForPoint(p: Point): string {
  if (p.flood_level === "rouge") return `Attention. L'eau monte à ${p.name}. Éloignez les enfants.`;
  if (p.flood_level === "jaune") return `Vigilance à ${p.name}. Le niveau de l'eau est surveillé.`;
  if (p.malaria_level !== "vert" && p.stagnation_days > 0)
    return `L'eau a baissé à ${p.name}, mais elle stagne depuis ${p.stagnation_days} jours. Risque de moustiques.`;
  return `Situation normale à ${p.name}. Aucune action nécessaire.`;
}
