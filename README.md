# Loan Application Service

## Overview

The Loan Application Service is a REST API built with FastAPI to manage customer information and loan applications. It uses PostgreSQL for data storage, SQLAlchemy for database operations, Alembic for database migrations, and JWT bearer tokens for authentication and authorization.

## Features

- Create, retrieve, update, and delete customers.
- Create and manage loan applications.
- Validate customer information.
- Calculate monthly loan EMIs.
- Authenticate users using JWT bearer tokens.
- Enforce role-based access control for customers and loan officers.
- Restrict customers to their authorized loan information.
- Filter loans by status and paginate loan results.
- Manage database schema changes using Alembic.
- Run automated tests and code-quality checks through CI.

## Technology Stack

- **Language:** Python 3.12
- **API framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Database migrations:** Alembic
- **Validation:** Pydantic and Pydantic Settings
- **Authentication:** JWT
- **Password hashing:** pwdlib
- **Testing:** pytest
- **Linting and formatting:** Ruff
- **Dependency management:** uv
- **Containerization:** Docker and Docker Compose

## Prerequisites

Install or configure:

- Python 3.12 and uv
- Docker Desktop with Docker Compose, or a compatible PostgreSQL installation
- Git

## Installation and Configuration

### 1. Clone the repository

```powershell
git clone <YOUR_REPOSITORY_URL>
cd Loan-Application-Service
```

Replace `<YOUR_REPOSITORY_URL>` with your repository URL. If the project is already cloned, open PowerShell in its project directory.

### 2. Install dependencies

```powershell
uv sync --dev
```

### 3. Configure environment variables

Create a `.env` file in the project root using `.env.example` as a starting point:

```powershell
Copy-Item .env.example .env
```

Update the values in `.env`. A typical configuration is:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/loan_db
APP_NAME="Loan Application Service"
DEBUG=false
JWT_SECRET_KEY=YOUR_RANDOM_SECRET
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Use your actual database credentials and a strong, randomly generated JWT secret. Do not commit `.env` or real credentials to version control.

**Database connection settings depend on where the API runs:**

- **API running directly on your computer:** use `localhost` if PostgreSQL is exposed on port `5432`.
- **API running inside Docker with PostgreSQL on the host:** use `host.docker.internal` as the database hostname.
- **API and PostgreSQL running in the same Compose network:** use the PostgreSQL service name as the hostname.

The current `docker-compose.yml` defines only the `api` service. It expects PostgreSQL to be running separately.

For the current Docker setup, the database URL should use this format:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@host.docker.internal:5432/loan_db
```

URL-encode special characters in the database password when necessary.

### 4. Prepare the database

Ensure PostgreSQL is running and that the `loan_db` database exists with credentials matching `DATABASE_URL`.

Check running containers:

```powershell
docker ps
```

If using the existing PostgreSQL container, verify that it is running and that its port is accessible from the API container.

### 5. Apply database migrations

For local development, run:

```powershell
uv run alembic upgrade head
```

Make sure `DATABASE_URL` points to the intended database before applying migrations.

### 6. Start the application locally

```powershell
uv run uvicorn app.main:app --reload
```

The default local URLs are:

- **Base URL:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

The root endpoint (`GET /`) returns a message confirming that the service is running.

## API Endpoints

All API endpoints are grouped under `/api`, except for the root endpoint.

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

### Loan list filtering and pagination

The loan list endpoint supports query parameters:

- `status`: filter loans by status.
- `page`: page number, starting at `1`.
- `size`: number of records per page.

For example:

```text
GET /api/loans/?page=1&size=10
GET /api/loans/?status=approved&page=1&size=10
```

Use the valid loan status values defined by the application. The API enforces authorization so users only receive loans they are permitted to access.

### Loan decision rules

Customers carry an eligibility profile: `age`, `monthly_income`, `existing_emi` and `credit_score`. Each new loan application is decided in this priority order:

1. **Profile incomplete:** the request is refused with `400` and the missing fields are listed.
2. **REJECTED** if any rule fails, with every failed rule listed in `rejection_reason`:
   - age is not between 21 and 60
   - monthly income is below 25,000
   - credit score is below 650
   - existing EMI plus the new EMI is more than 50% of monthly income
3. **REFERRED** to an officer if the credit score is between 650 and 699, or the amount is above 10,00,000. The reason is stored in `rejection_reason`.
4. **APPROVED** otherwise.

The interest rate depends on tenure: 12 months 10%, 24 months 11%, 36 months 12%, 48 and 60 months 13%. Other tenures are refused with `400`.

Refer to Swagger UI at `/docs` for the complete request schemas, response models, validation rules, and available endpoint details.

## Authentication

The service uses JWT bearer authentication for protected operations.

### Logging in

**Endpoint:** `POST /api/auth/login`

The login endpoint accepts form data:

- `username`: the registered user's email address
- `password`: the user's password

PowerShell example:

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

Use the returned token for protected requests:

```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod `
    -Method Get `
    -Uri "http://localhost:8000/api/loans/" `
    -Headers $headers
```

The token expires according to the configured access-token lifetime. Log in again when a new token is needed.

### Roles and permissions

**CUSTOMER**

- Can access loan information associated with their linked customer record.
- Can apply for a loan for their linked customer record.
- Cannot perform officer-only loan operations.

**OFFICER**

- Can view all loans.
- Can create loan applications for customers.
- Can update and delete loans through authorized officer operations.

Actual permissions are enforced by the application's authentication and authorization logic.

## Database Migrations

Alembic manages database schema changes.

Apply pending migrations:

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

Generate a migration after model changes:

```powershell
uv run alembic revision --autogenerate -m "describe schema change"
```

Review autogenerated migrations before applying them.

Check whether model changes require a migration:

```powershell
uv run alembic check
```

Back up important data before schema changes, particularly in shared or production environments.

## Testing and Code Quality

Run the automated test suite:

```powershell
uv run pytest -v
```

Run Ruff lint checks:

```powershell
uv run ruff check .
```

Check formatting:

```powershell
uv run ruff format --check .
```

Format files if needed:

```powershell
uv run ruff format .
```

Resolve test failures, lint errors, and formatting issues before submitting changes.

## Docker Setup

The current Docker Compose configuration defines the `api` service only. PostgreSQL must be running separately and reachable using the configured `DATABASE_URL`.

Configure `.env` before starting the service.

Build and start the API:

```powershell
docker compose up --build -d
```

List Compose containers:

```powershell
docker compose ps
```

View API logs:

```powershell
docker compose logs --tail=100 api
```

Follow API logs:

```powershell
docker compose logs -f api
```

View logs for the separately managed PostgreSQL container:

```powershell
docker logs loan_postgres
```

The API container runs Alembic migrations before starting Uvicorn. If the database is unavailable or the migration fails, the API may fail to start. Check the logs and database connection settings when troubleshooting.

### Port conflicts

The default Compose configuration maps host port `8000` to container port `8000`.

If another application is already using port `8000`, change the host-side port mapping in `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"
```

The API can then be accessed at `http://localhost:8001`. The port inside the container remains `8000`.

## Project Structure

```text
Loan-Application-Service/
├── .github/
│   └── workflows/
├── alembic/
├── app/
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
│   ├── routers/
│   └── services/
├── scripts/
├── src/
├── tests/
├── .dockerignore
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── README.md
└── uv.lock
```

## Security

- Store passwords as secure hashes, never as plaintext.
- Use a strong, randomly generated JWT secret.
- Keep `.env`, passwords, access tokens, and database credentials out of version control.
- Validate incoming request data.
- Enforce authentication and authorization on protected endpoints.
- Use HTTPS and securely managed secrets in production.
- Use database credentials with only the permissions the application needs.
- Back up important data before schema changes or database maintenance.
- Avoid logging passwords, authentication tokens, or other sensitive information.

## Continuous Integration

GitHub Actions runs automated quality checks for pushes and pull requests covered by the configured workflow.

The workflow checks:

- Ruff linting.
- Ruff formatting.
- Automated tests using pytest.

Review the repository's GitHub Actions tab to confirm the latest workflow result.

## Troubleshooting

### Missing environment variables

Ensure `.env` exists in the project root and contains the variables required by the application configuration. Check that every variable is on its own line and that names match the application's settings.

### Database connection errors

Verify that PostgreSQL is running, `loan_db` exists, and the database credentials match `DATABASE_URL`.

For an API running inside Docker that connects to PostgreSQL on the host, use `host.docker.internal` rather than `localhost`.

### Migration errors

Check the database connection and review the current Alembic revision and migration history. Back up important data before making schema changes.

### API container keeps restarting

Inspect the API logs:

```powershell
docker compose logs --tail=100 api
```

Check the database logs if PostgreSQL is managed separately:

```powershell
docker logs loan_postgres
```

Verify environment variables, database connectivity, and migration status.

## Stopping the Application

Stop the API service managed by Docker Compose:

```powershell
docker compose down
```

This does not necessarily stop the separately managed PostgreSQL container.

To stop that container without explicitly deleting it:

```powershell
docker stop loan_postgres
```

Do not remove database containers or volumes unless you intentionally want to delete the associated data.

## License

Add the applicable license information if the project is distributed under a specific license.