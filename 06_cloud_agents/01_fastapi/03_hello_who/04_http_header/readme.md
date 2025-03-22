# Header

Passing the greeting argument as an HTTP header

Start Uvicorn with the command line

    uvicorn hello:app --reload

Test with HTTPie

    http -v localhost:8000/hi who:Mom
