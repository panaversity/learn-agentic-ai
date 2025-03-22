# URL Path

Start Uvicorn with the command line

    uvicorn hello:app --reload

Test /hi/Mom in the browser
    
    localhost:8000/hi/Mom

Test /hi/Mom with HTTPie

    http localhost:8000/hi/Mom

Test /hi/Mom with Requests

    python test_url_path.py