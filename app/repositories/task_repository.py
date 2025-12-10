from typing import Optional, List
from datetime import datetime
from bson import ObjectId

from app.configs.database import get_task_master_collection, get_counter_master_collection


class TaskRepository:
    """
    Repository class for task data access
    Handles all database operations for the task_master collection
    """
    
    def __init__(self):
        self._collection = None
        self._counter_collection = None
    
    @property
    def collection(self):
        """Lazy load collection to avoid initialization issues"""
        if self._collection is None:
            self._collection = get_task_master_collection()
        return self._collection
    
    @property
    def counter_collection(self):
        """Lazy load counter collection to avoid initialization issues"""
        if self._counter_collection is None:
            self._counter_collection = get_counter_master_collection()
        return self._counter_collection
    
    async def _get_next_task_id(self) -> str:
        """
        Generate next task ID by incrementing counter in counter_master
        
        Returns:
            Task ID in format TSK-XXXXXX (e.g., TSK-000001)
        """
        # Atomically increment the counter and get the new value
        result = await self.counter_collection.find_one_and_update(
            {"counter_type": "TASK"},
            {"$inc": {"counter_value": 1}},
            return_document=True,
            upsert=True  # Create if doesn't exist
        )
        
        counter_value = result.get("counter_value", 1)
        # Format as TSK-XXXXXX (6 digits with leading zeros)
        return f"TSK-{counter_value:06d}"
    
    async def save(self, task_data: dict) -> dict:
        """
        Save a new task to the database
        
        Args:
            task_data: Task data to save
            
        Returns:
            Created task document with task_id
        """
        # Generate next task_id
        task_id = await self._get_next_task_id()
        task_data["task_id"] = task_id
        
        # Add created_date timestamp
        task_data["created_date"] = datetime.utcnow()
        task_data["updated_date"] = datetime.utcnow()
        
        # Insert into database
        result = await self.collection.insert_one(task_data)
        
        # Fetch and return the created task
        created_task = await self.collection.find_one({"_id": result.inserted_id})
        return created_task
    
    async def find_by_id(self, task_id: str) -> Optional[dict]:
        """
        Find a task by ID
        
        Args:
            task_id: Task ID (e.g., TSK-000001)
            
        Returns:
            Task document or None if not found
        """
        # Find task in database by task_id field
        task = await self.collection.find_one({"task_id": task_id})
        return task
    
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[dict]:
        """
        Find all tasks with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of task documents
        """
        cursor = self.collection.find().skip(skip).limit(limit).sort("created_date", -1)
        tasks = await cursor.to_list(length=limit)
        return tasks
    
    async def update(self, task_id: str, task_data: dict) -> Optional[dict]:
        """
        Update a task by ID
        
        Args:
            task_id: Task ID (e.g., TSK-000001)
            task_data: Updated task data
            
        Returns:
            Updated task document or None if not found
        """
        # Add updated_date timestamp
        task_data["updated_date"] = datetime.utcnow()
        
        # Update in database using task_id field
        result = await self.collection.find_one_and_update(
            {"task_id": task_id},
            {"$set": task_data},
            return_document=True
        )
        
        return result
    
    async def delete(self, task_id: str) -> bool:
        """
        Delete a task by ID
        
        Args:
            task_id: Task ID (e.g., TSK-000001)
            
        Returns:
            True if deleted, False otherwise
        """
        result = await self.collection.delete_one({"task_id": task_id})
        return result.deleted_count > 0
    
    async def find_by_db_name(self, db_name: str) -> List[dict]:
        """
        Find all tasks for a specific database
        
        Args:
            db_name: Database name
            
        Returns:
            List of task documents
        """
        cursor = self.collection.find({"db_name": db_name}).sort("created_date", -1)
        tasks = await cursor.to_list(length=None)
        return tasks
    
    async def find_by_created_by(self, created_by: str) -> List[dict]:
        """
        Find all tasks created by a specific user
        
        Args:
            created_by: Username
            
        Returns:
            List of task documents
        """
        cursor = self.collection.find({"created_by": created_by}).sort("created_date", -1)
        tasks = await cursor.to_list(length=None)
        return tasks
