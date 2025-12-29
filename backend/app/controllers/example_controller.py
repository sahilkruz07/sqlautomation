from fastapi import APIRouter, HTTPException
from typing import List

# Create router instance
router = APIRouter()

@router.get("/example")
async def get_example():
    """Example GET endpoint"""
    return {"message": "This is an example controller"}

@router.post("/example")
async def create_example(data: dict):
    """Example POST endpoint"""
    return {"message": "Data received", "data": data}

# To use this router, import it in main.py and include it:
# from app.controllers.example_controller import router as example_router
# app.include_router(example_router, prefix="/api/v1", tags=["example"])
