from typing import Optional, List
from datetime import datetime
from bson import ObjectId

from app.models.task_model import TaskCreate, TaskResponse, TaskInDB
from app.configs.database import get_task_master_collection


class TaskService:
    """
    Service class for task-related business logic
    """
    
    def __init__(self):
        self.collection = get_task_master_collection()
    
    async def create_task(self, task_data: TaskCreate) -> TaskResponse:
        """
        Create a new task in the database
        
        Args:
            task_data: Task creation data
            
        Returns:
            Created task response
        """
        # Prepare task document
        task_dict = task_data.model_dump()
        task_dict["created_date"] = datetime.utcnow()
        task_dict["updated_date"] = None
        
        # Insert into database
        result = await self.collection.insert_one(task_dict)
        
        # Fetch the created task
        created_task = await self.collection.find_one({"_id": result.inserted_id})
        
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
        # Validate ObjectId
        if not ObjectId.is_valid(task_id):
            return None
        
        # Find task in database
        task = await self.collection.find_one({"_id": ObjectId(task_id)})
        
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
        cursor = self.collection.find().skip(skip).limit(limit).sort("created_date", -1)
        tasks = await cursor.to_list(length=limit)
        
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
        if not ObjectId.is_valid(task_id):
            return None
        
        # Add updated_date
        task_data["updated_date"] = datetime.utcnow()
        
        # Update in database
        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(task_id)},
            {"$set": task_data},
            return_document=True
        )
        
        if result is None:
            return None
        
        return self._convert_to_response(result)
    
    async def delete_task(self, task_id: str) -> bool:
        """
        Delete a task
        
        Args:
            task_id: Task ID
            
        Returns:
            True if deleted, False otherwise
        """
        if not ObjectId.is_valid(task_id):
            return False
        
        result = await self.collection.delete_one({"_id": ObjectId(task_id)})
        return result.deleted_count > 0
    
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
