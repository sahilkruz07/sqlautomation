from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class TaskBase(BaseModel):
    """Base model for Task"""
    task_description: str = Field(..., description="Description of the task")
    db_name: str = Field(..., description="Database name")
    sql_query: str = Field(..., description="SQL query to execute")
    query_type: Literal["SELECT", "INSERT", "UPDATE", "DELETE"] = Field(..., description="Type of SQL query")
    created_by: str = Field(..., description="User who created the task")


class TaskCreate(TaskBase):
    """Model for creating a new task"""
    pass


class TaskUpdate(BaseModel):
    """Model for updating a task"""
    task_description: Optional[str] = None
    db_name: Optional[str] = None
    sql_query: Optional[str] = None
    query_type: Optional[Literal["SELECT", "INSERT", "UPDATE", "DELETE"]] = None


class TaskResponse(TaskBase):
    """Model for task response"""
    task_id: str = Field(..., description="Task ID (e.g., TSK-000001)")
    created_date: datetime = Field(..., description="Creation timestamp")
    updated_date: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "task_id": "TSK-000001",
                "task_description": "Generate sales report",
                "db_name": "sales_db",
                "sql_query": "SELECT * FROM sales WHERE date > '2024-01-01'",
                "query_type": "SELECT",
                "created_by": "admin",
                "created_date": "2024-01-01T00:00:00",
                "updated_date": "2024-01-01T00:00:00"
            }
        }


class TaskInDB(TaskBase):
    """Model for task stored in database"""
    _id: ObjectId
    created_date: datetime
    updated_date: Optional[datetime] = None
