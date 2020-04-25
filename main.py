from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()
app.counter = 0
#global patients
patients = []


class HelloResp(BaseModel):
    msg: str

class Patient(BaseModel):
    name: str
    surename: str


class PatientID(BaseModel):
    id: int
    patient: Patient 


@app.get('/hello/{name}', response_model=HelloResp)
def read_item(name: str):
    return HelloResp(msg=f"Hello {name}")

@app.get('/')
def hello_world():
    return {"message": "Hello World during the coronavirus pandemic!"}

@app.get('/welcome')
def welcome():
    return {"message": "Welcome user"}

@app.get('/method')
def read_method(request: Request):
    return {'method': request.method}


@app.post('/method')
def read_method(request: Request):
    return {'method': request.method}


@app.put('/method')
def read_method(request: Request):
    return {'method': request.method}


@app.post('/patient', response_model=PatientID)
def add_patient(request: Patient):
    global patients
    p = PatientID(id = app.counter, patient = request)
    app.counter+=1
    patients.append(p)
    return p

@app.get('/patient/{pk}')
def read_patient(pk: int):
    global patients
    if pk not in [i.id for i in patients]:
       return JSONResponse(status_code = 204, content = {}) 
    return patients[pk].patient
