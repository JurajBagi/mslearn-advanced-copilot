from main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200


def test_countries():
    response = client.get("/countries")
    assert response.status_code == 200
    assert sorted(response.json()) == ["England", "France", "Germany", "Italy", "Peru", "Portugal", "Spain"]


def test_cities_by_country_lists_city_names():
    response = client.get("/countries/Portugal")
    assert response.status_code == 200

    body = response.json()
    assert body["country"] == "Portugal"
    assert sorted(body["cities"]) == ["Lisbon", "Porto"]


def test_cities_by_country_month_returns_high_low_by_city():
    response = client.get("/countries/Portugal", params={"month": "January"})
    assert response.status_code == 200

    body = response.json()
    assert body["country"] == "Portugal"
    assert body["month"] == "January"

    assert body["cities"]["Lisbon"] == {"high": 57, "low": 46}
    assert body["cities"]["Porto"] == {"high": 57, "low": 45}