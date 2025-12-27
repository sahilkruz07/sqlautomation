from typing import Optional, List
from datetime import datetime
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
            Run Task ID in format RTSK_XXXXXX (e.g., RTSK_000001)
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
            # Format as RTSK_XXXXXX (6 digits with leading zeros)
            run_task_id = f"RTSK_{counter_value:06d}"
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
            run_data["created_date"] = datetime.utcnow()
            
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
