# Synchronous Inter Services Messages between Microservices

[Building Microservices: Inter-Process Communication in a Microservices Architecture](https://www.nginx.com/blog/building-microservices-inter-process-communication/)

There are two main approaches to inter-service communication in a microservices architecture:

1. **Synchronous Communication:** This method involves a direct call between services, typically using an API exposed by one service that another service can interact with. Protocols like HTTP are commonly used for this purpose. The calling service waits for a response from the other service before proceeding.

2. **Asynchronous Messaging:** In this approach, services don't directly call each other. Instead, they send messages to a queue or message broker. The receiving service then processes the message independently. This allows for looser coupling between services and improved scalability. Message brokers like Kafka or RabbitMQ are popular choices for asynchronous communication.

Both synchronous and asynchronous communication have their advantages and disadvantages:

* **Synchronous communication** is simpler to implement and easier to debug, but it can lead to tight coupling between services and performance bottlenecks if not designed carefully.

* **Asynchronous communication** offers better scalability and looser coupling, but it can be more complex to implement and reason about.

The best choice for your microservices communication will depend on the specific needs of your application. Consider factors like latency requirements, message volume, and desired level of coupling between services when making your decision.

## Synchronous Communication with FastAPI, Docker, and Poetry

https://g.co/gemini/share/3a129f9e5743 

This example demonstrates synchronous communication between two Python microservices built with FastAPI, using SQLModel for database access. Both services will be containerized using Docker and orchestrated with Docker Compose. Poetry will manage dependencies.

**Microservice 1: user-service**

**1. Dependencies:**

```bash
poetry add fastapi uvicorn sqlmodel[postgresql] pydantic[postgresql] docker python-docker
```

**2. Database Model (user.py):**

```python
from sqlmodel import Field, SQLModel

class User(SQLModel):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
```

**3. User Service (user_service.py):**

```python
from fastapi import FastAPI, Body
from pydantic import BaseModel
from user import User

app = FastAPI()

# Database connection (replace with your connection details)
engine = create_engine("postgresql://user:password@host:port/database")
User.create_table(engine)


class UserResponse(BaseModel):
    id: int
    name: str


@app.post("/users")
async def create_user(user: UserResponse = Body(...)):
    new_user = User(name=user.name)
    with Session(engine) as session:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
    return new_user


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    with Session(engine) as session:
        user = session.query(User).filter(User.id == user_id).first()
    if user:
        return UserResponse(id=user.id, name=user.name)
    else:
        return {"message": "User not found"}

```

**4. Dockerfile (user-service/Dockerfile):**

```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "user_service:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Microservice 2: order-service**

**1. Dependencies:**

```bash
poetry add fastapi uvicorn requests docker python-docker
```

**2. Order Model (order.py):**

```python
from pydantic import BaseModel

class Order(BaseModel):
    user_id: int
    item_name: str
```

**3. Order Service (order_service.py):**

```python
from fastapi import FastAPI, Body
from requests import get

app = FastAPI()


class OrderResponse(BaseModel):
    id: int  # Placeholder for future implementation with database
    user_id: int
    item_name: str
    username: str  # Retrieved from user-service


@app.post("/orders")
async def create_order(order: Order = Body(...)):
    # Call user service to get username
    user_response = get(f"http://user-service:8000/users/{order.user_id}")
    if user_response.status_code == 200:
        user_data = user_response.json()
        username = user_data["name"]
    else:
        return {"message": "User not found"}

    new_order = Order(user_id=order.user_id, item_name=order.item_name, username=username)
    # Implement logic to store order (replace with database interaction)
    print(f"Order created for user {username} (ID: {order.user_id}) - Item: {order.item_name}")
    return new_order

```

**4. Dockerfile (order-service/Dockerfile):**

```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "order_service:app", "--host", "0.0.0.0", "--port", "8001"]
```

**5. docker-compose.yml:**

```yaml
version: "3.8"

services:
  user-service:
    build: user-service
    ports:
      -