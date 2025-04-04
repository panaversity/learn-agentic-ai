# Steps
1. `poetry new heroapi_uit`
2. `cd heroapi_uit`
3. `poetry add fastapi sqlmodel "uvicorn[standard]"`

4. create a new "main.py" file in child package folder 
```
from fastapi import FastAPI

app : FastAPI = FastAPI()

@app.get("/")
def root():
    return {"Hello": "world"}
```
    * `poetry run uvicorn heroapi_uit.main:app --reload`

5. write test in test folder 
```
from fastapi.testclient import TestClient
from heroapi_uit.main import app

def test_root_path():
    client = TestClient(app=app)
    response = client.get('/')
    assert response.status_code == 200
```

6. `poetry run pytest -v`
