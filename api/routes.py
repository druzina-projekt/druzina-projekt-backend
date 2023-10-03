from fastapi import APIRouter
from .endpoints import parse_router

router = APIRouter()

router.include_router(parse_router, prefix="/pdf", tags=["pdf"])
