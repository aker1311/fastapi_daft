from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def hello_world():
    return {"message": "Hello world"}

#Some comment to check git adding file
