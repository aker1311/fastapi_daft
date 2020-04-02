from fastapi import FastAPI, Request

from pydantic import BaseModel

app = FastAPI()
app.counter = 0

class HelloResp(BaseModel):
    msg: str

@app.get('/hello/{name}', response_model=HelloResp)
def read_item(name: str):
    return HelloResp(msg=f"Hello {name}")

#-------------------------------------------------- 

#---------- Homework 1 Problem 1
@app.get('/')
def hello_world():
    return {"message": "Hello World during the coronavirus pandemic!"}

#---------- Homework 1 Problem 2

@app.get('/method')
def read_method(request: Request):
    return {'method': request.method}

@app.post('/method')
def read_method(request: Request):
    return {'method': request.method}

@app.put('/method')
def read_method(request: Request):
    return {'method': request.method}
    
#---------- Homework 1 Problem 3

class Patient(BaseModel):
    name: str 
    surname: str

class PatientID(BaseModel):
    app.counter+=1
    id: int
    patient: dict

@app.post('/patient', response_model = PatientID)
def get_patient(request: Patient):
#    app.counter+=1
    return PatientID(id=app.counter, patient=request.dict())

#---------- Homework 1 Problem 4

#@app.get('/patient/{id}', response_model = Patient