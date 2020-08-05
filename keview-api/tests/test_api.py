import os
import pytest
import requests
from requests.adapters import HTTPAdapter
HOST = os.getenv("KEVIEW_HOST", "http://127.0.0.1")
PORT = 8000
ENDPOINT = "keview/v1alpha"
API_URL = f"{HOST}:{PORT}/{ENDPOINT}"


@pytest.fixture(scope="session", autouse=True)
def do_something(request):
    session = requests.Session()
    session.mount('http://', HTTPAdapter(max_retries=10))
    session.get(f"{HOST}:{PORT}/docs", timeout=5)


def test_get_layers():
    res = requests.get(f"{API_URL}/layers")
    assert res.status_code == 200


def test_get_layer():
    for layer_id in range(0, 9):
        res = requests.get(f"{API_URL}/layers/{layer_id}")
        assert res.status_code == 200


def test_get_components():
    for layer_id in range(0, 9):
        res = requests.get(f"{API_URL}/layers/{layer_id}/components")
        assert res.status_code == 200

        res = requests.get(f"{API_URL}/layers/{layer_id}/components/0")
        if layer_id == 6:
            assert res.status_code == 404
        else:
            assert res.status_code == 200


def test_get_outputs():
    for layer_id in range(0, 9):
        res = requests.get(f"{API_URL}/layers/{layer_id}/outputs")
        assert res.status_code == 200


def test_display_layer():
    for layer_id in range(0, 9):
        res = requests.get(f"{API_URL}/layers/{layer_id}/display")
        assert res.status_code == 200
