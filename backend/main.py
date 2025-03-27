from fastapi import FastAPI
from backend.mysql_connector import main

app = FastAPI()



@app.get("/")
async def root():
    return {"message": "Hello World"}
