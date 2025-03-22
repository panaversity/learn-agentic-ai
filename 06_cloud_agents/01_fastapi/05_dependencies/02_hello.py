from fastapi import FastAPI, Depends, Query


app : FastAPI = FastAPI()

def dep_check(name:str = Query(None), password:str = Query(None)):
    if not name:
        raise

    
@app.get("/login", dependencies=[Depends(dep_check)])
def login():
    return True