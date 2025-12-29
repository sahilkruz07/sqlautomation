from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ExampleBase(BaseModel):
    """Base model with common attributes"""
    name: str = Field(..., description="Name of the example")
    description: Optional[str] = Field(None, description="Description of the example")

class ExampleCreate(ExampleBase):
    """Model for creating a new example"""
    pass

class ExampleUpdate(BaseModel):
    """Model for updating an example"""
    name: Optional[str] = None
    description: Optional[str] = None

class ExampleResponse(ExampleBase):
    """Model for example response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # For SQLAlchemy models compatibility
