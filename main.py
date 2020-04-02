from fastapi import FastAPI, Request

from pydantic import BaseModel

app = FastAPI()
app.counter = 0

class HelloResp(BaseModel):
    msg: str

class Patient(BaseModel):
    name: str
    surname: str

#-------------------------------------------------- 

@app.get('/')
def hello_world():
    return {"message": "Hello World during the coronavirus pandemic!"}

#---------- Homework 1 Problem 1

@app.get('/hello/{name}', response_model=HelloResp)
def read_item(name: str):
    return HelloResp(msg=f"Hello {name}")

#---------- Homework 1 Problem 2

@app.get('/method')
def read_method(request: Request):
    used_method = request.method
    return {'method': used_method}

@app.post('/method')
def read_method(request: Request):
    used_method = request.method
    return {'method': used_method}

@app.put('/method')
def read_method(request: Request):
    used_method = request.method
    return {'method': used_method}

#---------- Homework 1 Problem 3

@app.post('/patient', response_model = Patient)
def get_patient(patient: Patient):
    app.counter +=1
    return {'id': app.counter, 'patient': patient} 
