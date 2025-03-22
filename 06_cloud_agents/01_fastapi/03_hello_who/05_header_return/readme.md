# Return the User-Agent header

FastAPI converts HTTP header keys to lowercase, and converts a hyphen (-) to an underscore (_). So you could print the value of the HTTP User-Agent header.

Start Uvicorn with the command line

    uvicorn hello:app --reload

Test with HTTPie

    http -v localhost:8000/agent

    http -v POST localhost:8000/agent