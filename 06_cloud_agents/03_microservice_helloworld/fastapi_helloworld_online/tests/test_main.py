from fastapi.testclient import TestClient
from fastapi_helloworld_online.main import app


def test_root_path():
    client = TestClient(app=app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "world"}

def test_piaic_description():
    client = TestClient(app=app)
    response = client.get("/piaic/")
    assert response.status_code == 200
    assert response.json() == {"organization": "piaic"}

def test_third_check():
    client = TestClient(app=app)
    response = client.get("/piaic/")
    assert response.status_code == 200
    assert response.json() == {"organization": "ABC"}


