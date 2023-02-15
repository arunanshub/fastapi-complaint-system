# FastAPI Complaint System

The Complaint System is a backend service for a complaint management system. It
provides a REST API to manage complaint tickets, users, and other information.

This project is based on the [Udemy tutorial on FastAPI][udemy].

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

- `AWS_ACCESS_KEY`: Access key for accessing AWS services. (**required**)

- `AWS_SECRET_ACCESS_KEY`: The AWS secret access key used for accessing AWS
  services. (**required**)

- `AWS_BUCKET_NAME`: name of the Amazon Web Services (AWS) S3 bucket to be used
   by the application. (**required**)

- `AWS_REGION`: the AWS region to be used for the S3 bucket defined in the
   `AWS_BUCKET_NAME` field. (**required**)

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

## Creating the Admin

The API provides a command line interface for creating an admin user. To create
an admin, use the following command in your terminal:


```bash
python -m app create-admin \
    --first-name <first_name> \
    --last-name <last_name> \
    --email <email> \
    --phone <phone> \
    --iban <iban> \
    --password <password>
```

This will create an admin user in the database with the provided information.
The created user will have the role of `ADMIN`.

## Run the Project

To run the project, navigate to the root directory of the project and run the
following command in the terminal:

```bash
uvicorn app.main:app
```

This will start the development server at `http://localhost:8000/`.

[poetry]: <https://python-poetry.org>
[udemy]: <https://www.udemy.com/course/fastapi-rest/>

## Improvements

In this project, a number of improvements over the original tutorial have been
made to enhance the organization and structure of the code.

1. To streamline the process of handling API requests, the endpoints utilize
   SQLModel and Pydantic models instead of raw requests. This provides a clear
   and organized approach to data validation and management.

2. The authentication process has been updated to utilize OAuth2, instead of a
   custom HTTP authentication method. This provides a more secure and
   standardized approach to authentication.

3. The database operations have been centralized and organized into a `crud`
   module, making it easier to manage and maintain the database interactions
   within the API.

4. The API endpoints are located in the `api` module, providing a clear and
   organized structure for the API routes and functions.
