from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from fastapi import FastAPI, Depends
from typing import Annotated

DB_URL = "Add Postgress Database URL"

# Enable connection pooling with pessimistic testing
engine = create_engine(DB_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for getting the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print(f"Exception occurred: {e}")
    finally:
        db.close()

app = FastAPI()

@app.get("/hello")
def add_data(db: Annotated[Session, Depends(get_db)]):

    # Now you can use db as a session object to query the database and do other operations
    # i.e: db.query(User).filter(User.name == "test").first() where User is a SQLAlchemy ORM model

    return {"message": "Hello from FastAPI with SQLAlchemy DB Injection"}