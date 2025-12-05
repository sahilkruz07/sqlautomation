from typing import Optional, List

from app.models.task_model import TaskCreate, TaskResponse
from app.repositories.task_repository import TaskRepository


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
        # Convert Pydantic model to dict
        task_dict = task_data.model_dump()
        
        # Save to database via repository
        created_task = await self.task_repository.save(task_dict)
        
        # Convert to response model
        return self._convert_to_response(created_task)
    
    async def get_task(self, task_id: str) -> Optional[TaskResponse]:
        """
        Get a task by ID
        
        Args:
            task_id: Task ID (MongoDB ObjectId as string)
            
        Returns:
            Task response or None if not found
        """
        # Find task via repository
        task = await self.task_repository.find_by_id(task_id)
        
        if task is None:
            return None
        
        # Convert to response model
        return self._convert_to_response(task)
    
    async def get_all_tasks(self, skip: int = 0, limit: int = 100) -> List[TaskResponse]:
        """
        Get all tasks with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of task responses
        """
        # Find all tasks via repository
        tasks = await self.task_repository.find_all(skip=skip, limit=limit)
        
        # Convert to response models
        return [self._convert_to_response(task) for task in tasks]
    
    async def update_task(self, task_id: str, task_data: dict) -> Optional[TaskResponse]:
        """
        Update a task
        
        Args:
            task_id: Task ID
            task_data: Updated task data
            
        Returns:
            Updated task response or None if not found
        """
        # Update via repository
        updated_task = await self.task_repository.update(task_id, task_data)
        
        if updated_task is None:
            return None
        
        # Convert to response model
        return self._convert_to_response(updated_task)
    
    async def delete_task(self, task_id: str) -> bool:
        """
        Delete a task
        
        Args:
            task_id: Task ID
            
        Returns:
            True if deleted, False otherwise
        """
        # Delete via repository
        return await self.task_repository.delete(task_id)
    
    async def get_tasks_by_db_name(self, db_name: str) -> List[TaskResponse]:
        """
        Get all tasks for a specific database
        
        Args:
            db_name: Database name
            
        Returns:
            List of task responses
        """
        tasks = await self.task_repository.find_by_db_name(db_name)
        return [self._convert_to_response(task) for task in tasks]
    
    async def get_tasks_by_user(self, created_by: str) -> List[TaskResponse]:
        """
        Get all tasks created by a specific user
        
        Args:
            created_by: Username
            
        Returns:
            List of task responses
        """
        tasks = await self.task_repository.find_by_created_by(created_by)
        return [self._convert_to_response(task) for task in tasks]
    
    def _convert_to_response(self, task_doc: dict) -> TaskResponse:
        """
        Convert MongoDB document to TaskResponse model
        
        Args:
            task_doc: Task document from MongoDB
            
        Returns:
            TaskResponse model
        """
        task_doc["_id"] = str(task_doc["_id"])
        return TaskResponse(**task_doc)
