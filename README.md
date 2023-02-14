# FastAPI Complaint System

The Complaint System is a backend service for a complaint management system. It
provides a REST API to manage complaint tickets, users, and other information.

## Setting Up

To set up the project, you need to have the following installed on your
computer:

- Python 3.8+
- [Poetry][poetry] (for dependencies management)

Clone the repository and navigate to the project directory. Then run the
following commands to install the dependencies:

```bash
poetry install
```

To install the dependencies required to use PostgreSQL as the database, run the
following command:

```bash
poetry install --extras postgres
```

## Configuration

The application uses environment variables to set its configuration. You can
find an example configuration in the `.env.example` file. You can create a new
`.env` file based on the example file and configure it for your use case.

The `src/app/core/settings.py` file contains the configuration for the
application. The important configuration options are as follows:

- `SECRET_KEY`: A secret key used for signing cookies and other information.
  (**required**)

- `DATABASE_URL`: The URL to connect to the database. (**required**)

- `ACCESS_TOKEN_EXPIRE_MINUTES`: The number of minutes an access token should
  remain valid. (default: 60)

- `API_VERSION_URL`: The base URL for the API endpoints. (default: `/api/v1`)

- `PROJECT_NAME`: The name of the project. (default: `Complaint System`)

## Database Migration

The project uses Alembic for database migrations. Alembic is already installed
by default. To run the migration, follow these steps:

Navigate to the root directory of the project. Run the following command in the
terminal:

```bash
alembic upgrade head
```

## Run the Project

To run the project, navigate to the root directory of the project and run the
following command in the terminal:

```bash
uvicorn app.main:app
```

This will start the development server at `http://localhost:8000/`.

[poetry]: <https://python-poetry.org>
