from fastapi import FastAPI, Depends 
from typing import Annotated

def depfunc1(num:int): 
    num = int(num)
    num += 1
    return num

def depfunc2(num): 
    num = int(num)
    num += 1
    return num

app = FastAPI(dependencies=[Depends(depfunc1), Depends(depfunc2)])

@app.get("/main/{num}")
def get_main(num: int, num1:  Annotated[int,Depends(depfunc1)], num2: Annotated[int,Depends(depfunc2)]):
    # Assuming you want to use num1 and num2 in some way
    #       1      2      2
    total = num + num1 + num2
    return f"Pakistan {total}"
