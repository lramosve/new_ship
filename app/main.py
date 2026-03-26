import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, document, issue, plan, project, task, user

# Enhanced Logging Setup
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
logger = logging.getLogger('uvicorn.error')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:4173',
        'http://127.0.0.1:4173',
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Register all routers
app.include_router(auth.router)
app.include_router(project.router)
app.include_router(document.router)
app.include_router(user.router)
app.include_router(issue.router)
app.include_router(plan.router)
app.include_router(task.router)


@app.get('/health')
def read_health():
    return {'status': 'up and running'}
