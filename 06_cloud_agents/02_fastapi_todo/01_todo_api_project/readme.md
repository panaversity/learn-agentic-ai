# Complete Todo REST API and App Project

Develop a todo REST API project using combination of FastAPI, Postgres SQL Database, and SQLAlchemy in Python using layered architecture. Add API endpoints for todo CRUD operations (POST, PUT, DELETE. Also develop Streamlit client and a Python console client and a Typescript Node.js console client. Also add unit tests using pytest.

The API should multi-tenant meaning multiple users can use this APIs, therefore every user todo will be saved with a user ID, and [JWT authentication](https://www.freecodecamp.org/news/how-to-add-jwt-authentication-in-fastapi/) also need to be implemented. 

Also develop a Next.js version of the Project where FastAPI which will also be deployed on Vercel. You may use [Next.js FastAPI Starter](https://vercel.com/templates/next.js/nextjs-fastapi-starter). 

You may use [Neon Postgres compatiable database](https://neon.tech/) as your Database. You can also use [any other Postgres Cloud Database](https://www.yugabyte.com/postgresql/compare-postgresql-compatibility/). 

Share your deployed Streamlit and Next.js projects with everyone. 

# The Project

 We will guide you through creating a simplified version of this project and provide code snippets for each component.

 Modify and enhance the code for handling error cases, authentication, input validation, and other security considerations.

 Note this code is only to get you started only, and is neither multi-tanent nor implements layered architecture. It also doesnot implement JWT authentication. You will have to add all these things and more.

Firstly, ensure you have the necessary packages installed:
- FastAPI
- SQLAlchemy
- PostgresSQL
- Streamlit
- psycopg2
- requests (for Python console client)
- Axios (for Typescript Node.js console client)

Let's break down the steps:

### 1. Set up the PostgreSQL Database and SQLAlchemy Models
```python
# database.py

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://username:password@localhost/dbname"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
```

### 2. Create FastAPI CRUD Endpoints
```python
# main.py

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Todo

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/todos/")
def create_todo(todo: Todo, db: Session = Depends(get_db)):
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo

@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, updated_todo: Todo, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    for key, value in updated_todo.dict().items():
        setattr(db_todo, key, value)
    db.commit()
    return db_todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(db_todo)
    db.commit()
    return {"message": "Todo deleted"}
```

### 3. Implement Streamlit Client
```python
# streamlit_client.py

import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

st.title("Todo App")

def create_todo():
    title = st.text_input("Enter Todo Title")
    description = st.text_area("Enter Todo Description")
    if st.button("Add Todo"):
        response = requests.post(f"{BASE_URL}/todos/", json={"title": title, "description": description})
        if response.status_code == 200:
            st.success("Todo added successfully")

def delete_todo():
    todo_id = st.number_input("Enter Todo ID to delete")
    if st.button("Delete Todo"):
        response = requests.delete(f"{BASE_URL}/todos/{todo_id}")
        if response.status_code == 200:
            st.success("Todo deleted successfully")

if __name__ == "__main__":
    create_todo()
    delete_todo()
```

### 4. Python Console Client
```python
# python_console_client.py

import requests

BASE_URL = "http://127.0.0.1:8000"

def create_todo():
    title = input("Enter Todo Title: ")
    description = input("Enter Todo Description: ")
    response = requests.post(f"{BASE_URL}/todos/", json={"title": title, "description": description})
    if response.status_code == 200:
        print("Todo added successfully")

def delete_todo():
    todo_id = input("Enter Todo ID to delete: ")
    response = requests.delete(f"{BASE_URL}/todos/{todo_id}")
    if response.status_code == 200:
        print("Todo deleted successfully")

if __name__ == "__main__":
    create_todo()
    delete_todo()
```

### 5. TypeScript Node.js Console Client
```typescript
// nodejs_console_client.ts

import axios from 'axios';

const BASE_URL = "http://127.0.0.1:8000";

async function createTodo() {
    const title = 'Sample Title';
    const description = 'Sample Description';
    try {
        const response = await axios.post(`${BASE_URL}/todos/`, { title, description });
        console.log("Todo added successfully");
    } catch (error) {
        console.error("Error:", error.message);
    }
}

async function deleteTodo() {
    const todoId = 1; // Replace with the desired Todo ID
    try {
        const response = await axios.delete(`${BASE_URL}/todos/${todoId}`);
        console.log("Todo deleted successfully");
    } catch (error) {
        console.error("Error:", error.message);
    }
}

createTodo();
deleteTodo();
```

### 6. Unit Tests using Pytest
Create tests for the FastAPI endpoints and their functionality.

```python
# test_api.py

from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)

def test_create_todo():
    response = client.post("/todos/", json={"title": "Test Todo", "description": "Test Description"})
    assert response.status_code == 200
    assert response.json()["title"] == "Test Todo"

def test_update_todo():
    response = client.put("/todos/1", json={"title": "Updated Todo", "description": "Updated Description"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Todo"

def test_delete_todo():
    response = client.delete("/todos/1")
    assert response.status_code == 200
    assert response.json()["message"] == "Todo deleted"
```

To run the entire setup, you'll need to:

- Set up a PostgreSQL database.
- Run the FastAPI application using `uvicorn main:app --reload`.
- Run the Streamlit client using `streamlit run streamlit_client.py`.
- Run the Python console client using `python python_console_client.py`.
- Run the TypeScript Node.js console client after transpiling using a TypeScript compiler.

Note: Review the Open API Specifications generated by FastAPI.

