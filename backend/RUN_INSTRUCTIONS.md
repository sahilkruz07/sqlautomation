# Task Execution Feature

## Overview
Implemented a new feature to execute task queries in specific environments (DEV, QA, PROD).

## Changes

### 1. New Models
**File**: [`app/models/run_model.py`](app/models/run_model.py)
- `RunRequest`: Accepts `task_id`, `environment`, and optional `parameters`.
- `RunResponse`: Returns execution status, data, and timing.

### 2. New Service
**File**: [`app/services/run_service.py`](app/services/run_service.py)
- `execute_task`: Orchestrates the execution flow.
  1. Fetches task details using `TaskService`.
  2. Resolves connection string based on `db_name` and `environment` (Mocked).
  3. Simulates query execution (Mocked).
- `_get_connection_string`: Returns mock connection strings for `sales_db` and `inventory_db`.
- `_simulate_execution`: returns dummy data after a short delay.

### 3. New Controller
**File**: [`app/controllers/run_controller.py`](app/controllers/run_controller.py)
- `POST /api/v1/run`: Endpoint to trigger task execution.
- Includes error handling and logging consistent with the rest of the app.

### 4. Main Application
**File**: [`main.py`](main.py)
- Registered `run_router`.
- Added logging configuration for `app.controllers.run_controller` and `app.services.run_service`.

## Usage

### Run a Task
**Endpoint**: `POST http://localhost:8000/api/v1/run`

**Request Body**:
```json
{
  "task_id": "TSK-000001",
  "environment": "DEV",
  "parameters": {
    "limit": 10
  }
}
```

**Response**:
```json
{
  "task_id": "TSK-000001",
  "status": "success",
  "environment": "DEV",
  "message": "Query executed successfully",
  "data": [
    {
      "id": 1,
      "result": "mock_data_row_1",
      "query_snippet": "SELECT * FROM sales ..."
    }
  ],
  "execution_time_ms": 500.21
}
```
