from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from pydantic import BaseModel

from hashlib import sha256

import secrets

app = FastAPI()
security = HTTPBasic()

app.counter = 0
app.secret_key = '432A462D4A614E645267556B58703273357538782F413F4428472B4B62506553'
patients = []
app.sessions = []


class HelloResp(BaseModel):
    msg: str

class Patient(BaseModel):
    name: str
    surename: str

class PatientID(BaseModel):
    id: int
    patient: Patient

class User(BaseModel):
    login: str
    password: str

# ------------------------------------------------------

def get_current_user(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    user, passw = credentials.username, credentials.password
    correct_username = secrets.compare_digest(user, "trudnY")
    correct_password = secrets.compare_digest(passw, "PaC13Nt")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    else:
        session_token = sha256(bytes(f"{user}{passw}{app.secret_key}", encoding = 'utf8')).hexdigest()
        if not (session_token in app.sessions):
            app.sessions.append(session_token)
        return session_token 


def check(cookie: str = Cookie(None)):
    if not (cookie in app.sessions):
        cookie = None
    return cookie

# ------------------------------------------------------  

@app.post('/login')
def login(response: Response, cookie: str = Depends(get_current_user)):
    response.set_cookie(key = 'cookie', value = cookie)
    return RedirectResponse(url='/welcome') 

@app.post('/logout')
def logout(response: Response, cookie: str = Depends(check)):
    if cookie is None:
        return "ERROR KURWA"
    app.sessions = []
    return RedirectResponse(url='/') 

@app.post('/')
@app.get('/')
def hello_world(cookie: str = Depends(check)):
    if cookie not in app.sessions:
        raise HTTPException(status_code=403, detail="Unathorised")
    return {"message": "Hello World during the coronavirus pandemic!"}

@app.post('/welcome')
@app.get('/welcome')
def welcome():
    if cookie not in app.sessions:
        raise HTTPException(status_code=403, detail="Unathorised")
    return {"message": "Welcome user"}


@app.get('/hello/{name}', response_model=HelloResp)
def read_item(name: str, cookie: str = Depends(check)):
    if cookie not in app.sessions:
        raise HTTPException(status_code=403, detail="Unathorised")
    return HelloResp(msg=f"Hello {name}")


@app.post('/patient', response_model=PatientID)
def add_patient(request: Patient, cookie: str = Depends(check)):
    if cookie not in app.sessions:
        raise HTTPException(status_code=403, detail="Unathorised")
    global patients
    p = PatientID(id = app.counter, patient = request)
    app.counter+=1
    patients.append(p)
    return p


@app.get('/patient/{pk}')
def read_patient(pk: int, cookie: str = Depends(check)):
    if cookie not in app.sessions:
        raise HTTPException(status_code=403, detail="Unathorised")
    global patients
    if pk not in [i.id for i in patients]:
       return JSONResponse(status_code = 204, content = {}) 
    return patients[pk].patient
