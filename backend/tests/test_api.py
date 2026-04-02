from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import create_app
from app.services.external_planet_source import WikipediaPlanetSource


def build_client() -> TestClient:
    get_settings.cache_clear()
    app = create_app()
    app.dependency_overrides = {}
    return TestClient(app)


def test_healthcheck(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("AUTO_SYNC_ON_STARTUP", "false")
    with build_client() as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_planets(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("AUTO_SYNC_ON_STARTUP", "false")
    with build_client() as client:
        response = client.get("/planets")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 11
    assert payload["items"][0]["name"] == "Mercurio"
    assert (tmp_path / "data" / "planets.db").exists()


def test_list_exoplanets(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("AUTO_SYNC_ON_STARTUP", "false")
    with build_client() as client:
        response = client.get("/planets", params={"category": "exoplanets"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 3
    assert payload["items"][0]["category"] == "exoplanets"


def test_list_planets_rejects_invalid_category(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("AUTO_SYNC_ON_STARTUP", "false")
    with build_client() as client:
        response = client.get("/planets", params={"category": "invalid"})

    assert response.status_code == 422


def test_get_planet_detail(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("AUTO_SYNC_ON_STARTUP", "false")
    with build_client() as client:
        response = client.get("/planets/3")

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "Tierra"
    assert payload["moons"] == 1


def test_get_missing_planet(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("AUTO_SYNC_ON_STARTUP", "false")
    with build_client() as client:
        response = client.get("/planets/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Planet not found"


def test_admin_overview(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("AUTO_SYNC_ON_STARTUP", "false")
    with build_client() as client:
        response = client.get("/admin/overview")

    assert response.status_code == 200
    payload = response.json()
    assert payload["runtime"]["planet_total"] == 11
    assert payload["sync"]["source_name"] == "Wikipedia REST ES"
    assert payload["sync"]["last_status"] == "never"


def test_manual_sync(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("AUTO_SYNC_ON_STARTUP", "false")

    def fake_fetch(self, wikipedia_title: str):
        return {
            "source_summary": f"Resumen de {wikipedia_title}",
            "source_description": "planeta sincronizado desde fuente externa",
            "source_page_url": f"https://example.test/{wikipedia_title}",
            "image_url": "https://example.test/image.png",
            "last_synced_at": "2026-04-02T18:00:00+00:00",
        }

    monkeypatch.setattr(WikipediaPlanetSource, "fetch_planet_details", fake_fetch)

    with build_client() as client:
        response = client.post("/admin/sync")

    assert response.status_code == 200
    payload = response.json()
    assert payload["sync"]["last_status"] == "success"
    assert payload["sync"]["records_processed"] == 11
    assert payload["runtime"]["serving_from_cache"] is False