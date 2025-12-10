from typing import Optional, List
import logging

from app.models.task_model import TaskCreate, TaskResponse
from app.repositories.task_repository import TaskRepository

# Initialize logger
logger = logging.getLogger(__name__)


class TaskService:
    """
    Service class for task-related business logic
    Orchestrates operations between controllers and repositories
    """
    
    def __init__(self):
        self.task_repository = TaskRepository()
    
    async def create_task(self, task_data: TaskCreate) -> TaskResponse:
        """
        Create a new task
        
        Args:
            task_data: Task creation data
            
        Returns:
            Created task response
        """
        logger.info(f"Service: Creating task for db_name={task_data.db_name}, created_by={task_data.created_by}")
        try:
            # Convert Pydantic model to dict
            task_dict = task_data.model_dump()
            
            # Save to database via repository
            created_task = await self.task_repository.save(task_dict)
            
            # Convert to response model
            response = self._convert_to_response(created_task)
            logger.info(f"Service: Task {response.task_id} created successfully")
            return response
        except Exception as e:
            logger.error(f"Service: Error creating task: {str(e)}", exc_info=True)
            raise
    
    async def get_task(self, task_id: str) -> Optional[TaskResponse]:
        """
        Get a task by ID
        
        Args:
            task_id: Task ID (e.g., TSK-000001)
            
        Returns:
            Task response or None if not found
        """
        logger.debug(f"Service: Getting task {task_id}")
        try:
            # Find task via repository
            task = await self.task_repository.find_by_id(task_id)
            
            if task is None:
                logger.info(f"Service: Task {task_id} not found")
                return None
            
            # Convert to response model
            logger.debug(f"Service: Task {task_id} retrieved successfully")
            return self._convert_to_response(task)
        except Exception as e:
            logger.error(f"Service: Error getting task {task_id}: {str(e)}", exc_info=True)
            raise
    
    async def get_all_tasks(self, skip: int = 0, limit: int = 100) -> List[TaskResponse]:
        """
        Get all tasks with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of task responses
        """
        logger.debug(f"Service: Getting all tasks with skip={skip}, limit={limit}")
        try:
            # Find all tasks via repository
            tasks = await self.task_repository.find_all(skip=skip, limit=limit)
            
            # Convert to response models
            responses = [self._convert_to_response(task) for task in tasks]
            logger.info(f"Service: Retrieved {len(responses)} tasks")
            return responses
        except Exception as e:
            logger.error(f"Service: Error getting all tasks: {str(e)}", exc_info=True)
            raise
    
    async def update_task(self, task_id: str, task_data: dict) -> Optional[TaskResponse]:
        """
        Update a task
        
        Args:
            task_id: Task ID
            task_data: Updated task data
            
        Returns:
            Updated task response or None if not found
        """
        logger.info(f"Service: Updating task {task_id}")
        try:
            # Update via repository
            updated_task = await self.task_repository.update(task_id, task_data)
            
            if updated_task is None:
                logger.info(f"Service: Task {task_id} not found for update")
                return None
            
            # Convert to response model
            logger.info(f"Service: Task {task_id} updated successfully")
            return self._convert_to_response(updated_task)
        except Exception as e:
            logger.error(f"Service: Error updating task {task_id}: {str(e)}", exc_info=True)
            raise
    
    async def delete_task(self, task_id: str) -> bool:
        """
        Delete a task
        
        Args:
            task_id: Task ID
            
        Returns:
            True if deleted, False otherwise
        """
        logger.info(f"Service: Deleting task {task_id}")
        try:
            # Delete via repository
            deleted = await self.task_repository.delete(task_id)
            if deleted:
                logger.info(f"Service: Task {task_id} deleted successfully")
            else:
                logger.info(f"Service: Task {task_id} not found for deletion")
            return deleted
        except Exception as e:
            logger.error(f"Service: Error deleting task {task_id}: {str(e)}", exc_info=True)
            raise
    
    async def get_tasks_by_db_name(self, db_name: str) -> List[TaskResponse]:
        """
        Get all tasks for a specific database
        
        Args:
            db_name: Database name
            
        Returns:
            List of task responses
        """
        logger.debug(f"Service: Getting tasks for database {db_name}")
        try:
            tasks = await self.task_repository.find_by_db_name(db_name)
            responses = [self._convert_to_response(task) for task in tasks]
            logger.info(f"Service: Retrieved {len(responses)} tasks for database {db_name}")
            return responses
        except Exception as e:
            logger.error(f"Service: Error getting tasks for database {db_name}: {str(e)}", exc_info=True)
            raise
    
    async def get_tasks_by_user(self, created_by: str) -> List[TaskResponse]:
        """
        Get all tasks created by a specific user
        
        Args:
            created_by: Username
            
        Returns:
            List of task responses
        """
        logger.debug(f"Service: Getting tasks created by {created_by}")
        try:
            tasks = await self.task_repository.find_by_created_by(created_by)
            responses = [self._convert_to_response(task) for task in tasks]
            logger.info(f"Service: Retrieved {len(responses)} tasks created by {created_by}")
            return responses
        except Exception as e:
            logger.error(f"Service: Error getting tasks for user {created_by}: {str(e)}", exc_info=True)
            raise
    
    def _convert_to_response(self, task_doc: dict) -> TaskResponse:
        """
        Convert MongoDB document to TaskResponse model
        
        Args:
            task_doc: Task document from MongoDB
            
        Returns:
            TaskResponse model
        """
        # No need to convert _id anymore, task_id is already in the document
        return TaskResponse(**task_doc)
