# Warband HQ

**Warband HQ** is a World of Warcraft character tracking application designed to centralize player and character information through the Blizzard Battle.net API.

The project aims to provide a clear overview of a player's WoW account and its characters through a dedicated web interface.

## Features

### Authentication — US-01

- Authentication through Blizzard OAuth 2.0.
- Server-side session management.
- Retrieval of the authenticated Blizzard account profile.
- Logout functionality.
- Integration between the React frontend and the FastAPI backend.

### Character Retrieval — US-02

- Retrieve characters associated with the authenticated Blizzard account.
- Display available characters in the web interface.
- Select characters for import into Warband HQ.
- Store imported characters in PostgreSQL.
- Prevent duplicate character imports for the same user.
- Retrieve the characters already imported by the authenticated user.
- Preserve the association between users and their imported characters.

### Planned Features

- Character overview and progression tracking.
- Character details and synchronization with Blizzard.
- Additional character tracking features as the project evolves.

## Tech Stack

### Frontend

- React
- Vite
- JavaScript
- CSS

### Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic

### External API

- Blizzard Battle.net API
- OAuth 2.0 authentication
- WoW Account Profile API

### Testing

- pytest
- Automated backend tests
- API endpoint and service tests

## Project Structure

```text
wow_project_warband_hq/
├── backend/
│   ├── alembic/
│   │   └── versions/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   └── services/
│   ├── tests/
│   ├── alembic.ini
│   └── requirements.txt
├── docs/
│   └── database/
│       └── setup.sql
└── frontend/
    └── src/
```

## Local Development

### Prerequisites

- Python
- Node.js and npm
- PostgreSQL
- A Blizzard Developer Portal application with OAuth credentials

### Backend Setup

From the project root:

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Configure the environment variables using `backend/.env.example` as a reference. Set your PostgreSQL connection details, Blizzard OAuth credentials, redirect URI, and session secret.

Apply database migrations:

```bash
alembic upgrade head
```

Start the backend:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Backend URL: http://127.0.0.1:8000/
- API documentation: http://127.0.0.1:8000/docs

### Frontend Setup

Open a second terminal from the project root:

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: http://127.0.0.1:5173/

## Authentication Configuration

For local development, configure the Blizzard OAuth redirect URI as follows:

```text
http://127.0.0.1:8000/api/auth/callback
```

The authentication flow uses these endpoints:

| Method | Endpoint             | Description                              |
| ------ | -------------------- | ---------------------------------------- |
| GET    | `/api/auth/login`    | Starts Blizzard authentication           |
| GET    | `/api/auth/callback` | Processes the OAuth callback             |
| GET    | `/api/auth/me`       | Returns the authenticated user's profile |
| POST   | `/api/auth/logout`   | Ends the user's session                  |

The backend manages authentication sessions, while the frontend communicates with the API using credentials to maintain the session.

## Character API

The character retrieval and import workflow uses the following endpoints:

| Method | Endpoint                    | Description                                                            |
| ------ | --------------------------- | ---------------------------------------------------------------------- |
| GET    | `/api/characters/available` | Retrieves characters available from the authenticated Blizzard account |
| POST   | `/api/characters/import`    | Imports selected characters into Warband HQ                            |
| GET    | `/api/characters`           | Retrieves characters imported by the authenticated user                |

The import endpoint accepts a JSON payload containing the selected Blizzard character IDs:

```json
{
  "character_ids": [123456, 789012]
}
```

Character IDs in this example are illustrative.

The backend verifies that the requested characters belong to the authenticated Blizzard account before importing them. Duplicate imports for the same user are skipped.

Imported character records are stored in PostgreSQL and associated with the authenticated application user.

## Database Migrations

Warband HQ uses Alembic to manage database schema changes.

After configuring the database connection, apply all migrations with:

```bash
alembic upgrade head
```

To check the current migration revision:

```bash
alembic current
```

## Running Tests

From the backend directory, with the virtual environment activated:

```bash
python -m pytest -v
```

The automated backend test suite covers authentication, health checks, character retrieval, character imports, and relevant error cases.

## Project Status

Warband HQ is being developed incrementally using Agile sprints and user stories.

- **US-01 — Blizzard Authentication:** implementation and frontend integration completed; automated tests passed.
- **US-02 — Character Retrieval:** backend endpoints, database model and migration, frontend character selection, and import workflow implemented; local functional verification completed.
- **US-03 — Character Overview:** planned.

## License

To be defined.
