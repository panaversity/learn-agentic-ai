# Example 01 old way with helper function
# from fastapi import FastAPI, Depends, Query

# app : FastAPI = FastAPI()

# def login(username : str , password : str ):
#     if username == "admin" and password == "admin":
#         return {"message" : "Login Successful"}
#     else:
#         return {"message" : "Login Failed"}
    

# @app.get("/login")
# def login_api(user,password):
#     result = login(user,password) # custom calling
#     return result
# Example 02 new way with Dependencies injection
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