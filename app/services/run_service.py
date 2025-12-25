from typing import Dict, Any, List
import logging
import time
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

from app.models.run_model import RunRequest, RunResponse
from app.models.run_model import RunRequest, RunResponse
from app.services.task_service import TaskService
from app.repositories.env_config_repository import EnvConfigRepository
from fastapi import HTTPException, status

# Initialize logger
logger = logging.getLogger(__name__)

class RunService:
    """
    Service class for executing tasks in specific environments.
    """
    
    def __init__(self):
        self.task_service = TaskService()
        self.env_config_repository = EnvConfigRepository()
        
    async def execute_task(self, request: RunRequest) -> RunResponse:
        """
        Execute a task's SQL query in the specified environment.
        
        Args:
            request: The run request containing task_id and environment
            
        Returns:
            RunResponse with execution results
        """
        start_time = time.time()
        
        logger.info(f"RunService: Execution requested for task {request.task_id} in {request.environment}")
        
        # 1. Fetch Task Details
        task = await self.task_service.get_task(request.task_id)
        
        if not task:
            logger.error(f"RunService: Task {request.task_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Task {request.task_id} not found"
            )
            
        logger.debug(f"RunService: Retrieved task details: {task.task_description}")
        
        # 2. Get Connection String for Environment
        # Query env_config collection via repository
        connection_string = await self._get_connection_string(task.db_name, request.environment)
        
        if not connection_string:
            logger.error(f"RunService: No configuration found for DB {task.db_name} in {request.environment}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Configuration for database '{task.db_name}' in environment '{request.environment}' not found"
            )

        # 3. Execute Query (Actual Execution)
        # Uses SQLAlchemy with async driver
        try:
            results = await self._execute_query(task.sql_query, connection_string, request.parameters)
            
            execution_time = (time.time() - start_time) * 1000
            
            logger.info(f"RunService: Task {request.task_id} executed successfully in {execution_time:.2f}ms")
            
            return RunResponse(
                task_id=request.task_id,
                status="success",
                environment=request.environment,
                message="Query executed successfully",
                data=results,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            logger.error(f"RunService: Execution failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Execution failed: {str(e)}"
            )

    async def _get_connection_string(self, db_name: str, environment: str) -> str:
        """
        Get connection string from env_config collection.
        """
        # Fetch config from repository
        config = await self.env_config_repository.get_config(db_name, environment)
        
        if not config or "config_value" not in config:
            return None
            
        db_config = config["config_value"]
        
        # Construct SQL connection string (assuming MySQL/SQLAlchemy format based on user example)
        # format: dialect+driver://username:password@host:port/database
        try:
            user = db_config.get("sql_db_username")
            password = db_config.get("sql_db_password")
            host = db_config.get("sql_db_host")
            port = db_config.get("sql_db_port")
            db = db_config.get("sql_db_name")
            
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
        except Exception as e:
            logger.error(f"Error constructing connection string: {str(e)}")
            return None

    async def _execute_query(self, query: str, connection_string: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute actual SQL query using SQLAlchemy.
        """
        logger.info(f"RunService: Executing query on {connection_string.split('@')[-1]}")  # Log only host/db for security
        logger.debug(f"RunService: Query: {query}")
        
        # Ensure connection string uses aiomysql/async driver
        if "mysql://" in connection_string and "+aiomysql" not in connection_string:
             connection_string = connection_string.replace("mysql://", "mysql+aiomysql://")
        if "postgresql://" in connection_string and "+asyncpg" not in connection_string:
             connection_string = connection_string.replace("postgresql://", "postgresql+asyncpg://")

        engine = create_async_engine(connection_string, echo=False)
        
        try:
            async with engine.connect() as conn:
                # Convert params to dict if None
                query_params = params or {}
                
                # Execute query
                result = await conn.execute(text(query), query_params)
                
                # Get column names
                keys = result.keys()
                
                # Fetch all rows and convert to list of dicts
                rows = result.all()
                data = [dict(zip(keys, row)) for row in rows]
                
                logger.info(f"RunService: Query returned {len(data)} rows")
                return data
                
        except Exception as e:
            logger.error(f"RunService: Database execution error: {str(e)}")
            raise
        finally:
            await engine.dispose()
