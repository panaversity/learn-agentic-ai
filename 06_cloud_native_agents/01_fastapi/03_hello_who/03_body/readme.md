# Body

The request body is used to send stuff to the server when creating (POST) or updating (PUT or PATCH).

Note:

That Body(embed=True) is needed to tell FastAPI that, this time, we get the value of who from the JSON-formatted request body. The embed part means that it should look like {"who": "Mom"} rather than just "Mom".

Start Uvicorn with the command line

    uvicorn hello:app --reload

Test with HTTPie

    http -v localhost:8000/hi who=Mom

Test with Requests

    python test_body.py

### Automated Documentation: Open in browser:

    http://localhost:8000/docs