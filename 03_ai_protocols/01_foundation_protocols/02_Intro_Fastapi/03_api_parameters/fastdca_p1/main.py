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