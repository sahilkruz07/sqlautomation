from fastapi import APIRouter, HTTPException, status, Query
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

@router.get(
    "/run/{run_task_id}",
    response_model=RunResponse,
    summary="Get run details",
    description="Retrieve details of a specific task run by its Run Task ID"
)
async def get_run_details(run_task_id: str):
    """Get details of a specific run"""
    run = await run_service.get_run(run_task_id)
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run {run_task_id} not found"
        )
    return run

@router.get(
    "/run",
    response_model=list[RunResponse],
    summary="Get all runs",
    description="Retrieve history of all task runs with pagination"
)
async def get_all_runs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    search: str = Query(None, description="Global search query across multiple fields")
):
    """Get history of all runs"""
    return await run_service.get_all_runs(skip=skip, limit=limit, search=search)

@router.delete(
    "/run/{run_task_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete run record",
    description="Remove a specific task run record from history"
)
async def delete_run(run_task_id: str):
    """Delete a specific run record"""
    deleted = await run_service.delete_run(run_task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Run {run_task_id} not found"
        )
    return {"status": "success", "message": f"Run {run_task_id} deleted successfully"}
