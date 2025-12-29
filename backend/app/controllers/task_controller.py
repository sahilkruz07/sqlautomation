from fastapi import APIRouter, HTTPException, status, Query
from typing import List
import logging

from app.models.task_model import TaskCreate, TaskResponse
from app.services.task_service import TaskService

# Initialize logger
logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter()

# Initialize service
task_service = TaskService()


@router.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task in the task_master collection"
)
async def create_task(task_data: TaskCreate):
    """
    Create a new task
    
    Args:
        task_data: Task creation data
        
    Returns:
        Created task details
    """
    logger.info(f"Controller: POST /tasks - Creating task for db_name={task_data.db_name}")
    try:
        task = await task_service.create_task(task_data)
        logger.info(f"Controller: Task {task.task_id} created successfully")
        return task
    except Exception as e:
        logger.error(f"Controller: Error creating task: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating task: {str(e)}"
        )


@router.get(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Get a task by ID",
    description="Retrieve a task from the task_master collection by its ID"
)
async def get_task(task_id: str):
    """
    Get a task by ID
    
    Args:
        task_id: Task ID (e.g., TSK-000001)
        
    Returns:
        Task details
    """
    logger.info(f"Controller: GET /tasks/{task_id}")
    task = await task_service.get_task(task_id)
    
    if task is None:
        logger.warning(f"Controller: Task {task_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    
    logger.debug(f"Controller: Returning task {task_id}")
    return task


@router.get(
    "/tasks",
    response_model=List[TaskResponse],
    summary="Get all tasks",
    description="Retrieve all tasks from the task_master collection with pagination"
)
async def get_all_tasks(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    search: str = Query(None, description="Global search query across multiple fields")
):
    """
    Get all tasks with pagination
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of tasks
    """
    logger.info(f"Controller: GET /tasks - skip={skip}, limit={limit}")
    try:
        tasks = await task_service.get_all_tasks(skip=skip, limit=limit, search=search)
        logger.info(f"Controller: Returning {len(tasks)} tasks")
        return tasks
    except Exception as e:
        logger.error(f"Controller: Error retrieving tasks: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving tasks: {str(e)}"
        )


@router.put(
    "/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Update a task",
    description="Update an existing task in the task_master collection"
)
async def update_task(task_id: str, task_data: dict):
    """
    Update a task
    
    Args:
        task_id: Task ID
        task_data: Updated task data
        
    Returns:
        Updated task details
    """
    logger.info(f"Controller: PUT /tasks/{task_id}")
    logger.debug(f"Controller: Update data: {task_data}")
    
    task = await task_service.update_task(task_id, task_data)
    
    if task is None:
        logger.warning(f"Controller: Task {task_id} not found for update")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    
    logger.info(f"Controller: Task {task_id} updated successfully")
    return task


@router.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Delete a task from the task_master collection"
)
async def delete_task(task_id: str):
    """
    Delete a task
    
    Args:
        task_id: Task ID
    """
    logger.info(f"Controller: DELETE /tasks/{task_id}")
    deleted = await task_service.delete_task(task_id)
    
    if not deleted:
        logger.warning(f"Controller: Task {task_id} not found for deletion")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found"
        )
    
    logger.info(f"Controller: Task {task_id} deleted successfully")
    return None


# To use this router, import it in main.py and include it:
# from app.controllers.task_controller import router as task_router
# app.include_router(task_router, prefix="/api/v1", tags=["tasks"])
