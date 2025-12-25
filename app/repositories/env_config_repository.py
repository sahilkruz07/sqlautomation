from typing import Optional
import logging

from app.configs.database import get_env_config_collection

# Initialize logger
logger = logging.getLogger(__name__)

class EnvConfigRepository:
    """
    Repository class for environment configuration data access
    Handles all database operations for the env_config collection
    """
    
    def __init__(self):
        self._collection = None
    
    @property
    def collection(self):
        """Lazy load collection to avoid initialization issues"""
        if self._collection is None:
            self._collection = get_env_config_collection()
        return self._collection
    
    async def get_config(self, config_key: str, env: str) -> Optional[dict]:
        """
        Get environment configuration by key and environment
        
        Args:
            config_key: Configuration key (e.g., LK_MASTER_DB)
            env: Environment (e.g., PREPROD, PROD, DEV)
            
        Returns:
            Configuration document or None if not found
        """
        try:
            logger.debug(f"Fetching config for key={config_key}, env={env}")
            config = await self.collection.find_one({
                "config_key": config_key, 
                "env": env
            })
            
            if config:
                logger.info(f"Found config for key={config_key}, env={env}")
            else:
                logger.warning(f"Config not found for key={config_key}, env={env}")
                
            return config
        except Exception as e:
            logger.error(f"Error fetching env config: {str(e)}", exc_info=True)
            raise
