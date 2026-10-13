# Loan Application Service

## Overview

The Loan Application Service is a REST API built with FastAPI to manage customer information and loan applications. It uses PostgreSQL for data storage, SQLAlchemy for database operations, Alembic for database migrations, and JWT-based authentication for protected loan operations.

## Features

- Create, retrieve, update, and delete customers.
- Create and manage loan applications.
- Validate customer information, including email and phone number.
- Calculate monthly loan EMIs.
- Authenticate users with JWT access tokens.
- Enforce role-based permissions for customers and officers.
- Restrict customers to viewing and applying for loans linked to their own customer accounts.
- Handle errors such as missing records, duplicate emails, invalid loan tenures, and unauthorized requests.
- Manage database schema changes using Alembic.
- Run automated tests using pytest.
- Check code quality and formatting using Ruff.

## Technology Stack

- Python 3.12
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic and Pydantic Settings
- PyJWT
- pwdlib
- pytest
- Ruff
- uv

## Prerequisites

Install the following before running the application:

- Python 3.12
- uv
- PostgreSQL, locally or through Docker
- Git

## Installation and Setup

### 1. Clone the repository

```powershell
git clone <repository-url>
cd Loan-Application-Service
```

Replace `<repository-url>` with your repository URL.

### 2. Install dependencies

```powershell
uv sync --dev
```

### 3. Configure environment variables

Create a `.env` file in the project root.

Example configuration:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/loan_db
APP_NAME="Loan Application Service"
DEBUG=false
JWT_SECRET_KEY="REPLACE_WITH_A_LONG_RANDOM_SECRET"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Replace the database credentials with your local PostgreSQL settings. Ensure the `loan_db` database exists and PostgreSQL is running.

Use a strong, randomly generated JWT secret for local development and production. Never commit `.env` files or real credentials to Git.

The environment variable names must match the settings defined in `app/config.py`.

### 4. Apply database migrations

Check the current migration revision:

```powershell
uv run alembic current
```

Apply migrations when setting up a new, correctly configured database:

```powershell
uv run alembic upgrade head
```

Back up existing databases and verify the target database before applying migrations.

### 5. Start the application

```powershell
uv run uvicorn app.main:app --reload
```

The API will be available at:

- **Base URL:** http://127.0.0.1:8000
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

## Authentication

The login endpoint accepts OAuth2 password-form fields. The email address is supplied in the `username` field.

### Login

**Endpoint:** `POST /api/auth/login`

Form fields:

- `username`: registered user's email address
- `password`: user's password

Example using PowerShell:

```powershell
$body = @{
    username = "customer@example.com"
    password = "YOUR_TEST_PASSWORD"
}

$response = Invoke-RestMethod `
    -Method Post `
    -Uri "http://127.0.0.1:8000/api/auth/login" `
    -ContentType "application/x-www-form-urlencoded" `
    -Body $body

$token = $response.access_token
```

Use the returned access token in requests to protected loan endpoints:

```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod `
    -Method Get `
    -Uri "http://127.0.0.1:8000/api/loans/" `
    -Headers $headers
```

Access tokens expire according to the configured token lifetime. Log in again to obtain a new token when necessary.

### Roles and permissions

- **CUSTOMER:** Can create loan applications for their linked customer record and view their own loans.
- **OFFICER:** Can view all loans, create loan applications, update loans, and delete loans.
- Requests to protected endpoints without a valid token are rejected.
- Customers cannot update or delete loans through the protected loan endpoints.

Customer accounts must be linked to an existing customer record to use customer-specific loan operations.

## API Endpoints

### Authentication APIs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/login` | Authenticate and obtain an access token |

### Customer APIs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/customers/` | Create a customer |
| GET | `/api/customers/` | Retrieve customers |
| GET | `/api/customers/{customer_id}` | Retrieve a customer by ID |
| PUT | `/api/customers/{customer_id}` | Replace customer details |
| PATCH | `/api/customers/{customer_id}` | Partially update a customer |
| DELETE | `/api/customers/{customer_id}` | Delete a customer |

### Loan APIs

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/loans/` | Create a loan application |
| GET | `/api/loans/` | Retrieve permitted loan applications |
| GET | `/api/loans/{loan_id}` | Retrieve a permitted loan by ID |
| PUT | `/api/loans/{loan_id}` | Update a loan; officer access required |
| PATCH | `/api/loans/{loan_id}` | Partially update a loan; officer access required |
| DELETE | `/api/loans/{loan_id}` | Delete a loan; officer access required |

Use Swagger UI at `/docs` to explore request schemas and try the endpoints. For protected operations, authorize with a bearer token.

## Database Migrations

View the current revision:

```powershell
uv run alembic current
```

View migration history:

```powershell
uv run alembic history
```

Check whether the database schema matches the SQLAlchemy models:

```powershell
uv run alembic check
```

Apply migrations:

```powershell
uv run alembic upgrade head
```

Back up existing databases before schema changes.

## Testing

Run the automated test suite:

```powershell
uv run pytest
```

Check code quality:

```powershell
uv run ruff check .
```

Verify code formatting:

```powershell
uv run ruff format --check .
```

## Project Structure

```text
Loan-Application-Service/
├── alembic/
│   └── versions/
├── app/
│   ├── routers/
│   │   ├── auth.py
│   │   ├── customers.py
│   │   └── loans.py
│   ├── services/
│   ├── auth.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── security.py
├── scripts/
│   └── create_test_user.py
├── tests/
├── .env
├── .gitignore
├── alembic.ini
├── pyproject.toml
└── README.md
```

## Security

- Never commit passwords, `.env` files, database credentials, or production secrets.
- Store password hashes rather than plaintext passwords.
- Use a strong JWT signing secret and keep it private.
- Use HTTPS and appropriate secret management in production.
- Back up the database before making schema changes.
- Use least-privilege database credentials and restrict access to protected endpoints.
