from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List

class RunRequest(BaseModel):
    """
    Request model for running a task
    """
    task_id: str = Field(..., description="The ID of the task to run (e.g., TSK-000001)")
    environment: str = Field(..., description="The target environment (e.g., DEV, QA, PROD)")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Optional parameters for the SQL query")

class RunResponse(BaseModel):
    """
    Response model for a task run
    """
    task_id: str
    status: str
    environment: str
    message: str
    data: Optional[List[Dict[str, Any]]] = None
    execution_time_ms: float
