# Mergington High School Activities and Project API

FastAPI application for extracurricular activities plus tenant-scoped project, audit-log, and notification workflows.

## Features

- View all available extracurricular activities
- Sign up for activities
- Create, update, list, and delete tenant-scoped projects
- Record and query tenant-scoped audit logs
- Create, list, and mark recipient notifications as read

## Getting Started

1. Install the dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Run the application:

   ```
   uvicorn src.app:app --reload
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| POST   | `/projects` | Create a project; requires `X-Tenant-ID` |
| PATCH  | `/projects/{project_id}/status` | Update a project status; requires `X-Tenant-ID` |
| GET    | `/projects?team=Platform` | List projects for a team; requires `X-Tenant-ID` |
| DELETE | `/projects/{project_id}` | Delete a project; requires `X-Tenant-ID` |
| POST   | `/audit-logs` | Record an audit event; requires `X-Tenant-ID` |
| GET    | `/audit-logs` | List tenant audit events; requires `X-Tenant-ID` |
| POST   | `/notifications` | Create a notification; requires `X-Tenant-ID` |
| GET    | `/notifications?recipient_id=user-1` | List recipient notifications; requires `X-Tenant-ID` |
| PATCH  | `/notifications/{notification_id}/read?recipient_id=user-1` | Mark a notification read; requires `X-Tenant-ID` |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

Activities remain in memory, while projects, audit logs, and notifications are stored in SQLite by default at `projects.db`. Set `PROJECT_DATABASE_URL` to configure another SQLAlchemy-supported database URL. Every project, audit, and notification operation requires a tenant ID and applies tenant scoping.
