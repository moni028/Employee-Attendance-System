# Employee Attendance Management System

A Flask and PostgreSQL application for employee attendance, leave, holidays, reporting, and analytics.

## Free deployment

Use a free PostgreSQL database from Neon or Supabase, then deploy the web service on Render's free plan.

1. Create a free PostgreSQL project at [Neon](https://neon.tech) or [Supabase](https://supabase.com).
2. Copy its PostgreSQL connection string. It must use the format `postgresql://...` or `postgres://...`; the application converts it automatically for psycopg.
3. In Render, choose **New > Blueprint** and select this repository.
4. Keep the `master` branch and `render.yaml` path.
5. When Render asks for `DATABASE_URL`, paste the external PostgreSQL connection string.
6. Deploy the web service on the free instance type.

The Blueprint does not create a Render database, so it avoids the payment requirement. Database migrations run automatically when the service starts.

After deployment, test:

```text
https://your-render-url.onrender.com/health
```

It should return:

```json
{"status":"ok","service":"employee-attendance"}
```
