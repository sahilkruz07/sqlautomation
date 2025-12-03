# SQL Automation API

A FastAPI skeleton project with a clean architecture structure.

## Project Structure

```
sqlautomation/
├── main.py                 # Application entry point
├── app/
│   ├── controllers/        # API route handlers
│   ├── services/          # Business logic layer
│   ├── repositories/      # Data access layer
│   ├── models/            # Pydantic models and schemas
│   ├── configs/           # Configuration files
│   └── utils/             # Utility functions and helpers
├── requirements.txt       # Python dependencies
└── .env.example          # Environment variables template
```

## Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Running the Application

### Development Mode (with auto-reload)

```bash
uvicorn main:app --reload
```

Or run directly:

```bash
python main.py
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Documentation

Once the application is running, visit:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Architecture

This project follows a layered architecture:

- **Controllers:** Handle HTTP requests and responses
- **Services:** Contain business logic and orchestrate operations
- **Repositories:** Handle data access and database operations
- **Models:** Define data structures and validation schemas
- **Configs:** Manage application configuration
- **Utils:** Provide reusable utility functions

## Adding New Features

1. Create models in `app/models/`
2. Create repository in `app/repositories/`
3. Create service in `app/services/`
4. Create controller in `app/controllers/`
5. Register router in `main.py`

## Example

See the example files in each directory for reference implementations.
