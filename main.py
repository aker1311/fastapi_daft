from fastapi import FastAPI

from pydantic import BaseModel

app = FastAPI()

class HelloResp(BaseModel):
    msg: str

@app.get('/')
def hello_world():
    return {"message": "Hello World during the coronavirus pandemic!"}

@app.get("/hello/{name}", response_model=HelloResp)
def read_item(name: str):
    return HelloResp(msg=f"Hello {name}")


#@app.get("/{METHOD}")
#def read_method(METHOD: str):
#    return {"method": f'{METHOD}'}
