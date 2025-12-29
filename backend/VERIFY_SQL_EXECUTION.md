# Verification Plan for SQL Execution Feature

## Overview
We have replaced the simulated query execution with actual SQL execution using SQLAlchemy and async drivers.

## New Dependencies
- SQLAlchemy
- pymysql (for MySQL)
- aiomysql (for Async MySQL)

To install these, run:
```bash
pip install -r requirements.txt
```

## Setup for Verification

1. **Verify Requirements**:
   Ensure `requirements.txt` contains:
   ```
   SQLAlchemy==2.0.25
   pymysql==1.1.0
   aiomysql==0.2.0
   ```

2. **MongoDB Data Setup**:
   Ensure you have a task and env_config set up (as per ENV_CONFIG_WALKTHROUGH.md).

   **Env Config (env_config collection)**:
   ```json
   {
       "config_key": "LK_MASTER_DB",
       "env": "PREPROD",
       "config_value": {
           "sql_db_host": "your-mysql-host",
           "sql_db_port": 3306,
           "sql_db_name": "lk_master",
           "sql_db_username": "user",
           "sql_db_password": "password"
       }
   }
   ```

   **Task (task_master collection)**:
   ```json
   {
       "task_id": "TSK-000001",
       "sql_query": "SELECT 1 as test_val",
       "db_name": "LK_MASTER_DB",
       ...
   }
   ```

3. **Execution Test**:
   Run the API:
   ```bash
   uvicorn main:app --reload
   ```

   Trigger the run:
   ```bash
   curl -X POST http://localhost:8000/api/v1/run \
     -H "Content-Type: application/json" \
     -d '{
       "task_id": "TSK-000001",
       "environment": "PREPROD"
     }'
   ```

   **Expected Result**:
   You should receive a JSON response with `data: [{"test_val": 1}]` and the logs should show:
   ```
   RunService: Executing query on lk_master
   RunService: Query returned 1 rows
   ```
