# Hello world with Fastapi
1. `poetry new fastapi_helloworld_online`
2. `cd fastapi_helloworld_online`
3. Select your project with VScode
4. open file `pyproject.toml`
```
[tool.poetry]
name = "fastapi-helloworld-online"
version = "0.1.0"
description = ""
authors = ["Sir Qasim <m.qasim077@gmail.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.11"


[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```
5. install new packages in poetry project
    `poetry add fastapi "uivcorn[standard]"`
    ```
    [tool.poetry.dependencies]
    python = "^3.11"
    fastapi = "^0.110.0"
    uvicorn = {extras = ["standard"], version = "^0.29.0"}
    ```

5. create `main.py` location `fastapi_helloworld_online/main.py`
```
from fastapi import FastAPI


app  = FastAPI()

@app.get("/")
def index():
    return {"Hello": "world"}

@app.get("/piaic/")
def piaic():
    return {"organization": "piaic"}

```
6. run server
    `poetry run uvicorn fastapi_helloworld_online.main:app --reload`

7. `http://127.0.0.1:8000/`
    * `http://127.0.0.1:8000/piaic/`
8. `http://127.0.0.1:8000/docs`

9. write your own test
    * `test/test_main.py`
    ```
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



    ```

    10. `poetry run test -v`
