from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from app.configs.database import MongoDB
from app.configs.settings import settings
from app.controllers.task_controller import router as task_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup: Connect to MongoDB
    await MongoDB.connect_to_database(
        mongodb_uri=settings.MONGODB_URI,
        db_name=settings.MONGODB_DB_NAME
    )
    yield
    # Shutdown: Close MongoDB connection
    await MongoDB.close_database_connection()


# Create FastAPI application instance
app = FastAPI(
    title="SQL Automation API",
    description="FastAPI skeleton project for SQL automation",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.ALLOWED_ORIGINS] if isinstance(settings.ALLOWED_ORIGINS, str) else settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint to verify API is running"""
    return {
        "message": "Welcome to SQL Automation API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# Include routers
app.include_router(task_router, prefix="/api/v1", tags=["tasks"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Enable auto-reload during development
    )
