from typing import Optional, List
from datetime import datetime
from app.utils.date_utils import get_now_ist
import logging

from app.configs.database import get_run_master_collection, get_counter_master_collection

# Initialize logger
logger = logging.getLogger(__name__)


class RunRepository:
    """
    Repository class for run execution data access
    Handles all database operations for the run_master collection
    """
    
    def __init__(self):
        self._collection = None
        self._counter_collection = None
    
    @property
    def collection(self):
        """Lazy load collection to avoid initialization issues"""
        if self._collection is None:
            self._collection = get_run_master_collection()
        return self._collection
    
    @property
    def counter_collection(self):
        """Lazy load counter collection to avoid initialization issues"""
        if self._counter_collection is None:
            self._counter_collection = get_counter_master_collection()
        return self._counter_collection
    
    async def _get_next_run_task_id(self) -> str:
        """
        Generate next run task ID by incrementing counter in counter_master
        
        Returns:
            Run Task ID in format RTSK-XXXXXX (e.g., RTSK-000001)
        """
        try:
            logger.debug("Generating next run task ID from counter_master")
            # Atomically increment the counter and get the new value
            result = await self.counter_collection.find_one_and_update(
                {"counter_type": "RUN_TASK"},
                {"$inc": {"counter_value": 1}},
                return_document=True,
                upsert=True  # Create if doesn't exist
            )
            
            counter_value = result.get("counter_value", 1)
            # Format as RTSK-XXXXXX (6 digits with leading zeros)
            run_task_id = f"RTSK-{counter_value:06d}"
            logger.info(f"Generated new run task ID: {run_task_id}")
            return run_task_id
        except Exception as e:
            logger.error(f"Error generating run task ID: {str(e)}", exc_info=True)
            raise
    
    async def save(self, run_data: dict) -> dict:
        """
        Save a new run execution to the database
        
        Args:
            run_data: Run data to save
            
        Returns:
            Created run document with run_task_id
        """
        try:
            # Generate next run_task_id
            run_task_id = await self._get_next_run_task_id()
            run_data["run_task_id"] = run_task_id
            
            # Add timestamps
            run_data["created_date"] = get_now_ist()
            
            logger.debug(f"Inserting run {run_task_id} into database")
            # Insert into database
            result = await self.collection.insert_one(run_data)
            
            # Fetch and return the created run document
            created_run = await self.collection.find_one({"_id": result.inserted_id})
            logger.info(f"Successfully saved run execution {run_task_id}")
            return created_run
        except Exception as e:
            logger.error(f"Error saving run execution: {str(e)}", exc_info=True)
            raise

    async def find_by_id(self, run_task_id: str) -> Optional[dict]:
        """
        Find a run by ID
        """
        try:
            return await self.collection.find_one({"run_task_id": run_task_id})
        except Exception as e:
            logger.error(f"Error finding run {run_task_id}: {str(e)}")
            raise

    async def find_all(self, skip: int = 0, limit: int = 100, search: str = None) -> List[dict]:
        """
        Find all runs with pagination and optional search
        """
        try:
            query = {}
            if search:
                # Search across multiple fields using regex
                search_regex = {"$regex": search, "$options": "i"}
                query = {
                    "$or": [
                        {"run_task_id": search_regex},
                        {"task_id": search_regex},
                        {"status": search_regex},
                        {"environment": search_regex},
                        {"created_by": search_regex}
                    ]
                }

            logger.debug(f"Finding runs with query={query}, skip={skip}, limit={limit}")
            cursor = self.collection.find(query).sort([("created_date", -1), ("run_task_id", -1)]).skip(skip).limit(limit)
            return await cursor.to_list(length=limit)
        except Exception as e:
            logger.error(f"Error finding all runs: {str(e)}")
            raise

    async def delete(self, run_task_id: str) -> bool:
        """
        Delete a run by ID
        """
        try:
            result = await self.collection.delete_one({"run_task_id": run_task_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting run {run_task_id}: {str(e)}")
            raise
