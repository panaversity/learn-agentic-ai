# Hello FastAPI

[Read Pages 27-32 FastAPI Textbook](https://www.amazon.com/FastAPI-Bill-Lubanovic-ebook/dp/B0CLKZJSGV/ref=sr_1_1)

Start Uvicorn with the command line:
    
    uvicorn hello:app --reload

Open in Browser:

    http://127.0.0.1:8000/hi

Test with requests:

    python test_requests.py

Test with HTTPie (pronounced aitch-tee-tee-pie):

    http localhost:8000/hi

Test with HTTPie, printing only the response body:

    http -b localhost:8000/hi

Test with HTTPie and get everything:

    http -v localhost:8000/hi

