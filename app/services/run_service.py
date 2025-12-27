from typing import Dict, Any, List, Tuple
import logging
import time

import re
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text, exc

from app.models.run_model import RunRequest, RunResponse
from app.services.task_service import TaskService
from app.repositories.env_config_repository import EnvConfigRepository
from app.repositories.run_repository import RunRepository
from app.configs.settings import settings
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
        self.run_repository = RunRepository()
        
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
            results, row_count = await self._execute_query(task.sql_query, connection_string, request.parameters)
            
            execution_time = (time.time() - start_time) * 1000
            
            logger.info(f"RunService: Task {request.task_id} executed successfully in {execution_time:.2f}ms")
            
            # Determine message based on rows affected/returned
            message = "Query executed successfully"
            if row_count >= 0 and not results:
                # Likely INSERT/UPDATE/DELETE
                message = f"Query executed successfully. Rows affected: {row_count}"
            elif results:
                 message = f"Query executed successfully. Rows returned: {len(results)}"
            
            # Save run execution details to run_master
            return await self._save_success_run(
                request=request,
                message=message,
                data=results,
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"RunService: Execution failed: {str(e)}", exc_info=True)
            
            # Record failed run
            error_detail = await self._save_failed_run(request, e, start_time)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_detail
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
            
            return f"mysql+aiomysql://{user}:{password}@{host}:{port}/{db}"
        except Exception as e:
            logger.error(f"Error constructing connection string: {str(e)}")
            return None

    def _inject_limit_if_needed(self, query: str) -> str:
        """
        Inject LIMIT clause if missing for SELECT queries.
        This prevents fetching too many rows at DB level.
        """
        limit = settings.SQL_QUERY_ROW_LIMIT
        clean_query = query.strip()
        upper_query = clean_query.upper()
        
        # Simple heuristic: strictly starts with SELECT and doesn't contain LIMIT
        # (excludes CTEs starting with WITH, or subqueries for safety initially)
        if upper_query.startswith("SELECT") and not re.search(r"\bLIMIT\b", upper_query) and not re.search(r"\bPROCEDURE\b", upper_query):
             # Remove trailing semicolon if present
             if clean_query.endswith(";"):
                 clean_query = clean_query[:-1]
             
             logger.info(f"RunService: Injecting LIMIT {limit} to query")
             return f"{clean_query} LIMIT {limit}"
             
        return query

    async def _save_success_run(self, request: RunRequest, message: str, data: List, execution_time: float) -> RunResponse:
        """
        Helper to construct response and save valid/successful run details.
        Returns the final RunResponse with generated run_task_id.
        """
        response_data = RunResponse(
            task_id=request.task_id,
            status="success",
            environment=request.environment,
            message=message,
            data=data,
            execution_time_ms=execution_time
        )

        try:
            # Convert Pydantic model to dict for storage
            run_doc = response_data.model_dump()
            # Add request parameters for context if needed
            run_doc["request_parameters"] = request.parameters
            
            saved_run = await self.run_repository.save(run_doc)
            
            # Update response with the generated run_task_id
            if saved_run and "run_task_id" in saved_run:
                response_data.run_task_id = saved_run["run_task_id"]
                
        except Exception as e:
            # Log error but don't fail the request if logging fails
            logger.error(f"RunService: Failed to save SUCCESS run execution log: {str(e)}", exc_info=True)
            
        return response_data

    async def _save_failed_run(self, request: RunRequest, error: Exception, start_time: float) -> str:
        """
        Helper to save failed run details.
        Returns the formatted error detail string (including run_task_id).
        """
        try:
            execution_time = (time.time() - start_time) * 1000
            failed_run_data = {
                "task_id": request.task_id,
                "status": "failed",
                "environment": request.environment,
                "message": f"Execution failed: {str(error)}",
                "data": None,
                "execution_time_ms": execution_time,
                "request_parameters": request.parameters
            }
            
            saved_run = await self.run_repository.save(failed_run_data)
            
            # If we have a run_task_id, we can include it in the error details
            run_task_id = saved_run.get("run_task_id") if saved_run else "UNKNOWN"
            return f"Execution failed: {str(error)} (Run ID: {run_task_id})"
            
        except Exception as save_err:
            logger.error(f"RunService: Failed to save FAILED run execution log: {str(save_err)}", exc_info=True)
            return f"Execution failed: {str(error)}"

    async def _execute_query(self, query: str, connection_string: str, params: Dict[str, Any] = None) -> Tuple[List[Dict[str, Any]], int]:
        """
        Execute actual SQL query using SQLAlchemy.
        """
        logger.info(f"RunService: Executing query on {connection_string.split('@')[-1]}")  # Log only host/db for security
        logger.debug(f"RunService: Query: {query}")
        
        # Ensure connection string uses aiomysql/async driver if not already present
        if "mysql://" in connection_string and "aiomysql" not in connection_string:
             connection_string = connection_string.replace("mysql://", "mysql+aiomysql://")
        if "postgresql://" in connection_string and "asyncpg" not in connection_string:
             connection_string = connection_string.replace("postgresql://", "postgresql+asyncpg://")

        engine = create_async_engine(connection_string, echo=False)
        
        try:
            async with engine.connect() as conn:
                # Convert params to dict if None
                query_params = params or {}
                
                # Check for SELECT and inject LIMIT if missing
                query = self._inject_limit_if_needed(query)

                # Execute query
                result = await conn.execute(text(query), query_params)
                await conn.commit()
                
                row_count = result.rowcount
                
                try:
                    # Check if the query returns rows (e.g., SELECT)
                    if result.returns_rows:
                        # Fetch all rows (query should already be limited)
                        rows = result.mappings().all()
                        data = [dict(row) for row in rows]
                        logger.info(f"RunService: Query returned {len(data)} rows")
                        return data, row_count
                    else:
                        logger.info(f"RunService: Query executed successfully. Rows affected: {row_count}")
                        return [], row_count
                except exc.ResourceClosedError:
                     logger.info("RunService: Query executed successfully (ResourceClosedError caught, assuming no rows)")
                     return [], row_count
                
        except Exception as e:
            logger.error(f"RunService: Database execution error: {str(e)}")
            raise
        finally:
            await engine.dispose()
