"""Tests unitaires du moteur — Partie B.4 a B.7.

But : verifier que chaque formule est fidele au cahier des charges,
independamment de l'API et du stockage.
"""
import engine


class TestIndiceInondation:
    def test_zero_everything_is_zero(self):
        assert engine.indice_inondation(0, 30, 0, 0, 0) == 0.0

    def test_clips_each_component_at_one(self):
        # water tres au-dessus du seuil, pluie enorme, montee tres rapide
        i = engine.indice_inondation(9999, 30, 9999, 9999, 0)
        assert i == 0.9  # 0.4+0.3+0.2 (vulnerabilite=0)

    def test_matches_contract_example_p07_day0(self):
        # Reprend exactement l'exemple A.5 / A.7 : P07, 42.5cm, pluie 55mm
        i = engine.indice_inondation(42.5, 30, 55, 0, 0.4)
        assert i == 0.74
        assert engine.flood_level_from_index(i) == "rouge"


class TestFloodLevelThresholds:
    def test_vert_below_035(self):
        assert engine.flood_level_from_index(0.34) == "vert"

    def test_jaune_boundary_inclusive_035(self):
        assert engine.flood_level_from_index(0.35) == "jaune"

    def test_jaune_boundary_inclusive_065(self):
        assert engine.flood_level_from_index(0.65) == "jaune"

    def test_rouge_above_065(self):
        assert engine.flood_level_from_index(0.66) == "rouge"


class TestMaturation:
    def test_empty_history_is_zero(self):
        assert engine.maturation([]) == 0

    def test_sums_degrees_above_base(self):
        # 29 - 16 = 13, deux jours identiques -> 26
        assert engine.maturation([("2026-08-23", 29.0), ("2026-08-24", 29.0)]) == 26

    def test_temp_below_base_contributes_zero(self):
        assert engine.maturation([("2026-08-23", 10.0)]) == 0


class TestJoursAvantEmergence:
    def test_already_reached_returns_zero(self):
        assert engine.jours_avant_emergence(105.0, 29.0) == 0
        assert engine.jours_avant_emergence(200.0, 29.0) == 0

    def test_pitch_example_29_degrees(self):
        # B.13 : "a 29 degres ca fait sept jours" (105 / 13 ~ 8.1 en realite,
        # on verifie juste la formule, pas le chiffre approximatif du pitch)
        jours = engine.jours_avant_emergence(0, 29.0)
        assert jours == round(105.0 / 13.0, 1)


class TestIndicePalu:
    def test_no_stagnation_is_zero(self):
        assert engine.indice_palu(0, 50, 100, True) == 0.0

    def test_clips_at_one(self):
        assert engine.indice_palu(30, 999, 999, True) == 1.0

    def test_surface_and_dechets_contribute_without_stagnation_history(self):
        # 1 jour de stagnation, 0 degre-jour cumule : ne reste que
        # surface (0.25 max) + dechets (0.15)
        p = engine.indice_palu(1, 0, 200, True)
        assert p == 0.40


class TestMalariaLevelThresholds:
    def test_vert_below_030(self):
        assert engine.malaria_level_from_index(0.29) == "vert"

    def test_jaune_boundary_inclusive_030(self):
        assert engine.malaria_level_from_index(0.30) == "jaune"

    def test_jaune_boundary_inclusive_060(self):
        assert engine.malaria_level_from_index(0.60) == "jaune"

    def test_rouge_above_060(self):
        assert engine.malaria_level_from_index(0.61) == "rouge"


class TestClassifier:
    def test_monte_sans_pluie_forces_d(self):
        assert engine.classifier(vitesse_vidange=5.0, vidange_reference=3.0,
                                  monte_sans_pluie=True, duree_jours=1) == "D"

    def test_duree_over_21_days_forces_d(self):
        assert engine.classifier(vitesse_vidange=5.0, vidange_reference=3.0,
                                  monte_sans_pluie=False, duree_jours=22) == "D"

    def test_no_drainage_is_c(self):
        assert engine.classifier(vitesse_vidange=0.1, vidange_reference=3.0,
                                  monte_sans_pluie=False, duree_jours=1) == "C"

    def test_slow_drainage_is_b(self):
        assert engine.classifier(vitesse_vidange=1.0, vidange_reference=3.0,
                                  monte_sans_pluie=False, duree_jours=1) == "B"

    def test_healthy_drainage_is_a(self):
        assert engine.classifier(vitesse_vidange=3.0, vidange_reference=3.0,
                                  monte_sans_pluie=False, duree_jours=1) == "A"

    def test_curage_utile_true_for_a_and_b(self):
        assert engine.curage_utile("A") is True
        assert engine.curage_utile("B") is True

    def test_curage_utile_false_for_c_and_d(self):
        assert engine.curage_utile("C") is False
        assert engine.curage_utile("D") is False


class TestCertificat:
    def test_matches_contract_example_p02(self):
        c = engine.certificat(1.8, 8.6)
        assert c == {
            "before_cmh": 1.8, "after_cmh": 8.6,
            "gain_pct": 378, "verdict": "CONFORME",
        }

    def test_exactly_100_percent_is_conforme(self):
        c = engine.certificat(2.0, 4.0)
        assert c["gain_pct"] == 100
        assert c["verdict"] == "CONFORME"

    def test_below_100_percent_is_non_conforme(self):
        c = engine.certificat(2.0, 3.5)
        assert c["gain_pct"] == 75
        assert c["verdict"] == "NON CONFORME"

    def test_before_zero_does_not_crash(self):
        c = engine.certificat(0.0, 5.0)
        assert c["verdict"] == "CONFORME"
