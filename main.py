from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel

import json

app = FastAPI()
app.counter =-1 
patients = []

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
    id: int
    patient: dict

@app.post('/patient', response_model = PatientID)
def add_patient(request: Patient):
    app.counter+=1
    patients.append(PatientID(id=app.counter, patient=request.dict()))
    return PatientID(id=app.counter, patient=request.dict())

#---------- Homework 1 Problem 4

@app.get('/patient/{no}')
def read_patient(no: int):
    if no not in [i.id for i in patients]:
        raise HTTPException(status_code=204, detail="Patient not found")
    return patients[no-1].patient
