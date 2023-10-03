from dotenv import load_dotenv

# Load environment variables from .env file, so they are accessible across the project
load_dotenv()

from fastapi import FastAPI, Request
from api import api_router
from database import init_db
from logger import log
from search import create_indices

# Initialize FastAPI and set api router
app = FastAPI()
app.include_router(api_router)

# Database initialization
init_db()

# Create elasticsearch indices
create_indices()


# Unexpected exception handling on API calls
@app.middleware("http")
async def log_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        log.error(f"Unhandled exception: {e}")
        raise
