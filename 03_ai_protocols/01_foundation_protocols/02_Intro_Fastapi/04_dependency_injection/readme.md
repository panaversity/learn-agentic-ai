# Step 4: Dependency Injection

In this step, you'll learn about **Dependency Injection** in FastAPI. Dependency Injection is a way to share reusable code (like checking user permissions or connecting to a database) across your API endpoints. FastAPI makes it easy to create and use dependencies, keeping your code clean and organized.

Reference:
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Classes as Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/classes-as-dependencies/)
- [Sub-Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/sub-dependencies/)
- [Dependencies in Path Operation Decorators](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-in-path-operation-decorators/)

## Why Use Dependency Injection?

-   **Code Reusability:** Define common logic or resources once and reuse them across multiple endpoints (e.g., fetching the current user).
-   **Separation of Concerns:** Keep your endpoint logic focused on the specific task, delegating common tasks (like authentication or fetching shared data) to dependencies.
-   **Testability:** Easily replace dependencies with mock objects during testing.
-   **Organization:** Structure your application logic cleanly.

## How It Works

1.  **Define a Dependency:** Create a function (or a class with `__call__`) that performs the necessary setup or provides the required resource. This function can itself have parameters (which FastAPI will also resolve, potentially including other dependencies).
2.  **"Depend" on It:** Add a parameter to your path operation function, type-hinted with the return type of the dependency function, and use `Depends(your_dependency_function)` as the default value. Use `typing.Annotated` for cleaner syntax.

FastAPI will execute the dependency function for each request that requires it and pass the result to your endpoint function. FastAPI also caches the result within the same request, so if multiple parts of your request handling depend on the same dependency function, it's only executed once per request.

## Setup

If continuing from Step 3, ensure you're in the `03_api_parameters` directory, or create a new project:

```bash
uv init fastdca_p1
cd fastdca_p1
uv venv
source .venv/bin/activate
uv add "fastapi[standard]"
```

## Learning Plan

We’ll learn Dependency Injection through four simple examples:
1. **Check a Secret Key**: Use a dependency to check a header (like a password) for secure endpoints.
2. **Common Query Parameters**: Share query parameters (like search terms) across endpoints.
3. **Simulate a Database**: Use a class as a dependency to act like a database.
4. **Sub-Dependencies**: Create a dependency that uses another dependency (like checking two headers).

### 1. Hello Dependency

```python
def get_simple_goal():
    return {"goal": "We are building AI Agents Workforce"}
    
@app.get("/get-simple-goal")
def simple_goal(response :  Annotated[dict, Depends(get_simple_goal)]):
    return response
```

### 2. Dependency with Parameter

We can even pass function parameters in Dep.

```python
# depency function
def get_goal(username: str):
    return {"goal": "We are building AI Agents Workforce", "username": username}
    
@app.get("/get-goal")
def get_my_goal(response :  Annotated[dict, Depends(get_goal)]):
    return response
```

### 3. Dependency with Query Parameters

Check a Secret Key

```python
from fastapi import FastAPI, Depends, Query
from typing import Annotated

app : FastAPI = FastAPI()

# depency function
def dep_login(username : str = Query(None), password : str = Query(None)):
    if username == "admin" and password == "admin":
        return {"message" : "Login Successful"}
    else:
        return {"message" : "Login Failed"}
    
@app.get("/signin")
def login_api(user :  Annotated[dict,Depends(dep_login)]):
    return user
```

### 4. Multiple Dependencies

```python
def depfunc1(num:int): 
    num = int(num)
    num += 1
    return num

def depfunc2(num): 
    num = int(num)
    num += 2
    return num

@app.get("/main/{num}")
def get_main(num: int, num1:  Annotated[int,Depends(depfunc1)], num2: Annotated[int,Depends(depfunc2)]):
    # Assuming you want to use num1 and num2 in some way
    #       1      2      3
    total = num + num1 + num2
    return f"Pakistan {total}"
```

### 5. CLASSES  

```python
blogs = {
    "1": "Generative AI Blog",
    "2": "Machine Learning Blog",
    "3": "Deep Learning Blog"
}

users = {
    "8": "Ahmed",
    "9": "Mohammed"
}

class GetObjectOr404():
    def __init__(self, model)->None:
        self.model = model

    def __call__(self, id: str):
        obj = self.model.get(id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Object ID {id} not found")
        return obj

blog_dependency = GetObjectOr404(blogs)

@app.get("/blog/{id}")
def get_blog(blog_name: Annotated[str, Depends(blog_dependency)]):
    return blog_name

user_dependency = GetObjectOr404(users)

@app.get("/user/{id}")
def get_user(user_name: Annotated[str, Depends(user_dependency)]):
    return user_name
```
