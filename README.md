# Loan Application Service

## Overview

The Loan Application Service is a REST API built with FastAPI to manage customer information and loan applications. It uses PostgreSQL for data storage, SQLAlchemy for database operations, Alembic for database migrations, and JWT-based authentication for protected loan operations.

## Features

- Create, retrieve, update, and delete customers.
- Create and manage loan applications.
- Validate customer information, including email and phone number.
- Calculate monthly loan EMIs.
- Authenticate users using JWT bearer tokens.
- Apply role-based access control for customers and loan officers.
- Restrict customers to viewing and managing only their authorized loan information.
- Manage database schema changes using Alembic.
- Run automated tests and code-quality checks through CI.

## Technology Stack

- **Language:** Python 3.12
- **API framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Database migrations:** Alembic
- **Data validation:** Pydantic and Pydantic Settings
- **Authentication:** JWT
- **Password hashing:** pwdlib
- **Testing:** pytest
- **Linting and formatting:** Ruff
- **Dependency management:** uv
- **Containerization:** Docker and Docker Compose

## Prerequisites

Install or configure the following before running the application locally:

- Python 3.12
- uv
- Docker Desktop with Docker Compose, or a compatible PostgreSQL installation
- Git

## Installation and Configuration

### 1. Clone the repository

```powershell
git clone <YOUR_REPOSITORY_URL>
cd Loan-Application-Service
```

Replace `<YOUR_REPOSITORY_URL>` with the actual repository URL.

If the repository is already cloned, open PowerShell in the project directory instead.

### 2. Install dependencies

```powershell
uv sync --dev
```

### 3. Configure environment variables

Create a `.env` file in the project root. Configure the variables required by `app/config.py`.

Example for running the application locally on your computer:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/loan_db
APP_NAME=Loan Application Service
DEBUG=false
JWT_SECRET_KEY=REPLACE_WITH_A_STRONG_RANDOM_SECRET
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Replace the example database password and JWT secret with your own values.

**Database URL configuration depends on where the application runs:**

- When running the API directly on your computer, use `localhost` if PostgreSQL is exposed on port `5432`.
- When running the API inside Docker and connecting to the separately running `loan_postgres` container, use `host.docker.internal` as the hostname, with port `5432`.

For example, the Docker database URL would use this format:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@host.docker.internal:5432/loan_db
```

Use the appropriate database URL for your execution environment. Never commit `.env` or real credentials to version control.

### 4. Start the database

The current Docker Compose configuration defines the `api` service. PostgreSQL runs separately in the `loan_postgres` container.

If the PostgreSQL container already exists and is running, you do not need to start another database container.

Check the running containers:

```powershell
docker ps
```

If you use a separate PostgreSQL installation, ensure that the database specified in `DATABASE_URL` exists and is accessible.

### 5. Apply database migrations

Run migrations from the project directory:

```powershell
uv run alembic upgrade head
```

Ensure PostgreSQL is running and that `DATABASE_URL` points to the correct database for your current environment.

### 6. Start the application locally

For local development:

```powershell
uv run uvicorn app.main:app --reload
```

The API should be available at:

- **Base URL:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

The root endpoint (`GET /`) returns a message confirming that the service is running.

## API Endpoints

The API endpoints are grouped under the `/api` prefix, except for the root health-check endpoint.

### General

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Check whether the application is running |

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/login` | Authenticate a user and obtain a JWT access token |

### Customers

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/customers/` | Create a customer |
| GET | `/api/customers/` | Retrieve customers |
| GET | `/api/customers/{customer_id}` | Retrieve a customer by ID |
| PUT | `/api/customers/{customer_id}` | Replace customer information |
| PATCH | `/api/customers/{customer_id}` | Partially update customer information |
| DELETE | `/api/customers/{customer_id}` | Delete a customer |

### Loans

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/loans/` | Apply for a loan |
| GET | `/api/loans/` | Retrieve loans accessible to the authenticated user |
| GET | `/api/loans/{loan_id}` | Retrieve a loan by ID |
| PUT | `/api/loans/{loan_id}` | Replace loan information |
| PATCH | `/api/loans/{loan_id}` | Partially update loan information |
| DELETE | `/api/loans/{loan_id}` | Delete a loan |

Protected endpoints require a valid bearer token. Actual permissions depend on the authenticated user's role.

Refer to the automatically generated Swagger documentation at `/docs` for request schemas, response models, and endpoint details.

## Authentication

The service uses JWT bearer authentication for protected operations.

### Logging in

**Endpoint:** `POST /api/auth/login`

The login endpoint accepts form data:

- `username`: the registered user's email address
- `password`: the user's password

Example using PowerShell:

```powershell
$body = @{
    username = "customer@example.com"
    password = "YOUR_TEST_PASSWORD"
}

$response = Invoke-RestMethod `
    -Method Post `
    -Uri "http://localhost:8000/api/auth/login" `
    -ContentType "application/x-www-form-urlencoded" `
    -Body $body

$token = $response.access_token
```

Use the returned token when calling protected endpoints:

```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod `
    -Method Get `
    -Uri "http://localhost:8000/api/loans/" `
    -Headers $headers
```

The token expires according to the configured access-token lifetime. Authenticate again to obtain a new token when necessary.

### Roles and permissions

**CUSTOMER**

- Can access loan information associated with their linked customer record.
- Can apply for a loan only for their linked customer record.
- Cannot update or delete loans through officer-only endpoints.

**OFFICER**

- Can view all loans.
- Can create loan applications for customers.
- Can update and delete loans through the officer-protected endpoints.

Requests to protected endpoints must include a valid JWT. The application enforces authorization based on the authenticated user's role and customer association.

## Database Migrations

Alembic manages database schema changes.

Apply all pending migrations:

```powershell
uv run alembic upgrade head
```

Display the current database revision:

```powershell
uv run alembic current
```

View migration history:

```powershell
uv run alembic history
```

Generate a migration from model changes:

```powershell
uv run alembic revision --autogenerate -m "describe schema change"
```

Review generated migration files before applying them. Autogenerated migrations should always be checked for correctness.

Check whether model changes require a migration:

```powershell
uv run alembic check
```

Back up important database data before applying schema changes, especially in shared or production environments.

## Testing

Run the automated test suite:

```powershell
uv run pytest
```

Run Ruff lint checks:

```powershell
uv run ruff check .
```

Check code formatting:

```powershell
uv run ruff format --check .
```

To format the code if needed:

```powershell
uv run ruff format .
```

Resolve test failures, lint errors, and formatting issues before submitting changes.

## Docker Setup

The current `docker-compose.yml` defines the `api` service. The `loan_postgres` database container is managed separately.

Build and start the API service:

```powershell
docker compose up --build -d
```

List services managed by Compose:

```powershell
docker compose ps
```

View API logs:

```powershell
docker compose logs api
```

Follow API logs continuously:

```powershell
docker compose logs -f api
```

View PostgreSQL logs:

```powershell
docker logs loan_postgres
```

The API container runs the Alembic migrations before starting Uvicorn. Ensure that the database is running and reachable using the database URL configured for Docker.

## Project Structure

```text
Loan-Application-Service/
├── .github/
│   └── workflows/
├── alembic/
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── base.py
│   ├── config.py
│   ├── database.py
│   ├── exceptions.py
│   ├── logging_config.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   ├── repositories/
│   │   ├── customer_repository.py
│   │   └── loan_repository.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── customers.py
│   │   └── loans.py
│   └── services/
│       ├── customer_service.py
│       └── loan_service.py
├── scripts/
├── src/
├── tests/
├── .dockerignore
├── .env.example
├── .gitignore
├── .python-version
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── README.md
└── uv.lock
```

The tree shows the main application files and repository directories. The `scripts/`, `src/`, `alembic/`, and `tests/` directories may contain additional files not listed here.

The `.env` file contains local configuration and should not be committed. Database backup files and generated caches are also excluded from this documentation tree.

## Security

- Store passwords as secure hashes, never as plaintext.
- Use a strong, randomly generated JWT secret.
- Keep `.env` files, passwords, tokens, and database credentials out of version control.
- Validate incoming request data with the application's schemas.
- Enforce authentication and authorization on protected endpoints.
- Use HTTPS and securely managed secrets in production.
- Use database credentials with only the permissions the application needs.
- Back up important data before schema changes or database maintenance.
- Avoid logging passwords, authentication tokens, or other sensitive information.

## Continuous Integration

GitHub Actions runs automated quality checks when changes are pushed to configured branches or when a pull request targets `main`.

The workflow checks:

- Ruff linting.
- Ruff formatting.
- Automated tests using pytest.

Review the workflow run in the repository's GitHub Actions tab if a check fails.

## Troubleshooting

### Missing environment variables

Verify that `.env` exists in the project root and contains the variables required by `app/config.py`. Confirm that the variable names match the settings defined by the application.

### Database connection errors

Check that PostgreSQL is running, the database exists, and the credentials in `DATABASE_URL` match the configured PostgreSQL credentials.

If the application runs inside Docker, use `host.docker.internal` to connect to the separately running PostgreSQL container. When running the API directly on your computer, use `localhost` if PostgreSQL is exposed on port `5432`.

### Migration errors

Check the current database revision and review migration history before applying further migrations. Back up existing data before making schema changes.

### API container keeps restarting

Inspect the API container logs:

```powershell
docker compose logs api
```

Inspect the PostgreSQL container logs:

```powershell
docker logs loan_postgres
```

Check the environment configuration and database connectivity if the API cannot start.

## Stopping the Application

Stop the API service managed by Docker Compose:

```powershell
docker compose down
```

The separately managed PostgreSQL container will not necessarily stop when you run this command.

To stop PostgreSQL without deleting its persisted data:

```powershell
docker stop loan_postgres
```

Only remove a database container or volume if you intentionally want to delete the associated database data. Confirm where your PostgreSQL data is stored before removing any container or volume.

## License

Add the applicable license information here if the project is distributed under a specific license.