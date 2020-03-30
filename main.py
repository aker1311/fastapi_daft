from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def hello_world():
    return {"message": "Hello world"}

@app.get("/hello/{name}")
def read_item(name: str):
    return f"Hello {name}"
