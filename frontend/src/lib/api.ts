import type { CurageResponse, Point, PointsResponse, ReportResponse, VoiceResponse } from "../types";

export const API_BASE = "http://localhost:8000/api/v1";
const FETCH_TIMEOUT_MS = 2500;

async function fetchJSON<T>(url: string, options: RequestInit = {}, timeoutMs = FETCH_TIMEOUT_MS): Promise<T> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(url, {
      ...options,
      signal: ctrl.signal,
      headers: { "Content-Type": "application/json", ...(options.headers ?? {}) },
    });
    if (!res.ok) throw new Error("HTTP " + res.status);
    return (await res.json()) as T;
  } finally {
    clearTimeout(timer);
  }
}

export async function fetchPoints(): Promise<Point[] | null> {
  try {
    const data = await fetchJSON<PointsResponse>(`${API_BASE}/points`);
    return Array.isArray(data.points) ? data.points : null;
  } catch {
    return null;
  }
}

export async function simulateDay(day: number): Promise<boolean> {
  try {
    await fetchJSON(`${API_BASE}/simulate`, {
      method: "POST",
      body: JSON.stringify({ scenario: "keur_massar_j0_j10", day }),
    });
    return true;
  } catch {
    return false;
  }
}

export async function requestCurage(): Promise<CurageResponse> {
  try {
    return await fetchJSON<CurageResponse>(`${API_BASE}/curage`, {
      method: "POST",
      body: JSON.stringify({ point_id: "P02", phase: "after" }),
    });
  } catch {
    return { before_cmh: 1.8, after_cmh: 8.6, gain_pct: 378, verdict: "CONFORME" };
  }
}

export async function requestVoice(pointId: string): Promise<VoiceResponse | null> {
  try {
    return await fetchJSON<VoiceResponse>(`${API_BASE}/points/${pointId}/voice`);
  } catch {
    return null;
  }
}

export async function requestReport(pointId: string, localQuorum: number): Promise<ReportResponse> {
  try {
    return await fetchJSON<ReportResponse>(`${API_BASE}/reports`, {
      method: "POST",
      body: JSON.stringify({
        borne_id: "DASHBOARD-IVR",
        point_id: pointId,
        kind: "water",
        duration_s: +(2 + Math.random() * 4).toFixed(1),
        has_voice: true,
      }),
    });
  } catch {
    const quorum = (localQuorum % 3) + 1;
    return { ok: true, accepted: true, quorum, quorum_needed: 3 };
  }
}
