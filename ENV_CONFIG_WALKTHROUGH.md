# Environment Configuration Feature
## Overview
Implemented a dynamic database configuration system using a new `env_config` collection in MongoDB. This allows fetching environment-specific database credentials (e.g., for PREPROD, PROD) at runtime.

## Changes

### 1. Database Configuration
**File**: `app/configs/database.py`
- Added `ENV_CONFIG` to `Collections`.
- Added `get_env_config_collection()` helper.

### 2. New Repository
**File**: `app/repositories/env_config_repository.py`
- Created `EnvConfigRepository`.
- Implemented `get_config(config_key, env)` to fetch connection details dynamically.

### 3. Service Update
**File**: `app/services/run_service.py`
- Injected `EnvConfigRepository`.
- Replaced mock connection logic with `await self.env_config_repository.get_config(...)`.
- Implemented connection string construction for MySQL (`mysql+pymysql://...`).

### 4. Logging
**File**: `main.py`
- Added logging configuration for `app.repositories.env_config_repository`.

## Usage
To use this feature, insert a document into the `env_config` collection:

```json
{
    "config_key": "LK_MASTER_DB",
    "env": "PREPROD",
    "config_value": {
        "sql_db_host": "host.example.com",
        "sql_db_port": 3306,
        "sql_db_name": "lk_master",
        "sql_db_username": "user",
        "sql_db_password": "password"
    }
}
```

Then trigger the run endpoint with the matching `db_name` (mapped to `config_key`) and `environment`:

```bash
curl -X POST http://localhost:8000/api/v1/run \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "TSK-000001",
    "environment": "PREPROD"
  }'
```
