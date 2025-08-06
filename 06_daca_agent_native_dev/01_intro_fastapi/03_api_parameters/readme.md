# Step 3: API Parameters

This step focuses on the different ways to receive and validate parameters in your FastAPI application. We'll cover path parameters, query parameters, and request bodies with enhanced validation using FastAPI's built-in functionality.

## Types of Parameters in FastAPI

FastAPI provides several ways to declare and validate parameters:

1. **Path Parameters**: Parts of the URL path that are variable (e.g., `/items/{item_id}`)
2. **Query Parameters**: Parameters appended to the URL after a `?` (e.g., `/items?skip=0&limit=10`)
3. **Request Body**: Data sent in the body of the request (usually in JSON format)
4. **Headers**: Custom HTTP headers sent with the request
5. **Cookies**: Data sent in the Cookie header
6. **Form Data**: Fields submitted in a form
7. **File Uploads**: Files uploaded in a form

In this step, we'll focus on the first two types and how to add validation to them. Take the code from last step and update it with following examples or quickly setup

```bash
uv init fastdca_p1
cd fastdca_p1
uv venv
source .venv/bin/activate
uv add "fastapi[standard]"
```

## Enhanced Path Parameter Validation

FastAPI offers the `Path()` function to add constraints and metadata to path parameters:

Update main.py

```python
from fastapi import FastAPI, Path

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(
    item_id: int = Path(
        ...,  # ... means the parameter is required
        title="The ID of the item",
        description="A unique identifier for the item",
        ge=1  # greater than or equal to 1
    )
):
    return {"item_id": item_id}
```

Run the server and try it out in docs:

```bash
fastapi dev main.py
```

## Enhanced Query Parameter Validation

Similarly, the `Query()` function adds validation to query parameters:

Add a new route:

```python
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/items/")
async def read_items(
    q: str | None = Query(
        None,  # Default value is None (optional parameter)
        title="Query string",
        description="Query string for searching items",
        min_length=3,
        max_length=50
    ),
    skip: int = Query(0, ge=0),  # Greater than or equal to 0
    limit: int = Query(10, le=100)  # Less than or equal to 100
):
    return {"q": q, "skip": skip, "limit": limit}
```

## Using Multiple Parameters Together

You can combine different types of parameters in a single endpoint:

```python
from fastapi import FastAPI, Path, Query, Body
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float

app = FastAPI()

@app.put("/items/validated/{item_id}")
async def update_item(
    item_id: int = Path(..., title="Item ID", ge=1),
    q: str | None = Query(None, min_length=3),
    item: Item | None = Body(None, description="Optional item data (JSON body)")
):
    result = {"item_id": item_id}
    if q:
        result.update({"q": q})
    if item:
        result.update({"item": item.model_dump()})
    return result
```

## Complete Example: main.py

Here's the complete code with various parameter types and validations.

```python
from fastapi import FastAPI, Path, Query, Body, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float

@app.get("/items/{item_id}")
async def read_item(
    item_id: int = Path(
        ...,  # ... means the parameter is required
        title="The ID of the item",
        description="A unique identifier for the item",
        ge=1  # greater than or equal to 1
    )
):
    return {"item_id": item_id}

@app.get("/items/")
async def read_items(
    q: str | None = Query(
        None,  # Default value is None (optional parameter)
        title="Query string",
        description="Query string for searching items",
        min_length=3,
        max_length=50
    ),
    skip: int = Query(0, ge=0),  # Greater than or equal to 0
    limit: int = Query(10, le=100)  # Less than or equal to 100
):
    return {"q": q, "skip": skip, "limit": limit}


@app.put("/items/validated/{item_id}")
async def update_item(
    item_id: int = Path(..., title="Item ID", ge=1),
    q: str | None = Query(None, min_length=3),
    item: Item | None = Body(None, description="Optional item data (JSON body)")
):
    result = {"item_id": item_id}
    if q:
        result.update({"q": q})
    if item:
        result.update({"item": item.model_dump()})
    return result
```

## Running the Application

1. Save the above code as `main.py` in the `03_api_parameters` directory.
2. Install the required dependencies:
   ```bash
   uv add "fastapi[standard]"
   ```
3. Run the FastAPI application:
   ```bash
   fastapi dev main.py
   ```
4. Open the interactive documentation at `http://localhost:8000/docs` to explore and test the endpoints.

## Key Points to Remember

- Use `Path()` for validating path parameters
- Use `Query()` for validating query parameters
- Both `Path()` and `Query()` support various validation options:
  - `ge`, `gt`, `le`, `lt` for numerical constraints
  - `min_length`, `max_length` for string length
  - `regex` or `pattern` for pattern matching
  - `enum` for restricting to a set of values
- FastAPI will automatically validate all parameters according to your specifications
- When validation fails, FastAPI returns a 422 Unprocessable Entity status code with detailed error information

---

In the next step, we'll learn about dependency injection in FastAPI, which enables more modular and reusable code.