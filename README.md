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
- Retrieve characters already imported by the authenticated user.
- Preserve the association between users and their imported characters.

### Character Overview — US-03

- Display imported characters in a centralized collection.
- Present character portraits and visual references for classes, races, and factions.
- Display key character information, including media, name, level, class, race, gender, realm, and faction.
- Switch between grid and list display modes.

### Error Handling — US-05

- Handle invalid or unavailable Blizzard profile data.
- Return appropriate API errors when character information cannot be retrieved.

### Character Filtering and Sorting — US-07

- Search characters by name, race, class, or realm.
- Filter characters by class and faction.
- Sort characters by name, level, or realm.

### Character Favorites — US-08

- Mark characters as favorites and remove them from favorites.
- Persist favorite status through the backend API and database.
- Filter the character collection to display favorites only.
- Support favorite management in both grid and list views.

### Global Character Tag Management — US-09

- Manage tags associated with characters.
- Organize the character collection using a shared tagging system.
- Persist tag information through the backend and database.

### Planned Features

- Character progression tracking.
- Character details and synchronization with Blizzard.
- Additional character tracking features as the project evolves.

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
- PostgreSQL
- Alembic
- HTTPX

### External API

- Blizzard Battle.net API
- OAuth 2.0 authentication
- WoW Account Profile API

### Testing and Quality

- pytest
- HTTPX-based API testing
- Automated backend tests
- ESLint
- Vite production build

## Project Structure

The following is the project's general structure. Update this section whenever the repository structure changes.

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
│   ├── requirements.txt
│   └── .env.example
├── docs/
│   └── database/
│       └── setup.sql
├── frontend/
│   └── src/
├── .gitignore
└── README.md
```

## Local Development

Warband HQ can be developed on Windows or macOS.

### Prerequisites

Install the following software before starting:

- **Git** — to clone and manage the repository.
- **Python** — a version compatible with the backend dependencies.
- **Node.js and npm** — for the React frontend.
- **PostgreSQL** — for persistent application data.
- **Blizzard Developer Portal application** — to obtain OAuth credentials.

Useful official resources:

- Git: https://git-scm.com/downloads
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/
- PostgreSQL: https://www.postgresql.org/download/
- Blizzard Developer Portal: https://develop.battle.net/

Check that the required commands are available in your terminal:

```bash
git --version
python --version
node --version
npm --version
```

On macOS, use `python3 --version` if `python` is not available.

### 1. Clone the Repository

Open a terminal and run:

```bash
git clone https://github.com/Crypoune/wow_project_warband_hq.git
cd wow_project_warband_hq
```

### 2. Configure PostgreSQL

PostgreSQL must be installed and running before the backend can connect to the database.

Create a dedicated application role and database using a PostgreSQL administrator account.

Example SQL:

```sql
CREATE ROLE warband_hq_user
WITH LOGIN PASSWORD 'REPLACE_WITH_A_STRONG_PASSWORD';

CREATE DATABASE warband_hq
OWNER warband_hq_user;
```

Replace the example password with a strong password of your own.

The default PostgreSQL port is `5432`. If your local installation uses another port, use that port in the database connection string.

Do not expose PostgreSQL directly to the public internet for local development.

### 3. Configure Environment Variables

The backend uses environment variables to configure its database connection, Blizzard credentials, and session security.

Create a local environment file from the example provided by the project.

**Windows PowerShell**, from the repository root:

```powershell
Copy-Item backend/.env.example backend/.env
```

**macOS Terminal**, from the repository root:

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and replace the example values with your own configuration.

Example:

```dotenv
DATABASE_URL=postgresql+psycopg://warband_hq_user:YOUR_DATABASE_PASSWORD@localhost:5432/warband_hq

BLIZZARD_CLIENT_ID=YOUR_BLIZZARD_CLIENT_ID
BLIZZARD_CLIENT_SECRET=YOUR_BLIZZARD_CLIENT_SECRET
BLIZZARD_REGION=eu
BLIZZARD_REDIRECT_URI=http://127.0.0.1:8000/api/auth/callback

SESSION_SECRET_KEY=YOUR_SESSION_SECRET
```

Use the variable names defined in `backend/.env.example` as the source of truth.

Generate a strong, random session secret. Never reuse your Blizzard client secret as the session secret.

**Security requirements:**

- Never commit `backend/.env` to Git.
- Never publish your Blizzard client secret.
- Never include real passwords or secrets in documentation.
- Keep `.env.example` limited to placeholder values.

### 4. Backend Setup

The backend uses FastAPI, SQLAlchemy, PostgreSQL, and Alembic.

#### Windows — PowerShell

From the repository root:

```powershell
cd backend
python -m venv .venv
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation because of its execution policy, use an appropriate local environment configuration or activate the environment through another supported terminal. Avoid changing system-wide security settings unnecessarily.

Install the dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### macOS — Terminal

From the repository root:

```bash
cd backend
python3 -m venv .venv
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On macOS, make sure the selected Python version is compatible with the project's pinned dependencies.

#### Apply Database Migrations

Once PostgreSQL is running and `backend/.env` is configured, run the following command from the `backend` directory with the virtual environment activated:

```bash
alembic upgrade head
```

Alembic manages database schema changes. Use the project's migrations instead of manually creating application tables.

To inspect the current migration revision:

```bash
alembic current
```

#### Start the Backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend should now be accessible at:

- API: http://127.0.0.1:8000/
- Interactive API documentation: http://127.0.0.1:8000/docs

Keep this terminal open while using the application.

### 5. Frontend Setup

Open a second terminal from the repository root.

#### Windows — PowerShell

```powershell
cd frontend
npm install
npm run dev
```

#### macOS — Terminal

```bash
cd frontend
npm install
npm run dev
```

The Vite development server is configured to use:

http://127.0.0.1:5173/

The frontend communicates with the backend at:

http://127.0.0.1:8000/

If you change the frontend or backend ports, make sure the API configuration and backend CORS settings remain consistent.

#### Useful Frontend Commands

Run the linter:

```bash
npm run lint
```

Build the production version:

```bash
npm run build
```

Stop the development server with `Ctrl + C`.

### 6. Blizzard OAuth Configuration

Create or configure an application in the Blizzard Developer Portal:

https://develop.battle.net/

Set the OAuth redirect URI to:

```text
http://127.0.0.1:8000/api/auth/callback
```

Make sure this value matches `BLIZZARD_REDIRECT_URI` in `backend/.env`.

The backend uses the Blizzard client ID and client secret to initiate and complete the OAuth flow.

The user must authenticate through Blizzard before accessing endpoints that require an authenticated session.

### 7. Verify the Installation

Start PostgreSQL, the backend, and the frontend.

Then verify the following:

1. The backend starts without configuration or database errors.
2. Alembic migrations complete successfully.
3. The API documentation opens at `http://127.0.0.1:8000/docs`.
4. The frontend opens at `http://127.0.0.1:5173/`.
5. Blizzard OAuth redirects to the configured callback.
6. Authenticated character retrieval works when Blizzard provides the required account data.

If the project exposes a health endpoint, verify it using the route implemented in the current backend. Do not assume a health endpoint is available unless it is present in the code.

## Authentication API

The documented authentication workflow uses the following endpoints:

| Method | Endpoint             | Description                              |
| ------ | -------------------- | ---------------------------------------- |
| GET    | `/api/auth/login`    | Starts Blizzard authentication           |
| GET    | `/api/auth/callback` | Processes the OAuth callback             |
| GET    | `/api/auth/me`       | Returns the authenticated user's profile |
| POST   | `/api/auth/logout`   | Ends the user's session                  |

The backend manages authentication sessions. The frontend must send requests with credentials when necessary to preserve the session.

## Character API

The character retrieval and import workflow uses the following endpoints:

| Method | Endpoint                    | Description                                                            |
| ------ | --------------------------- | ---------------------------------------------------------------------- |
| GET    | `/api/characters/available` | Retrieves characters available from the authenticated Blizzard account |
| POST   | `/api/characters/import`    | Imports selected characters into Warband HQ                            |
| GET    | `/api/characters`           | Retrieves characters imported by the authenticated user                |

The import endpoint accepts a JSON payload containing the selected Blizzard character IDs.

Example payload:

```json
{
  "character_ids": [123456, 789012]
}
```

The IDs above are illustrative and do not represent actual characters.

The backend verifies that the requested characters belong to the authenticated Blizzard account before importing them. Duplicate imports for the same user are skipped.

Imported character records are stored in PostgreSQL and associated with the authenticated application user.

Refer to the current API implementation and the interactive API documentation for the exact request and response schemas.

## Database Migrations

Warband HQ uses Alembic to manage database schema changes.

Run migration commands from the `backend` directory with the virtual environment activated.

Apply all pending migrations:

```bash
alembic upgrade head
```

Inspect the current revision:

```bash
alembic current
```

Inspect the available migration history:

```bash
alembic history
```

After pulling changes that introduce new migrations, apply them before running the application against the updated schema.

Do not delete existing migrations or modify an already-applied migration without understanding the impact on other environments.

## Running Tests

### Backend Tests

From the `backend` directory, with the virtual environment activated:

```bash
python -m pytest -v
```

The automated backend test suite covers application functionality, including authentication, character retrieval, imports, and relevant error cases as implemented in the project.

### Frontend Checks

From the `frontend` directory:

```bash
npm run lint
npm run build
```

These commands check the frontend code and generate a production build.

## Troubleshooting

### Python Is Not Recognized

On Windows, verify that Python is installed and available in the terminal.

On macOS, try:

```bash
python3 --version
```

Use `python3` to create the virtual environment if the `python` command is unavailable.

### Virtual Environment Is Not Activated

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS:

```bash
source .venv/bin/activate
```

After activation, install dependencies if necessary:

```bash
python -m pip install -r requirements.txt
```

### PostgreSQL Connection Refused

Check that:

- PostgreSQL is installed and running.
- The database exists.
- The configured database role exists.
- The password is correct.
- The database host and port match the local installation.
- `DATABASE_URL` in `backend/.env` is correct.

The default PostgreSQL port is `5432`, but some local installations use a different port.

### Database Migration Errors

Ensure the backend virtual environment is active and that the database connection is configured correctly.

From `backend`, run:

```bash
alembic current
alembic upgrade head
```

Read the complete error message before attempting to change the schema manually.

### Frontend Cannot Reach the Backend

Confirm that the backend is running on port `8000` and the frontend is running on port `5173`.

Check that the frontend API configuration points to:

```text
http://127.0.0.1:8000
```

The backend CORS configuration must allow the frontend origin:

```text
http://127.0.0.1:5173
```

Use the same hostname consistently. `localhost` and `127.0.0.1` may be treated as different origins by the browser.

### Blizzard OAuth Fails

Verify that:

- The client ID and client secret are correct.
- The configured region is correct.
- The redirect URI exactly matches the Blizzard Developer Portal configuration.
- The callback endpoint is available.
- The backend logs do not report an OAuth or session configuration error.

Never include the client secret in frontend code or public logs.

### Session Is Not Preserved

Check that frontend API requests include credentials where required and that the backend session and CORS settings are compatible with the configured frontend origin.

For local development, use the project's existing cookie settings rather than changing production security options unnecessarily.

### Node.js Dependencies or Build Failures

From `frontend`, run:

```bash
npm install
npm run lint
npm run build
```

If a dependency installation fails, inspect the Node.js version and the error output before deleting lockfiles or reinstalling packages.

## Security Notes

- Never commit `.env` files containing real credentials.
- Never expose Blizzard client secrets in frontend code.
- Use a strong session secret.
- Do not expose PostgreSQL directly to the public internet.
- Restrict CORS to the origins required by the application.
- Use HTTPS and secure cookie settings when deploying outside local development.
- Do not publish logs containing tokens, session identifiers, passwords, or other secrets.

## Project Status

Warband HQ is being developed incrementally using Agile sprints and user stories.

- **US-01 — Blizzard Authentication:** authentication and frontend integration implemented.
- **US-02 — Character Retrieval:** character retrieval, database persistence, and import workflow implemented.
- **US-03 — Character Overview:** character collection displayed in grid and list views.
- **US-05 — Error Handling:** appropriate API errors for invalid or unavailable profile data.
- **US-07 — Character Filtering and Sorting:** search, filtering, and sorting functionality.
- **US-08 — Character Favorites:** persistent favorite management and favorites-only filtering.
- **US-09 — Global Character Tag Management:** global character tag management implemented.

Project status should be updated as user stories are completed and verified.

## License

To be defined.
