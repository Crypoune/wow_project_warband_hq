# Warband HQ

Warband HQ is a World of Warcraft character-tracking application that
centralizes player and character information using the Blizzard
Battle.net API.

The project combines a React frontend with a FastAPI backend. It is
developed incrementally through Agile sprints and user stories.

## Features

### Authentication --- US-01

- Authenticate users through Blizzard OAuth 2.0.
- Manage authentication sessions on the backend.
- Retrieve the authenticated Blizzard account profile.
- Support logout.
- Integrate the React frontend with the FastAPI backend.

### Character Retrieval --- US-02

- Retrieve characters associated with the authenticated Blizzard
  account.
- Display available characters and import selected characters into
  Warband HQ.
- Store imported characters in MySQL.
- Prevent duplicate imports for the same user.
- Retrieve the authenticated user's imported characters.

### Character Overview --- US-03

- Display imported characters in a centralized collection.
- Show character portraits and visual references for classes, races,
  and factions.
- Display character media, name, level, class, race, gender, realm,
  and faction.
- Switch between grid and list views.

### Error Handling --- US-05

- Handle invalid or unavailable Blizzard profile data.
- Return appropriate API errors when character information cannot be
  retrieved.

### Character Filtering and Sorting --- US-07

- Search by character name, race, class, or realm.
- Filter by class and faction.
- Sort by name, level, or realm.

### Character Favorites --- US-08

- Mark characters as favorites and remove them from favorites.
- Persist favorite status through the backend and database.
- Filter the collection to show favorites only.
- Manage favorites in grid and list views.

### Global Character Tag Management --- US-09

- Manage tags associated with characters.
- Organize the collection with a shared tag catalogue.
- Persist tags and character-tag associations in the database.

### Planned Features

- Character progression tracking.
- Character details and synchronization with Blizzard.
- Additional character-tracking features as the project evolves.

## Tech Stack

### Frontend

- React
- Vite
- JavaScript
- Sass (SCSS)
- Lucide React

### Backend

- Python
- FastAPI
- SQLAlchemy
- MySQL
- PyMySQL
- HTTPX
- Pydantic Settings

### External API

- Blizzard Battle.net API
- OAuth 2.0
- WoW Account Profile API

### Testing and Quality

- pytest
- HTTPX-based API testing
- Automated backend tests
- ESLint
- Vite production build

## Project Structure

The following is a high-level overview. Update it when the repository
structure changes.

```text
wow_project_warband_hq/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   └── services/
│   ├── database/
│   │   ├── schema.sql
│   │   └── setup.sql
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
├── docs/
├── .gitignore
└── README.md
```

## Local Development

Warband HQ can be developed on Windows or macOS. The database
instructions below use MySQL; on the project's macOS development setup,
MySQL is provided by MAMP.

### Prerequisites

Install or configure: - Git - Python compatible with the pinned backend
dependencies - Node.js and npm - MySQL - A Blizzard Developer Portal
application with OAuth credentials

Official resources: - [Git](https://git-scm.com/downloads) -
[Python](https://www.python.org/downloads/) -
[Node.js](https://nodejs.org/) -
[MySQL](https://dev.mysql.com/downloads/) - [Blizzard Developer
Portal](https://develop.battle.net/)

Check that the required commands are available:

```bash
git --version
python3 --version
node --version
npm --version
```

### 1. Clone the Repository

```bash
git clone https://github.com/Crypoune/wow_project_warband_hq.git
cd wow_project_warband_hq
```

### 2. Configure MySQL

Start MySQL. On the macOS MAMP setup, the MySQL port is `8889`; the
default port for many standalone MySQL installations is `3306`. Use the
host and port configured by your local installation.

Create two databases: - `warband_hq` for local application
development. - `warband_hq_test` exclusively for automated tests.

Use a dedicated database account for the application rather than the
MySQL administrator account. Grant that account only the permissions
required by the project on these two databases.

The repository includes SQL scripts in `backend/database/`: -
`setup.sql` contains database setup SQL. - `schema.sql` defines the
application tables and related database objects.

Review the scripts before executing them. Use phpMyAdmin or a MySQL
client to run the setup and create the schema in **both** `warband_hq`
and `warband_hq_test`. Do not point automated tests at the development
database.

### 3. Configure Environment Variables

Create a local environment file from the example.

From the repository root:

**Windows PowerShell**

```powershell
Copy-Item backend/.env.example backend/.env
```

**macOS Terminal**

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and provide your own values. The database URL should
use the MySQL SQLAlchemy driver:

```dotenv
DATABASE_URL=mysql+pymysql://warband_hq_user:YOUR_DATABASE_PASSWORD@127.0.0.1:8889/warband_hq

BLIZZARD_CLIENT_ID=YOUR_BLIZZARD_CLIENT_ID
BLIZZARD_CLIENT_SECRET=YOUR_BLIZZARD_CLIENT_SECRET
BLIZZARD_REGION=eu
BLIZZARD_REDIRECT_URI=http://127.0.0.1:8000/api/auth/callback

SESSION_SECRET_KEY=YOUR_SESSION_SECRET
```

Adjust the host and port if your local MySQL installation differs. Use
the variable names in `backend/.env.example` as the source of truth.

Generate a strong, random session secret. Never reuse your Blizzard
client secret as the session secret.

**Security requirements** - Never commit `backend/.env`. - Never publish
Blizzard credentials, database passwords, session secrets, access
tokens, or session identifiers. - Keep `.env.example` limited to
placeholders. - Avoid sharing terminal output that contains credentials.

### 4. Backend Setup

From the repository root, create and activate a virtual environment.

**Windows PowerShell**

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**macOS Terminal**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The project uses versioned SQL scripts for database setup. **Alembic is
not used**; apply the SQL scripts in `backend/database/` when setting up
a new local database or when the project documents a schema change.

#### Start the Backend

From `backend`, with the virtual environment activated:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend should be available at: - API: <http://127.0.0.1:8000/> -
Interactive API documentation: <http://127.0.0.1:8000/docs>

Keep the backend terminal open while using the application.

### 5. Frontend Setup

Open a second terminal from the repository root.

```bash
cd frontend
npm install
npm run dev
```

The Vite development server is configured to use:

<http://127.0.0.1:5173/>

The frontend communicates with the backend at:

<http://127.0.0.1:8000/>

If you change either port, keep the frontend API configuration and
backend CORS settings consistent.

Useful frontend commands:

```bash
npm run lint
npm run build
```

Stop the development server with `Ctrl+C`.

### 6. Blizzard OAuth Configuration

Create or configure an application in the [Blizzard Developer
Portal](https://develop.battle.net/).

Set the OAuth redirect URI to:

```text
http://127.0.0.1:8000/api/auth/callback
```

This value must match `BLIZZARD_REDIRECT_URI` in `backend/.env` and the
redirect URI configured in the Blizzard Developer Portal.

The backend uses the Blizzard client ID and client secret to initiate
and complete OAuth. Users must authenticate through Blizzard before
accessing endpoints that require an authenticated session.

### 7. Verify the Installation

1.  Start MySQL and confirm both databases exist.
2.  Confirm `backend/.env` contains the correct local MySQL URL and
    Blizzard settings.
3.  Start the backend and verify it starts without configuration or
    database errors.
4.  Open the API documentation at <http://127.0.0.1:8000/docs>.
5.  Start the frontend and open <http://127.0.0.1:5173/>.
6.  Test the Blizzard OAuth flow using the configured callback.
7.  Verify character retrieval when Blizzard provides the required
    account data.

If the project exposes a health endpoint, use the route implemented in
the current backend; do not assume one exists unless it is present in
the code.

## Authentication API

The authentication workflow uses these endpoints:

Method Endpoint Description

---

GET `/api/auth/login` Starts Blizzard authentication
GET `/api/auth/callback` Processes the OAuth callback
GET `/api/auth/me` Returns the authenticated user's profile
POST `/api/auth/logout` Ends the user's session

The backend manages authentication sessions. Frontend requests must
include credentials when needed to preserve the session.

## Character API

The character retrieval and import workflow uses these endpoints:

---

Method Endpoint Description

---

GET `/api/characters/available` Retrieves characters
available from the
authenticated Blizzard
account

POST `/api/characters/import` Imports selected
characters into Warband
HQ

GET `/api/characters` Retrieves characters
imported by the
authenticated user

---

The import endpoint accepts a JSON payload containing selected Blizzard
character IDs. For example:

```json
{
  "character_ids": [123456, 789012]
}
```

These IDs are illustrative. The backend verifies that requested
characters belong to the authenticated Blizzard account before importing
them. Duplicate imports for the same user are skipped.

Refer to the current API implementation and interactive API
documentation for exact request and response schemas.

## Database Schema Management

Warband HQ uses MySQL and SQL scripts for schema setup. Alembic
migrations are no longer part of the project.

- `backend/database/setup.sql`: database setup SQL.
- `backend/database/schema.sql`: application table definitions.

Review SQL changes before applying them. For a new environment, create
the required databases and apply the schema to both the development and
test databases. Do not run integration tests against `warband_hq`.

## Running Tests

### Backend Tests

From the `backend` directory with the virtual environment activated, the
integration tests require `DATABASE_URL` to be present in the process
environment and to point to `warband_hq_test`. The tests check this
database name and fail if a different database is selected.

For a local MAMP installation, set the test database URL for the test
process. Replace the placeholder locally with your database password; do
not share the real value:

```bash
DATABASE_URL='mysql+pymysql://warband_hq_user:YOUR_DATABASE_PASSWORD@127.0.0.1:8889/warband_hq_test' python -m pytest -v
```

Use your actual MySQL host and port if they differ. Avoid committing or
sharing commands containing real credentials.

To run only the tag integration tests:

```bash
DATABASE_URL='mysql+pymysql://warband_hq_user:YOUR_DATABASE_PASSWORD@127.0.0.1:8889/warband_hq_test' python -m pytest tests/test_tag_integration.py -v
```

The automated backend tests cover the application behavior implemented
in the project. A passing test suite does not replace manual
verification of database setup and the OAuth flow.

### Frontend Checks

From the `frontend` directory:

```bash
npm run lint
npm run build
```

These commands check the frontend code and generate a production build.

## Troubleshooting

### Python Is Not Recognized

On macOS, try:

```bash
python3 --version
```

Use `python3` to create the virtual environment if `python` is
unavailable.

### Virtual Environment Is Not Activated

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS**

```bash
source .venv/bin/activate
```

Install dependencies from `backend` if needed:

```bash
python -m pip install -r requirements.txt
```

### MySQL Connection Refused

Check that: - MySQL is running. - The database exists and the schema has
been applied. - The database account exists and has the required
permissions. - The password is correct. - `DATABASE_URL` uses the
correct host, port, and database name. - For MAMP, the configured MySQL
port is commonly `8889`; confirm it in your local MAMP configuration.

### Integration Tests Fail Before Running

The integration tests read `DATABASE_URL` from the process environment
and require the database name `warband_hq_test`. A value in
`backend/.env` loaded by Pydantic Settings is not automatically copied
into `os.environ`. Set `DATABASE_URL` explicitly for the test command
and ensure it targets the test database.

### Frontend Cannot Reach the Backend

Confirm that the backend is running on port `8000` and the frontend on
port `5173`. Check that the frontend API configuration points to:

```text
http://127.0.0.1:8000
```

The backend CORS configuration must allow the frontend origin:

```text
http://127.0.0.1:5173
```

Use the same hostname consistently. Browsers may treat `localhost` and
`127.0.0.1` as different origins.

### Blizzard OAuth Fails

Verify that: - The client ID and client secret are correct. - The
configured region is correct. - The redirect URI exactly matches the
Blizzard Developer Portal configuration. - The callback endpoint is
available. - Backend logs do not report OAuth or session configuration
errors.

Never include the client secret in frontend code or public logs.

### Session Is Not Preserved

Check that frontend API requests include credentials where required and
that backend session and CORS settings match the configured frontend
origin. For local development, use the project's existing cookie
settings rather than changing production security options unnecessarily.

### Node.js Dependencies or Build Failures

From `frontend`, run:

```bash
npm install
npm run lint
npm run build
```

If installation fails, inspect the Node.js version and error output
before deleting lockfiles or reinstalling packages.

## Security Notes

- Never commit `.env` files containing real credentials.
- Never expose Blizzard client secrets in frontend code.
- Use a strong session secret.
- Use a dedicated MySQL account with limited permissions for the
  application.
- Do not expose a database service directly to the public internet.
- Restrict CORS to the origins required by the application.
- Use HTTPS and secure cookie settings when deploying outside local
  development.
- Do not publish logs containing tokens, session identifiers,
  passwords, or other secrets.

## Project Status

Warband HQ is developed incrementally using Agile sprints and user
stories.

- **US-01 --- Blizzard Authentication:** authentication and frontend
  integration implemented.
- **US-02 --- Character Retrieval:** character retrieval, database
  persistence, and import workflow implemented.
- **US-03 --- Character Overview:** character collection displayed in
  grid and list views.
- **US-05 --- Error Handling:** API errors for invalid or unavailable
  profile data.
- **US-07 --- Character Filtering and Sorting:** search, filtering,
  and sorting.
- **US-08 --- Character Favorites:** persistent favorite management
  and favorites-only filtering.
- **US-09 --- Global Character Tag Management:** global character tag
  management implemented.

Update project status as user stories are completed and verified.

## License

To be defined.
