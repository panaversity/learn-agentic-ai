# Query Parameters

Query parameters are the name=value strings after the ? in a URL, separated by & characters.

Start Uvicorn with the command line

    uvicorn hello:app --reload

Test in the browser
    
    localhost:8000/hi?who=Mom

Test with HTTPie

    http -b localhost:8000/hi?who=Mom

Test with Requests

    python test_query_param.py