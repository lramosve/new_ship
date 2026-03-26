import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.settings import settings
from app.routers import analytics, auth, document, issue, plan, project, project_management, realtime, task, user

# Enhanced Logging Setup
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
logger = logging.getLogger('uvicorn.error')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
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
app.include_router(project_management.router)
app.include_router(realtime.router)
app.include_router(analytics.router)


@app.get('/health')
def read_health():
    return {'status': 'up and running'}
