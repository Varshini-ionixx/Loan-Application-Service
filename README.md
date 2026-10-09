\# Loan Application Service



\## Overview



The Loan Application Service is a REST API built using FastAPI to manage customer information and loan applications. It uses PostgreSQL for data storage and SQLAlchemy for database operations.



\## Features



\* Create, retrieve, update, and delete customers.

\* Create, retrieve, update, and delete loan applications.

\* Validate customer information, including email and phone number.

\* Calculate monthly loan EMIs.

\* Handle errors such as missing customers, missing loans, and duplicate email addresses.

\* Manage database schema changes using Alembic.

\* Run automated tests using pytest.



\## Technology Stack



\* Python 3.12

\* FastAPI

\* SQLAlchemy

\* PostgreSQL

\* Alembic

\* Pydantic

\* pytest

\* Ruff

\* uv



\## Prerequisites



Install the following before running the application:



\* Python 3.12

\* uv

\* PostgreSQL, either locally or through Docker



\## Installation and Setup



\### 1. Install dependencies



From the project root directory, run:



```powershell

uv sync --dev

```



\### 2. Configure environment variables



Create a `.env` file in the project root with the following settings:



```dotenv

DATABASE\_URL=postgresql+psycopg://postgres:YOUR\_PASSWORD@localhost:5432/loan\_db

APP\_NAME="Loan Application Service"

DEBUG=false

```



Replace `YOUR\_PASSWORD` with your PostgreSQL password. Ensure the database exists and PostgreSQL is running.



Do not commit `.env` or actual database credentials to version control.



\### 3. Start the application



Run the following command:



```powershell

uv run uvicorn app.main:app --reload

```



The API will be available at:



\* \*\*Base URL:\*\* http://127.0.0.1:8000

\* \*\*Swagger UI:\*\* http://127.0.0.1:8000/docs

\* \*\*ReDoc:\*\* http://127.0.0.1:8000/redoc



\## API Endpoints



\### Customer APIs



| Method | Endpoint                       | Description                 |

| ------ | ------------------------------ | --------------------------- |

| POST   | `/api/customers/`              | Create a customer           |

| GET    | `/api/customers/`              | Retrieve all customers      |

| GET    | `/api/customers/{customer\_id}` | Retrieve a customer by ID   |

| PUT    | `/api/customers/{customer\_id}` | Replace customer details    |

| PATCH  | `/api/customers/{customer\_id}` | Partially update a customer |

| DELETE | `/api/customers/{customer\_id}` | Delete a customer           |



\### Loan APIs



| Method | Endpoint               | Description                    |

| ------ | ---------------------- | ------------------------------ |

| POST   | `/api/loans/`          | Create a loan application      |

| GET    | `/api/loans/`          | Retrieve all loan applications |

| GET    | `/api/loans/{loan\_id}` | Retrieve a loan by ID          |

| PUT    | `/api/loans/{loan\_id}` | Replace loan details           |

| PATCH  | `/api/loans/{loan\_id}` | Partially update a loan        |

| DELETE | `/api/loans/{loan\_id}` | Delete a loan                  |



\## Database Migrations



Check the current database migration revision:



```powershell

uv run alembic current

```



Check whether the database schema matches the SQLAlchemy models:



```powershell

uv run alembic check

```



For a new database that has been configured correctly, apply migrations using:



```powershell

uv run alembic upgrade head

```



\*\*Important:\*\* Back up existing databases before schema changes. Confirm the database schema and migration state before applying migrations to a database that already contains data.



\## Testing



Run the automated tests:



```powershell

uv run pytest

```



Check code quality using Ruff:



```powershell

uv run ruff check .

```



Check code formatting:



```powershell

uv run ruff format --check .

```



\## Security



\* Keep `.env` files and database backups out of Git.

\* Do not commit passwords, secrets, or production credentials.

\* Back up the database before making schema changes.
