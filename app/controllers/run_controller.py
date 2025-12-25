from fastapi import APIRouter, HTTPException, status
import logging

from app.models.run_model import RunRequest, RunResponse
from app.services.run_service import RunService

# Initialize logger
logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter()

# Initialize service
run_service = RunService()

@router.post(
    "/run",
    response_model=RunResponse,
    status_code=status.HTTP_200_OK,
    summary="Run a task query",
    description="Execute a task's SQL query in a specified environment (DEV, QA, PROD)"
)
async def run_task(request: RunRequest):
    """
    Run a task
    
    Args:
        request: Run request details including task_id and environment
        
    Returns:
        Execution results
    """
    logger.info(f"Controller: POST /run - Request to run task {request.task_id} in {request.environment}")
    
    try:
        response = await run_service.execute_task(request)
        logger.info(f"Controller: Task {request.task_id} execution completed successfully")
        return response
    except HTTPException as he:
        # Re-raise HTTP exceptions to preserve status codes
        raise he
    except Exception as e:
        logger.error(f"Controller: Check run failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error during execution: {str(e)}"
        )
