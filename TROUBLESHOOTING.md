# Troubleshooting Guide

## Common Errors

### 1. SQL Syntax Error
**Error**: `(pymysql.err.ProgrammingError) (1064, "You have an error in your SQL syntax...")`
**Cause**: The SQL query stored in the task is invalid.
**Fix**: Update the task with a valid SQL query using the `PUT /api/v1/tasks/{task_id}` endpoint.

**Example Fix**:
If your query is `SELECT * LK_LOAN_MASTER ...` (missing FROM), update it:

```bash
curl -X PUT http://localhost:8000/api/v1/tasks/TSK-000001 \
  -H "Content-Type: application/json" \
  -d '{
    "sql_query": "SELECT * FROM LK_LOAN_MASTER where L_APPLICATION_ID = 'LAI-119154893'"
  }'
```

### 2. Connection Error
**Error**: `ValueError: too many values to unpack` or connection failures.
**Cause**: Invalid connection string format or unreachable database.
**Fix**: Check `env_config` collection for correct host, port, username, password. Ensure the `config_key` matches the task's `db_name`.

### 3. Missing Configuration
**Error**: `Configuration for database '...' in environment '...' not found`
**Cause**: No document in `env_config` matches the requested `confg_key` and `env`.
**Fix**: Add the missing configuration to MongoDB.
