from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(
    title="My Simple Item API",
    description="A basic API to manage items, demonstrating REST principles with FastAPI.",
    version="0.1.0"
)

# In-memory "database" for demonstration
items_db: dict[int, dict] = {}
next_item_id = 1

class ItemCreate(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

class ItemResponse(ItemCreate):
    id: int

@app.post("/items/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED, tags=["Items"])
async def create_item(item_in: ItemCreate) -> ItemResponse:
    """
    Create a new item.
    """
    global next_item_id
    new_item = ItemResponse(id=next_item_id, **item_in.model_dump())
    items_db[next_item_id] = new_item.model_dump() # Store as dict for simplicity
    next_item_id += 1
    return new_item

@app.get("/items/", response_model=list[ItemResponse], tags=["Items"])
async def read_items(skip: int = 0, limit: int = 10) -> list[ItemResponse]:
    """
    Retrieve a list of items with pagination.
    """
    all_items = [ItemResponse(**item_data) for item_data in items_db.values()]
    return all_items[skip : skip + limit]

@app.get("/items/{item_id}", response_model=ItemResponse, tags=["Items"])
async def read_item(item_id: int) -> ItemResponse:
    """
    Retrieve a specific item by its ID.
    """
    if item_id not in items_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return ItemResponse(**items_db[item_id])

@app.put("/items/{item_id}", response_model=ItemResponse, tags=["Items"])
async def update_item(item_id: int, item_in: ItemCreate) -> ItemResponse:
    """
    Update an existing item by its ID. Replaces the entire item.
    """
    if item_id not in items_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    updated_item = ItemResponse(id=item_id, **item_in.model_dump())
    items_db[item_id] = updated_item.model_dump()
    return updated_item

@app.delete("/items/{item_id}", response_model=ItemResponse, tags=["Items"])
async def delete_item(item_id: int) -> ItemResponse:
    """
    Delete an item by its ID.
    """
    if item_id not in items_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    deleted_item_data = items_db.pop(item_id)
    return ItemResponse(**deleted_item_data)
