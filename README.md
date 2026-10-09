# Warband HQ

**Warband HQ** is a World of Warcraft character tracking application designed to centralize player and character information through the Blizzard Battle.net API.

The project aims to provide a clear overview of a player's WoW account and its characters through a dedicated web interface.

## Features

### Authentication — US-01

- Authentication through Blizzard OAuth 2.0.
- Secure server-side session management.
- Retrieval of the authenticated Blizzard account profile.
- Logout functionality.
- Integration between the React frontend and the FastAPI backend.

### Planned features

- Retrieve characters associated with the authenticated Blizzard account.
- Display character information and progression.
- Expand character tracking features progressively.

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

### Testing

- pytest
- Automated backend tests

## Project Structure

```text
wow_project_warband_hq/
├── backend/
│   ├── alembic/
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

Start the backend:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend URL: http://127.0.0.1:8000/

API documentation: http://127.0.0.1:8000/docs

### Frontend Setup

Open a second terminal from the project root:

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: http://127.0.0.1:5173/

## Authentication Configuration

For local development, the Blizzard OAuth redirect URI is:

```text
http://127.0.0.1:8000/api/auth/callback
```

The authentication flow uses the following endpoints:

| Method | Endpoint             | Description                              |
| ------ | -------------------- | ---------------------------------------- |
| GET    | `/api/auth/login`    | Starts Blizzard authentication           |
| GET    | `/api/auth/callback` | Processes the OAuth callback             |
| GET    | `/api/auth/me`       | Returns the authenticated user's profile |
| POST   | `/api/auth/logout`   | Ends the user's session                  |

The backend manages authentication sessions, while the frontend communicates with the API using credentials to maintain the session.

**Important:** The local URLs above are intended for development. Production deployment requires appropriate HTTPS, cookie, CORS, and environment configuration.

## Running Tests

From the backend directory, with the virtual environment activated:

```bash
python -m pytest -v
```

## Project Status

The project is being developed incrementally using Agile sprints and user stories.

- **US-01 — Blizzard Authentication:** implementation and integration completed; final automated test verification pending.
- **US-02 — Character Retrieval:** planned next step.

## License

To be defined.
