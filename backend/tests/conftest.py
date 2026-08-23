import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from fastapi.testclient import TestClient

import storage
import weather
from main import app


@pytest.fixture(autouse=True)
def reset_state(monkeypatch):
    """Chaque test part d'un etat propre et sans appel reseau reel.

    pluie_24h_mm est neutralisee par defaut (0.0) : un test qui a besoin
    d'une valeur de pluie precise doit la re-patcher lui-meme.
    """
    monkeypatch.setattr(weather, "pluie_24h_mm", lambda lat, lng, point_id: 0.0)
    storage.STATE.reset()
    yield


@pytest.fixture
def client():
    return TestClient(app)
