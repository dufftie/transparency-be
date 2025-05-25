# Transparency Backend Guidelines

## Project Commands
- Start server: `uvicorn api.main:app --reload`
- Create migration: `alembic revision --autogenerate -m "Description"`
- Apply migrations: `alembic upgrade head`
- Run linting: `flake8 api db`
- Run type checking: `mypy api db`

## Code Style
- **Indentation**: 4 spaces, no tabs
- **Line length**: Max 120 characters
- **Imports**: Standard library → third-party → local (separated by blank lines)
- **Strings**: Use double quotes consistently
- **Naming**: snake_case for variables/functions, PascalCase for classes
- **Type hints**: Required for all function parameters and return types
- **Error handling**: Use FastAPI's HTTPException for API errors, try/except with proper logging
- **Documentation**: Docstrings for all functions, classes, and modules
- **Database**: Always use transactions, proper session management with commit/rollback

## Architecture
- Keep API endpoints in `/api/endpoints/`
- Database models in `/db/models/`
- Use DBConnector for database operations
- Isolate business logic from API layer