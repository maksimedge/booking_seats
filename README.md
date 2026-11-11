# Café Table Booking Project

A backend application for booking tables at cafés.

The service provides a REST API for managing users, cafés, tables, time slots, and bookings, with role-based access control, image uploads, and background notifications.

The project is built with FastAPI, asynchronous SQLAlchemy, and PostgreSQL.

## Key Features

- User registration and JWT authentication;
- User roles: `ADMIN`, `MANAGER`, `USER`;
- Café management;
- Table and seating capacity management;
- Time slot management;
- Creating, viewing, updating, and cancelling bookings;
- Table and time slot availability checks;
- Capacity checks for selected tables;
- Image uploads and retrieval;
- Background notifications to managers when bookings are created or updated;
- Reminders to users about upcoming bookings;
- Centralized logging;
- A consistent API error format;
- Demo database seeding;
- Containerization and CI/CD.

## Technology Stack

### Backend

- Python 3.12
- FastAPI
- Uvicorn
- Pydantic
- Pydantic Settings
- SQLAlchemy 2.0 Async
- asyncpg
- Alembic
- PostgreSQL 17

### Authentication and Security

- JWT
- python-jose
- pwdlib
- Argon2

### Background Tasks and Notifications

- Celery
- RabbitMQ
- Celery Beat
- Flower
- SMTP
- Mailpit for local testing of email notifications

### File Handling

- Pillow
- aiofiles
- python-multipart

### Infrastructure and Code Quality

- Docker
- Docker Compose
- Dev Containers
- Nginx
- GitHub Actions
- uv
- Ruff
- Pre-commit
- Loguru

## Project Architecture

The project is organized into functional modules. Each main module contains its own models, schemas, routers, and business logic.

```text
src/
├── api/                 # Main API router
├── auth/                # Authentication and JWT
├── bookings/            # Bookings
├── cafes/               # Cafés
├── core/                # Shared settings and infrastructure
│   ├── celery_app.py
│   ├── celery_db.py
│   ├── db.py
│   ├── exception_handler.py
│   ├── exceptions.py
│   ├── logger.py
│   ├── middleware.py
│   ├── security.py
│   └── settings.py
├── media/               # Image uploads and retrieval
├── migrations/          # Alembic migrations
├── notifications/       # Email notifications and Celery tasks
├── scripts/             # Seed scripts
├── tables/              # Tables
├── time_slots/          # Time slots
├── users/               # Users
├── alembic.ini
└── main.py
```

The project root also contains:

```text
.devcontainer/           # VS Code Dev Containers development environment
.github/workflows/       # GitHub Actions
infra/                   # Docker Compose and Nginx for running/deploying the app
Dockerfile
entrypoint.sh
pyproject.toml
ruff.toml
uv.lock
```

## API

After starting the application locally, it is available at:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

OpenAPI schema:

```text
http://localhost:8000/openapi.json
```

Health check:

```http
GET /health
```

Example response:

```json
{
  "status": "ok"
}
```

## Main API Modules

### Users and Authentication

Supported features:

- User login and JWT issuance;
- Token expiration checks;
- Retrieving and updating user data;
- Role-based access control.

### Cafés

Supported features:

- Creating cafés;
- Listing cafés;
- Retrieving a café by ID;
- Updating café details;
- Filtering by active status;
- Assigning managers;
- Linking an image.

### Tables

Supported features:

- Creating a table at a café;
- Listing tables;
- Retrieving an individual table;
- Updating seating capacity, description, and active status;
- Filtering by active status;
- Checking that a table belongs to the café.

### Time Slots

Supported features:

- Creating time slots;
- Listing time slots;
- Retrieving a time slot by ID;
- Updating time slots;
- Validating times;
- Preventing overlapping and duplicate time slots.

### Bookings

Supported features:

- Creating bookings;
- Listing bookings;
- Retrieving a booking by ID;
- Updating bookings;
- Cancelling bookings;
- Booking multiple tables and time slots;
- Checking table availability for the selected date and time slot;
- Checking the number of guests against the total seating capacity;
- Restricting changes to past and completed bookings.

### Media API

Supported features:

- Uploading images;
- Validating file type and size;
- Converting images to JPG;
- Saving images with UUID identifiers;
- Retrieving saved images by ID.

## Roles and Permissions

The application uses three roles:

| Role | Permissions |
|---|---|
| `USER` | Manage their own bookings and view available data |
| `MANAGER` | Manage café resources and bookings they have access to |
| `ADMIN` | Extended administrative access |

Additional permission checks are performed through API dependencies and module business logic.

## Booking Business Logic

The following checks are performed when creating or updating a booking:

- The café exists and is active;
- The booking date is not in the past;
- The number of guests is at least 1;
- The selected tables and time slots exist;
- No table–time slot pair is duplicated;
- The table is not reserved by another booking for the same date and time slot;
- The total seating capacity is sufficient for the number of guests;
- Past bookings cannot be updated or cancelled;
- Completed or cancelled bookings cannot be updated or cancelled again.

## Notifications and Background Tasks

Celery and RabbitMQ are used for background processing.

Implemented features:

- Manager notifications when a booking is created;
- Manager notifications when a booking is updated;
- Periodic checks for upcoming bookings;
- Email reminders to users;
- Duplicate reminder prevention;
- Retries for temporary SMTP errors.

Celery Beat periodically queues a task to check bookings.
Celery Worker retrieves the task from RabbitMQ and executes the notification business logic.

### Starting Celery Worker

From the `src` directory:

```bash
celery -A core.celery_app:booking_celery worker --loglevel=info
```

### Starting Celery Beat

```bash
celery -A core.celery_app:booking_celery beat --loglevel=info
```

### Starting Flower

```bash
celery -A core.celery_app:booking_celery flower --port=5555
```

Flower:

```text
http://localhost:5555
```

## RabbitMQ

The DevContainer uses the following image:

```text
rabbitmq:3-management
```

RabbitMQ Management UI:

```text
http://localhost:15672
```

The default values for local development are:

```text
RABBITMQ_USER=booking
RABBITMQ_PASSWORD=booking_password
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
```

## Email and Mailpit

Mailpit is used for local email testing.

SMTP within the Docker network:

```text
mailpit:1025
```

Mailpit Web UI:

```text
http://localhost:8025
```

During local development, emails are not sent to an external email service. They can be viewed in the Mailpit interface.

## Logging

The project uses centralized logging based on Loguru.

The following are logged:

- Application startup and shutdown;
- HTTP requests and responses;
- Errors;
- Authentication operations;
- Business actions;
- Entity creation and updates;
- Booking operations;
- Notification delivery.

The logging context may include the user's ID and username.

Application logs are saved to:

```text
src/logs/app.log
```

## Error Format

The application uses a unified error-handling mechanism.

Business logic errors are returned in the following format:

```json
{
  "code": 400,
  "message": "Error description"
}
```

This is implemented using a custom application exception class and centralized FastAPI exception handlers.

A separate handler is used for input validation errors.

## Environment Variables

Create the following file:

```text
infra/.env
```

Example:

```env
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=db_name
POSTGRES_SERVER=db
POSTGRES_PORT=5432

# JWT
SECRET_KEY=change_me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# RabbitMQ
RABBITMQ_USER=booking
RABBITMQ_PASSWORD=booking_password
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672

# Notifications
REMINDER_BEFORE_PERIOD_HOURS=1
EMAIL_FROM_ADDRESS=booking@cafe.local
```

> Do not commit real secrets or production passwords to the repository. The `.env` file must be excluded from Git.

## Development Setup

### Requirements

Install the following:

- Docker Desktop or Docker Engine;
- Visual Studio Code;
- The Dev Containers extension.

### Starting the DevContainer

1. Clone the repository.
2. Create `infra/.env`.
3. Open the project in VS Code.
4. Press `Ctrl + Shift + P`.
5. Select `Dev Containers: Reopen in Container`.

This starts:

- The application container;
- PostgreSQL;
- RabbitMQ;
- Mailpit.

The project source code is mounted at:

```text
/workspace
```

## Starting FastAPI

After opening the DevContainer:

```bash
cd src
python main.py
```

The application starts at:

```text
http://localhost:8000
```

You can also start the application using the VS Code `Run and Debug` configuration.

## Alembic Migrations

Run these commands from the `src` directory.

### Apply Existing Migrations

```bash
alembic upgrade head
```

### Create a New Migration

```bash
alembic revision --autogenerate -m "migration description"
```

### Roll Back the Latest Migration

```bash
alembic downgrade -1
```

## Demo Data

A seed script is provided to populate the database.

Run the following from the `src` directory:

```bash
PYTHONPATH=/workspace/src python scripts/seed_demo.py
```

On successful completion:

```text
Demo data loaded successfully.
```

The seed script can be run multiple times. Existing demo data is cleared before new demo data is created.

### Demo Accounts

Password for demo users:

```text
Demo123!
```

| Email | Role | Status |
|---|---|---|
| admin@example.com | ADMIN | Active |
| manager1@example.com | MANAGER | Active |
| manager2@example.com | MANAGER | Active |
| user1@example.com | USER | Active |
| user2@example.com | USER | Active |
| user3@example.com | USER | Active |
| user4@example.com | USER | Active |
| user5@example.com | USER | Active |
| blocked@example.com | USER | Inactive |

The user's email address is used to log in.

Example credentials:

```json
{
  "login": "user1@example.com",
  "password": "Demo123!"
}
```

## Dependency Management

The project uses `uv` as its dependency manager.

Install dependencies:

```bash
uv sync
```

The `uv.lock` file locks exact dependency versions and must be committed to Git.

## Ruff and Pre-commit

Ruff is used to check code quality and style.

Check the project:

```bash
ruff check .
```

Automatically fix issues where possible:

```bash
ruff check . --fix
```

Run pre-commit hooks:

```bash
pre-commit run --all-files
```

## Docker

Local development uses:

```text
.devcontainer/docker-compose.yml
```

It starts the following services:

- `app`;
- `db`;
- `rabbitmq`;
- `mailpit`.

A production-like environment uses:

```text
infra/docker-compose.production.yml
```

The provided configuration includes:

- The application;
- PostgreSQL;
- Nginx.

> If background notifications are required in production, RabbitMQ, Celery Worker, and Celery Beat must also be running, either as additional Docker services or as separate infrastructure processes/services.

## CI/CD

The project uses GitHub Actions.

Workflow files are located in:

```text
.github/workflows/
├── main.yml
└── style_check.yml
```

CI/CD automates project checks, Docker image builds, and deployment.

The application's production configuration is located in:

```text
infra/
```

It includes Docker Compose and the Nginx configuration.

## Testing

Automated tests have not been implemented in the current version of the project.

API functionality is tested manually through Swagger/OpenAPI:

```text
http://localhost:8000/docs
```

The following can also be used to check the infrastructure:

- RabbitMQ Management UI;
- Flower;
- Mailpit;
- The application's health check endpoint.

## Current Status

The project is intended for educational team development.

A public production instance is not currently maintained. To use the API, run the project locally.
