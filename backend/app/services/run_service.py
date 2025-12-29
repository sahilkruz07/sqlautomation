from typing import Dict, Any, List, Tuple, Optional
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

        # 3. Fetch Old Data for Rollback (if strictly UPDATE/DELETE)
        old_data = []
        try:
            if task.query_type in ["UPDATE", "DELETE"]:
                old_data = await self._fetch_rollback_data(task.sql_query, connection_string, request.parameters)
        except Exception as e:
            logger.warning(f"RunService: Failed to fetch old data for rollback: {str(e)}")

        # 4. Execute Query (Actual Execution)
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
            
            # 5. Generate Rollback Query
            rollback_query = self._generate_rollback_query(task.query_type, task.sql_query, request.parameters, old_data)

            # Save run execution details to run_master
            return await self._save_success_run(
                request=request,
                task=task,
                message=message,
                data=results,
                execution_time=execution_time,
                rollback_query=rollback_query
            )
            
        except Exception as e:
            logger.error(f"RunService: Execution failed: {str(e)}", exc_info=True)
            
            # Attempt to generate rollback query even on failure if we have old data
            rollback_query = self._generate_rollback_query(task.query_type, task.sql_query, request.parameters, old_data)
            
            # Record failed run
            error_detail = await self._save_failed_run(request, task, e, start_time, rollback_query)

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_detail
            )

    async def get_run(self, run_task_id: str) -> Optional[RunResponse]:
        """
        Get run details by ID
        """
        run_doc = await self.run_repository.find_by_id(run_task_id)
        if not run_doc:
            return None
        return RunResponse(**run_doc)

    async def get_all_runs(self, skip: int = 0, limit: int = 100, search: str = None) -> List[RunResponse]:
        """
        Get all runs with pagination
        """
        run_docs = await self.run_repository.find_all(skip=skip, limit=limit, search=search)
        return [RunResponse(**doc) for doc in run_docs]

    async def delete_run(self, run_task_id: str) -> bool:
        """
        Delete a run record by ID
        """
        return await self.run_repository.delete(run_task_id)

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

    async def _fetch_rollback_data(self, sql_query: str, connection_string: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query to fetch data before it is modified.
        Used for generating rollback queries for UPDATE/DELETE.
        """
        sql = sql_query.strip().upper()
        table_name = ""
        where_clause = ""
        
        # Simple extraction logic
        if sql.startswith("DELETE"):
            match = re.search(r"DELETE\s+FROM\s+([^\s]+)\s+(WHERE\s+.+)", sql, re.IGNORECASE | re.DOTALL)
            if match:
                table_name = match.group(1)
                where_clause = match.group(2)
        elif sql.startswith("UPDATE"):
             match = re.search(r"UPDATE\s+([^\s]+)\s+SET\s+.+\s+(WHERE\s+.+)", sql, re.IGNORECASE | re.DOTALL)
             if match:
                table_name = match.group(1)
                where_clause = match.group(2)
                
        if table_name and where_clause:
            select_query = f"SELECT * FROM {table_name} {where_clause}"
            logger.info(f"RunService: Fetching rollback data: {select_query}")
            # Reuse _execute_query but ignore row count (since it's a select)
            data, _ = await self._execute_query(select_query, connection_string, params)
            logger.info(f"RunService: Fetched {len(data)} rows for rollback generation")
            return data
            
        return []

    def _generate_rollback_query(self, query_type: str, sql_query: str, params: Dict[str, Any] = None, old_data: List[Dict[str, Any]] = None) -> str:
        """
        Generate a rollback query based on the task query type.
        """
        query_type = query_type.upper()
        params = params or {}
        old_data = old_data or []
        
        try:
            if query_type == "SELECT":
                return ""
                
            elif query_type == "INSERT":
                # Logic: INSERT INTO table (col1, col2) VALUES (val1, val2), (val3, val4)
                # Rollback: DELETE FROM table WHERE col1 IN (val1, val3)
                
                sql = sql_query.strip()
                # Regex to find table, columns, and the values part
                # Format: INSERT INTO table (col1, col2...) VALUES ...
                match = re.search(r"INSERT\s+INTO\s+([^\s\(]+)\s*\((.+?)\)\s*VALUES\s*(.+)", sql, re.IGNORECASE | re.DOTALL)
                
                if match:
                    table_name = match.group(1)
                    columns_str = match.group(2)
                    rest_of_query = match.group(3) # The VALUES part
                    
                    # Get the first column name
                    first_col = columns_str.split(",")[0].strip()
                    
                    # Extract values for the first column
                    # This is tricky because of potentially multiple rows: (v1, v2), (v3, v4)
                    # and values might contain commas (strings). 
                    # Naive split by ")," might work for simple cases.
                    
                    # Normalize the values string
                    values_part = rest_of_query.strip()
                    if values_part.endswith(";"):
                        values_part = values_part[:-1]
                        
                    # Split into row groups: (val1, val2), (val3, val4)
                    # Simple regex to capture content inside parens ()
                    row_values_groups = re.findall(r"\((.+?)\)", values_part)
                    
                    extracted_values = []
                    for row_str in row_values_groups:
                        # row_str is like "'SQL_ID_1', 'Desc', 'true'"
                        # We want the first value.
                        # Naive split by comma, respecting quotes is hard with simple split.
                        # Assuming simple CSV for now.
                        first_val = row_str.split(",")[0].strip()
                        extracted_values.append(first_val)
                        
                    if extracted_values:
                        joined_values = ", ".join(extracted_values)
                        return f"DELETE FROM {table_name} WHERE {first_col} IN ({joined_values});"
                        
                return "-- Could not generate rollback for INSERT (Complex parsing required)"

            elif query_type == "DELETE":
                # Rollback DELETE: INSERT INTO table (cols) VALUES (old_dat)
                if not old_data:
                     return "-- No old data found to rollback DELETE"
                
                # Construct INSERT statements
                # We need table name again
                sql = sql_query.strip()
                match = re.search(r"DELETE\s+FROM\s+([^\s]+)", sql, re.IGNORECASE)
                table_name = match.group(1) if match else "UNKNOWN_TABLE"
                
                inserts = []
                for row in old_data:
                    # Construct simple INSERT based on dict keys
                    # Quote strings, handle None, etc.
                    cols = ", ".join(row.keys())
                    
                    vals = []
                    for v in row.values():
                        vals.append(self._format_sql_value(v))
                            
                    val_str = ", ".join(vals)
                    inserts.append(f"INSERT INTO {table_name} ({cols}) VALUES ({val_str});")
                
                return "\n".join(inserts)
                
            elif query_type == "UPDATE":
                # Rollback UPDATE: UPDATE table SET col=old_val WHERE first_col = val
                if not old_data:
                     return "-- No old data found to rollback UPDATE"
                
                sql = sql_query.strip()
                match = re.search(r"UPDATE\s+([^\s]+)", sql, re.IGNORECASE)
                table_name = match.group(1) if match else "UNKNOWN_TABLE"
                
                # Get the first column name from the first row of data
                first_col = list(old_data[0].keys())[0] if old_data else None
                
                updates = []
                for row in old_data:
                    set_clause = []
                    for k, v in row.items():
                         val = self._format_sql_clause(k, v)
                         set_clause.append(val)
                    set_str = ", ".join(set_clause)
                    
                    if first_col:
                        id_val = row[first_col]
                        id_val_str = self._format_sql_value(id_val)
                        updates.append(f"UPDATE {table_name} SET {set_str} WHERE {first_col} = {id_val_str};")
                    else:
                        updates.append(f"-- Warning: No columns found to identify row. UPDATE {table_name} SET {set_str} WHERE ...;")
                        
                return "\n".join(updates)
                
            return ""
        except Exception as e:
            logger.error(f"Error generating rollback query: {str(e)}")
            return f"-- Error generating rollback: {str(e)}"

    def _format_sql_value(self, v: Any) -> str:
        """
        Format a Python value for inclusion in a raw SQL string.
        """
        if v is None:
            return "NULL"
        if isinstance(v, (int, float)):
            return str(v)
        # For strings, datetimes, and everything else, wrap in single quotes
        val_str = str(v).replace("'", "''") # Basic escaping for single quotes
        return f"'{val_str}'"

    def _format_sql_clause(self, column: str, value: Any) -> str:
        """
        Format a 'column = value' clause for SQL.
        """
        return f"{column} = {self._format_sql_value(value)}"

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

    async def _save_success_run(self, request: RunRequest, task: Any, message: str, data: List, execution_time: float, rollback_query: str = "") -> RunResponse:
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
            rollback_query=rollback_query,
            task_description=task.task_description,
            sql_query=task.sql_query,
            created_by=request.created_by,
            execution_time_ms=execution_time
        )

        try:
            # Convert Pydantic model to dict for storage
            run_doc = response_data.model_dump()
            # Add request parameters and created_by for context
            run_doc["request_parameters"] = request.parameters
            run_doc["created_by"] = request.created_by
            
            saved_run = await self.run_repository.save(run_doc)
            
            # Update response with the generated run_task_id and created_date
            if saved_run:
                if "run_task_id" in saved_run:
                    response_data.run_task_id = saved_run["run_task_id"]
                if "created_date" in saved_run:
                    response_data.created_date = saved_run["created_date"]
                
        except Exception as e:
            # Log error but don't fail the request if logging fails
            logger.error(f"RunService: Failed to save SUCCESS run execution log: {str(e)}", exc_info=True)
            
        return response_data

    async def _save_failed_run(self, request: RunRequest, task: Any, error: Exception, start_time: float, rollback_query: str = "") -> str:
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
                "rollback_query": rollback_query,
                "task_description": task.task_description if task else None,
                "sql_query": task.sql_query if task else None,
                "execution_time_ms": execution_time,
                "request_parameters": request.parameters,
                "created_by": request.created_by
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
