from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime

class RunRequest(BaseModel):
    """
    Request model for running a task
    """
    task_id: str = Field(..., description="The ID of the task to run (e.g., TSK-000001)")
    environment: str = Field(..., description="The target environment (e.g., DEV, QA, PROD)")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Optional parameters for the SQL query")
    created_by: str = Field(..., description="The user who is running the task")

class RunResponse(BaseModel):
    """
    Response model for a task run
    """
    task_id: str
    run_task_id: Optional[str] = None
    status: str
    environment: str
    message: str
    data: Optional[List[Dict[str, Any]]] = None
    rollback_query: Optional[str] = ""
    task_description: Optional[str] = None
    sql_query: Optional[str] = None
    created_by: Optional[str] = None
    execution_time_ms: float
    created_date: Optional[datetime] = None
