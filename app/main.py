import logging
from fastapi import FastAPI
from app.routers import project, document, user, issue, plan

# Enhanced Logging Setup
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
logger = logging.getLogger("uvicorn.error")

app = FastAPI()

# Register all routers
app.include_router(project.router)
app.include_router(document.router)
app.include_router(user.router)
app.include_router(issue.router)
app.include_router(plan.router)

@app.get("/health")
def read_health():
    return {"status": "up and running"}