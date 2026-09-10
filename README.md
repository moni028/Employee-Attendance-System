# Employee Attendance Management System

A Flask and PostgreSQL application for employee attendance, leave, holidays, reporting, and analytics.

## Local setup

1. Install Python 3.11+ and PostgreSQL.
2. Create a dedicated PostgreSQL role and database. Open **SQL Shell (psql)** or run `psql.exe` from your PostgreSQL installation, connect to the default `postgres` database, and execute:

```sql
CREATE ROLE attendance_app LOGIN PASSWORD 'replace-with-a-strong-password';
CREATE DATABASE employee_attendance OWNER attendance_app;
```

If either object already exists, use these alternatives instead:

```sql
ALTER ROLE attendance_app WITH LOGIN PASSWORD 'replace-with-a-strong-password';
-- Run this only if the database does not already exist:
CREATE DATABASE employee_attendance OWNER attendance_app;
```

Do not use the literal example password in a real environment.

3. Create and activate a virtual environment in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and set the same role password:

```powershell
Copy-Item .env.example .env
notepad .env
```

The important setting is:

```text
DATABASE_URL=postgresql+psycopg://attendance_app:YOUR_PASSWORD@localhost:5432/employee_attendance
```

If the password contains characters such as `@`, `:`, `/`, or `#`, URL-encode them in `DATABASE_URL`.

5. Generate and apply the schema migration:

```powershell
flask --app run.py db migrate -m "initial schema"
flask --app run.py db upgrade
```

These commands create the application tables from the SQLAlchemy models. You do not need to create the tables manually.

6. Start the development server:

```powershell
flask --app run.py run --debug
```

The health check is available at `http://127.0.0.1:5000/health`.

If PostgreSQL is installed in the default Windows location, the client can usually be run directly with:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d postgres
```

The PostgreSQL service must be running. Check it with:

```powershell
Get-Service postgresql*
```

The database password in `.env` must match the role password in PostgreSQL. The previous `password authentication failed for user "postgres"` error occurred because the application was using the fallback URL `postgres:password`, not valid credentials.

## Deploy to Render

This repository includes `render.yaml` for a Render web service and PostgreSQL database.

1. Push the project to GitHub.
2. In Render, choose **New > Blueprint** and select the repository.
3. Set `SECRET_KEY` to a long random value when prompted.
4. Deploy. The service runs Gunicorn and applies migrations during deployment.

The hosted service uses these values from Render:

```text
DATABASE_URL        # supplied by the Render PostgreSQL database
SECRET_KEY          # set as a secret in Render
APP_TIMEZONE=Asia/Kolkata
OFFICE_START_TIME=09:30
OFFICE_END_TIME=18:00
STANDARD_WORKING_HOURS=8
LATE_THRESHOLD_MINUTES=0
HALF_DAY_THRESHOLD_HOURS=4
```

Do not commit `.env` or production credentials. Open the deployed `/health` URL after deployment; it should return `{"status":"ok","service":"employee-attendance"}`.
