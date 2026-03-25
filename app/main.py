from fastapi import FastAPI
from app.routers import project

app = FastAPI()

app.include_router(project.router)

@app.get("/health")
def read_health():
    return {"status": "up and running"}
