"""Tests d'integration de l'API — verifient le contrat A.5 de bout en bout
(FastAPI + moteur + stockage), et les criteres d'acceptation B.10.
"""
import time

from seed import POINTS_SEED


def test_get_points_returns_all_eight(client):
    r = client.get("/api/v1/points")
    assert r.status_code == 200
    body = r.json()
    assert body["sim_day"] == 0
    assert "generated_at" in body
    assert {p["id"] for p in body["points"]} == {s["id"] for s in POINTS_SEED}


def test_get_points_matches_seed_types_and_curage_utile(client):
    body = client.get("/api/v1/points").json()
    by_id = {p["id"]: p for p in body["points"]}
    for seed in POINTS_SEED:
        assert by_id[seed["id"]]["type"] == seed["type_reel"], seed["id"]

    # Critere B.10 : P04 et P05 sortent en type D avec curage_utile False
    assert by_id["P04"]["type"] == "D"
    assert by_id["P04"]["curage_utile"] is False
    assert by_id["P05"]["type"] == "D"
    assert by_id["P05"]["curage_utile"] is False


def test_baseline_state_is_ras_for_non_d_points(client):
    # NDOX BI mesure l'age de l'eau : sans eau presente, tout doit etre vert.
    body = client.get("/api/v1/points").json()
    for p in body["points"]:
        if p["type"] != "D":
            assert p["flood_level"] == "vert", p["id"]
            assert p["malaria_level"] == "vert", p["id"]
            assert p["stagnation_days"] == 0, p["id"]


def test_get_points_responds_fast(client):
    start = time.perf_counter()
    r = client.get("/api/v1/points")
    elapsed = time.perf_counter() - start
    assert r.status_code == 200
    assert elapsed < 0.3  # Critere B.10 : < 300 ms


def test_cors_is_open(client):
    r = client.get("/api/v1/points", headers={"Origin": "http://example.com"})
    assert r.headers.get("access-control-allow-origin") == "*"


def test_post_reading_unknown_point_returns_404(client):
    r = client.post("/api/v1/readings", json={
        "device_id": "TEEW-99", "point_id": "P99", "ts": "2026-08-23T14:32:00Z",
        "water_cm": 10.0, "temp_c": 27.0, "battery_v": 4.0, "source": "sensor",
    })
    assert r.status_code == 404


def test_post_reading_matches_contract_example_exactly(client, monkeypatch):
    import weather
    # Cf A.7 J0 14h : 55mm de pluie tombent sur Keur Massar.
    monkeypatch.setattr(weather, "pluie_24h_mm", lambda lat, lng, point_id: 55.0)

    r = client.post("/api/v1/readings", json={
        "device_id": "TEEW-07", "point_id": "P07", "ts": "2026-08-23T14:32:00Z",
        "water_cm": 42.5, "temp_c": 29.4, "battery_v": 3.92, "source": "sensor",
    })
    assert r.status_code == 200
    assert r.json() == {"ok": True, "point_id": "P07", "flood_level": "rouge"}


def test_post_reading_updates_get_points(client):
    client.post("/api/v1/readings", json={
        "device_id": "TEEW-01", "point_id": "P01", "ts": "2026-08-23T10:00:00Z",
        "water_cm": 12.0, "temp_c": 28.0, "battery_v": 4.0, "source": "sensor",
    })
    body = client.get("/api/v1/points").json()
    p01 = next(p for p in body["points"] if p["id"] == "P01")
    assert p01["water_cm"] == 12.0
    assert p01["temp_c"] == 28.0


def test_voice_endpoint_unknown_point_404(client):
    assert client.get("/api/v1/points/P99/voice").status_code == 404


def test_voice_endpoint_shape_for_green_point(client):
    r = client.get("/api/v1/points/P01/voice")
    assert r.status_code == 200
    body = r.json()
    assert body["point_id"] == "P01"
    assert body["level"] == "vert"
    assert isinstance(body["audio_sequence"], list) and body["audio_sequence"]
    assert "text_fr" in body and "text_wo" in body


def test_voice_endpoint_reflects_flood_red(client, monkeypatch):
    import weather
    monkeypatch.setattr(weather, "pluie_24h_mm", lambda lat, lng, point_id: 55.0)
    client.post("/api/v1/readings", json={
        "device_id": "TEEW-07", "point_id": "P07", "ts": "2026-08-23T14:32:00Z",
        "water_cm": 42.5, "temp_c": 29.4, "battery_v": 3.92, "source": "sensor",
    })
    body = client.get("/api/v1/points/P07/voice").json()
    assert body["level"] == "rouge"
    assert "action_evacuate" in body["audio_sequence"]


def test_reports_quorum_not_reached_with_two_reports(client, monkeypatch):
    import weather
    monkeypatch.setattr(weather, "pluie_24h_mm", lambda lat, lng, point_id: 10.0)

    for borne in ("BORNE-01", "BORNE-02"):
        r = client.post("/api/v1/reports", json={
            "borne_id": borne, "point_id": "P01", "kind": "water",
            "duration_s": 4.2, "has_voice": True,
        })
    body = r.json()
    assert body == {"ok": True, "accepted": True, "quorum": 2.0, "quorum_needed": 3}


def test_reports_quorum_reached_with_three_reports(client, monkeypatch):
    import weather
    monkeypatch.setattr(weather, "pluie_24h_mm", lambda lat, lng, point_id: 10.0)

    for borne in ("BORNE-01", "BORNE-02", "BORNE-03"):
        r = client.post("/api/v1/reports", json={
            "borne_id": borne, "point_id": "P02", "kind": "water",
            "duration_s": 4.2, "has_voice": True,
        })
    assert r.json()["quorum"] == 3.0


def test_reports_anti_rebond_rejects_same_borne_within_window(client, monkeypatch):
    import weather
    monkeypatch.setattr(weather, "pluie_24h_mm", lambda lat, lng, point_id: 10.0)

    payload = {"borne_id": "BORNE-01", "point_id": "P03", "kind": "water",
               "duration_s": 4.2, "has_voice": True}
    first = client.post("/api/v1/reports", json=payload)
    second = client.post("/api/v1/reports", json=payload)
    assert first.json()["accepted"] is True
    assert second.json()["accepted"] is False


def test_curage_matches_contract_example_p02(client):
    before = client.post("/api/v1/curage", json={"point_id": "P02", "phase": "before", "before_cmh": 1.8})
    assert before.json() == {"ok": True, "phase": "before", "before_cmh": 1.8}

    after = client.post("/api/v1/curage", json={"point_id": "P02", "phase": "after", "after_cmh": 8.6})
    assert after.json() == {
        "before_cmh": 1.8, "after_cmh": 8.6, "gain_pct": 378, "verdict": "CONFORME",
    }


def test_curage_unknown_point_404(client):
    r = client.post("/api/v1/curage", json={"point_id": "P99", "phase": "before"})
    assert r.status_code == 404


def test_curage_invalid_phase_400(client):
    r = client.post("/api/v1/curage", json={"point_id": "P02", "phase": "sideways"})
    assert r.status_code == 400


def test_simulate_unknown_scenario_404(client):
    r = client.post("/api/v1/simulate", json={"scenario": "nope", "day": 0})
    assert r.status_code == 404


def test_simulate_day0_matches_flood_red_narrative(client):
    r = client.post("/api/v1/simulate", json={"scenario": "keur_massar_j0_j10", "day": 0})
    assert r.status_code == 200
    body = r.json()
    assert body["sim_day"] == 0
    assert body["point"]["id"] == "P07"
    assert body["point"]["water_cm"] == 42.5
    assert body["point"]["flood_level"] == "rouge"


def test_simulate_day2_recedes_to_green(client):
    body = client.post("/api/v1/simulate", json={"scenario": "keur_massar_j0_j10", "day": 2}).json()
    assert body["point"]["water_cm"] == 11.0
    assert body["point"]["flood_level"] == "vert"
    assert body["point"]["stagnation_days"] >= 1  # le compteur a demarre (A.7 J2)


def test_simulate_day4_crosses_malaria_window(client):
    body = client.post("/api/v1/simulate", json={"scenario": "keur_massar_j0_j10", "day": 4}).json()
    # A.7 J4 : l'indice P franchit le seuil -> fenetre d'or (alerte larvicide)
    assert body["point"]["malaria_level"] in ("jaune", "rouge")
    assert body["point"]["days_to_emergence"] is not None


def test_simulate_day6_treatment_resets_emergence_clock(client):
    body = client.post("/api/v1/simulate", json={"scenario": "keur_massar_j0_j10", "day": 6}).json()
    # A.7 J6 : traitement effectue -> compteur remis a zero, emergence evitee
    assert body["point"]["malaria_index"] == 0.0
    assert body["point"]["malaria_level"] == "vert"
    assert body["point"]["stagnation_days"] == 0
    assert body["point"]["days_to_emergence"] is None


def test_simulate_changes_get_points_sim_day(client):
    client.post("/api/v1/simulate", json={"scenario": "keur_massar_j0_j10", "day": 5})
    body = client.get("/api/v1/points").json()
    assert body["sim_day"] == 5
    p07 = next(p for p in body["points"] if p["id"] == "P07")
    assert p07["water_cm"] == 7.0


def test_simulate_day_clamped_to_last_available_day(client):
    body = client.post("/api/v1/simulate", json={"scenario": "keur_massar_j0_j10", "day": 999}).json()
    assert body["sim_day"] == 10
