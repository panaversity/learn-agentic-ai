# https://www.youtube.com/watch?v=0c4NFdpu2vY&t=69s

from fastapi import FastAPI, Depends, HTTPException, status
from typing import Annotated

blogs = {
    "1": "Generative AI Blog",
    "2": "Machine Learning Blog",
    "3": "Deep Learning Blog"
}

users = {
    "8": "Ahmed",
    "9": "Mohammed"
}

def get_blog_or_404(id: str):
    name = blogs.get(id)
    if not name:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog ID {id} not found")
    return name

app = FastAPI(title="Learn Dependency Injection")

@app.get("/blog/{id}")
def get_blog(blog_name: Annotated[str, Depends(get_blog_or_404)]):
    return blog_name