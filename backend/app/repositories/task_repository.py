from typing import Optional, List
from datetime import datetime
from app.utils.date_utils import get_now_ist
from bson import ObjectId
import logging

from app.configs.database import get_task_master_collection, get_counter_master_collection

# Initialize logger
logger = logging.getLogger(__name__)


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
        try:
            logger.debug("Generating next task ID from counter_master")
            # Atomically increment the counter and get the new value
            result = await self.counter_collection.find_one_and_update(
                {"counter_type": "TASK"},
                {"$inc": {"counter_value": 1}},
                return_document=True,
                upsert=True  # Create if doesn't exist
            )
            
            counter_value = result.get("counter_value", 1)
            # Format as TSK-XXXXXX (6 digits with leading zeros)
            task_id = f"TSK-{counter_value:06d}"
            logger.info(f"Generated new task ID: {task_id}")
            return task_id
        except Exception as e:
            logger.error(f"Error generating task ID: {str(e)}", exc_info=True)
            raise
    
    async def save(self, task_data: dict) -> dict:
        """
        Save a new task to the database
        
        Args:
            task_data: Task data to save
            
        Returns:
            Created task document with task_id
        """
        try:
            logger.info(f"Creating new task for db_name: {task_data.get('db_name')}")
            
            # Generate next task_id
            task_id = await self._get_next_task_id()
            task_data["task_id"] = task_id
            
            # Add created_date timestamp
            task_data["created_date"] = get_now_ist()
            task_data["updated_date"] = get_now_ist()
            
            logger.debug(f"Inserting task {task_id} into database")
            # Insert into database
            result = await self.collection.insert_one(task_data)
            
            # Fetch and return the created task
            created_task = await self.collection.find_one({"_id": result.inserted_id})
            logger.info(f"Successfully created task {task_id}")
            return created_task
        except Exception as e:
            logger.error(f"Error saving task: {str(e)}", exc_info=True)
            raise
    
    async def find_by_id(self, task_id: str) -> Optional[dict]:
        """
        Find a task by ID
        
        Args:
            task_id: Task ID (e.g., TSK-000001)
            
        Returns:
            Task document or None if not found
        """
        try:
            logger.debug(f"Finding task by ID: {task_id}")
            # Find task in database by task_id field
            task = await self.collection.find_one({"task_id": task_id})
            if task:
                logger.info(f"Task {task_id} found")
            else:
                logger.warning(f"Task {task_id} not found")
            return task
        except Exception as e:
            logger.error(f"Error finding task {task_id}: {str(e)}", exc_info=True)
            raise
    
    async def find_all(self, skip: int = 0, limit: int = 100, search: str = None) -> List[dict]:
        """
        Find all tasks with pagination and optional search
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Search query string
            
        Returns:
            List of task documents
        """
        try:
            query = {}
            if search:
                # Search across multiple fields using regex
                search_regex = {"$regex": search, "$options": "i"}
                query = {
                    "$or": [
                        {"task_id": search_regex},
                        {"task_description": search_regex},
                        {"db_name": search_regex},
                        {"query_type": search_regex},
                        {"created_by": search_regex}
                    ]
                }

            logger.debug(f"Finding tasks with query={query}, skip={skip}, limit={limit}")
            cursor = self.collection.find(query).sort([("created_date", -1), ("task_id", -1)]).skip(skip).limit(limit)
            tasks = await cursor.to_list(length=limit)
            logger.info(f"Retrieved {len(tasks)} tasks")
            return tasks
        except Exception as e:
            logger.error(f"Error finding all tasks: {str(e)}", exc_info=True)
            raise
    
    async def update(self, task_id: str, task_data: dict) -> Optional[dict]:
        """
        Update a task by ID
        
        Args:
            task_id: Task ID (e.g., TSK-000001)
            task_data: Updated task data
            
        Returns:
            Updated task document or None if not found
        """
        try:
            logger.info(f"Updating task {task_id}")
            logger.debug(f"Update data: {task_data}")
            
            # Add updated_date timestamp
            task_data["updated_date"] = get_now_ist()
            
            # Update in database using task_id field
            result = await self.collection.find_one_and_update(
                {"task_id": task_id},
                {"$set": task_data},
                return_document=True
            )
            
            if result:
                logger.info(f"Successfully updated task {task_id}")
            else:
                logger.warning(f"Task {task_id} not found for update")
            return result
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {str(e)}", exc_info=True)
            raise
    
    async def delete(self, task_id: str) -> bool:
        """
        Delete a task by ID
        
        Args:
            task_id: Task ID (e.g., TSK-000001)
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            logger.info(f"Deleting task {task_id}")
            result = await self.collection.delete_one({"task_id": task_id})
            deleted = result.deleted_count > 0
            if deleted:
                logger.info(f"Successfully deleted task {task_id}")
            else:
                logger.warning(f"Task {task_id} not found for deletion")
            return deleted
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {str(e)}", exc_info=True)
            raise
    
    async def find_by_db_name(self, db_name: str) -> List[dict]:
        """
        Find all tasks for a specific database
        
        Args:
            db_name: Database name
            
        Returns:
            List of task documents
        """
        try:
            logger.debug(f"Finding tasks for database: {db_name}")
            cursor = self.collection.find({"db_name": db_name}).sort("created_date", -1)
            tasks = await cursor.to_list(length=None)
            logger.info(f"Found {len(tasks)} tasks for database {db_name}")
            return tasks
        except Exception as e:
            logger.error(f"Error finding tasks for database {db_name}: {str(e)}", exc_info=True)
            raise
    
    async def find_by_created_by(self, created_by: str) -> List[dict]:
        """
        Find all tasks created by a specific user
        
        Args:
            created_by: Username
            
        Returns:
            List of task documents
        """
        try:
            logger.debug(f"Finding tasks created by: {created_by}")
            cursor = self.collection.find({"created_by": created_by}).sort("created_date", -1)
            tasks = await cursor.to_list(length=None)
            logger.info(f"Found {len(tasks)} tasks created by {created_by}")
            return tasks
        except Exception as e:
            logger.error(f"Error finding tasks for user {created_by}: {str(e)}", exc_info=True)
            raise
