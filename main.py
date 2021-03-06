from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, Response, status, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel

from hashlib import sha256

import secrets, sqlite3

app = FastAPI()
security = HTTPBasic()
templates = Jinja2Templates(directory = "templates")

app.counter = 0
app.secret_key = '432A462D4A614E645267556B58703273357538782F413F4428472B4B62506553'
patients = []
app.sessions = []
app.users = []
    

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
            app.users.append(user)
        return session_token 

    
# ---Homework 1------------------------------------------

class HelloResp(BaseModel):
    msg: str

@app.post('/')
@app.get('/')
def hello_world():
    return {"message": "Hello World during the coronavirus pandemic!"}


@app.get('/hello/{name}', response_model=HelloResp)
def read_item(name: str, cookie: str = Cookie(None)):
    if cookie not in app.sessions:
        raise HTTPException(status_code=403, detail="Unathorised")
    return HelloResp(msg=f"Hello {name}")


@app.get('/welcome')
def welcome(request: Request, response: Response, cookie: str = Cookie(None)):
    if cookie not in app.sessions:
        raise HTTPException(status_code=401, detail="Unathorised")
    user = app.users[0]
    return templates.TemplateResponse('welcome.html', {"request": request,"user": user})

# ---Homework 2------------------------------------------

class Patient(BaseModel):
    name: str
    surename: str

class PatientID(BaseModel):
    id: int
    patient: Patient



@app.post('/patient', response_model=PatientID)
def add_patient(request: Patient, response: Response, cookie: str = Cookie(None)):
    if cookie not in app.sessions:
        raise HTTPException(status_code=401, detail="Unathorised")
    global patients
    p = PatientID(id = app.counter, patient = request)
    patients.append(p)
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"]=f"/patient/{app.counter}"
    app.counter+=1

@app.get('/patient')
def show_patients(request: Request, response: Response, cookie: str = Cookie(None)):
    if cookie not in app.sessions:
        raise HTTPException(status_code=401, detail="Unathorised")
    global patients
    if len(patients)==0:
        response.status_code = status.HTTP_204_NO_CONTENT
    return patients

@app.get('/patient/{pk}')
def read_patient(pk: int, cookie: str = Cookie(None)):
    if cookie not in app.sessions:
        raise HTTPException(status_code=401, detail="Unathorised")
    global patients
    if pk not in [i.id for i in patients]:
        raise HTTPException(status_code=401, detail="Unathorised")
    return patients[pk].patient

@app.delete('/patient/{pk}')
def delete_patient(pk: int, response: Response, cookie: str = Cookie(None)):
    if cookie not in app.sessions:
        raise HTTPException(status_code=401, detail="Unathorised")
    patients.pop(pk) 
    response.status_code = status.HTTP_204_NO_CONTENT

# ---Homework 3------------------------------------------

@app.post('/login')
def login(response: Response, cookie: str = Depends(get_current_user)):
    response.set_cookie(key = 'cookie', value = cookie)
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = '/welcome'

@app.post('/logout')
def logout(response: Response, cookie: str = Cookie(None)):
    if cookie not in app.sessions:
        return RedirectResponse(url='/')
    response.delete_cookie(key='cookie')
    app.sessions.clear()
    return RedirectResponse(url='/')


# ---Homework 4------------------------------------------

class Album(BaseModel):
    title: str
    artist_id: int

class Customer(BaseModel):
    company: str = None
    address: str = None
    city: str = None
    state: str = None
    country: str = None 
    postalcode: str = None
    fax: str = None

@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect('chinook/chinook.db')


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.get('/tracks/')
async def tracks(page: int = Query(0), per_page:int = Query(10)):
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute(f"SELECT * FROM tracks LIMIT {per_page} OFFSET {page * per_page}").fetchall()
    return data  


@app.get('/tracks/composers/')
async def composer(composer_name: str = Query(None)):
    app.db_connection.row_factory = lambda cursor, row: row[0]
    data = app.db_connection.execute(f"SELECT DISTINCT composer FROM tracks").fetchall()
    if composer_name not in data:
        raise HTTPException(status_code=404, detail={"error": composer_name})
    names = app.db_connection.execute(f"SELECT name FROM tracks WHERE composer = ? ORDER BY name", (composer_name, )).fetchall()
    return names


@app.post('/albums', status_code = status.HTTP_201_CREATED)
async def add_album(album: Album):
    app.db_connection.row_factory = sqlite3.Row 
    find = app.db_connection.execute(f"SELECT ArtistId FROM artists WHERE ArtistId = ?", (album.artist_id,)).fetchone()
    if find is None:
        raise HTTPException(status_code=404, detail={"error": "No artist like that in the database"})
    insert = app.db_connection.execute("INSERT INTO albums (title, artistid) VALUES (?, ?)", (album.title, album.artist_id, ))
    app.db_connection.commit()
    result = app.db_connection.execute(f"SELECT * FROM albums WHERE albumid = ?", (insert.lastrowid,)).fetchall()
    return {"AlbumId": insert.lastrowid, "Title": album.title, "ArtistId": album.artist_id}

@app.get('/albums/{album_id}')
async def album(album_id: int):
    app.db_connection.row_factory = sqlite3.Row
    result = app.db_connection.execute(f"SELECT * FROM albums WHERE albumid = ?", (album_id,)).fetchone()
    return result


@app.put('/customers/{customer_id}')
async def edit_customer(customer: Customer, customer_id: int):
    app.db_connection.row_factory = sqlite3.Row
    res = app.db_connection.execute(f"SELECT * FROM customers WHERE customerid = ?", (customer_id, )).fetchone()
    if res is None:
        raise HTTPException(status_code=404, detail={"error": "Customer not found"})
    update_customer = jsonable_encoder(customer)
    trimed = {k: v for k, v in update_customer.items() if v is not None}
    for i in trimed:
        I = i.capitalize()
        command =f"UPDATE customers SET {I} = '{trimed[i]}' WHERE customerid = {customer_id}"
        update = app.db_connection.execute(command)
        app.db_connection.commit()
    return app.db_connection.execute(f"SELECT * FROM customers WHERE customerid = ?", (customer_id,)).fetchone()


@app.get('/sales')
async def get_sales(category: str = Query(None)):
    if category not in ['customers', 'genres']:
        raise HTTPException(status_code=404, detail={"error": "Wrong category"})
    if category == 'customers':
        app.db_connection.row_factory = sqlite3.Row
        cat = app.db_connection.execute('''
        SELECT invoices.customerid, email, phone, ROUND(SUM(total), 2) as Sum FROM invoices 
        JOIN customers ON invoices.customerid = customers.customerid 
        GROUP BY invoices.customerid 
        ORDER BY sum DESC, invoices.customerid
        ''').fetchall()
        return cat
    if category == 'genres':
        app.db_connection.row_factory = sqlite3.Row
        gen = app.db_connection.execute('''
        SELECT genres.name, SUM(quantity) as Sum FROM invoice_items
        JOIN genres ON tracks.genreid = genres.genreid
        JOIN tracks ON invoice_items.trackid = tracks.trackid
        GROUP BY tracks.genreid 
        ORDER BY Sum DESC, genres.name
        ''').fetchall()
        return gen

