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

### Battle.net Account Switching --- US-21

- Open an account-switch confirmation modal from the application header.
- Open Battle.net logout in a separate browser tab.
- Preserve the current Warband HQ session until the new OAuth authentication succeeds.
- Detect when Blizzard returns the same account instead of a different account.
- After Battle.net logout, manually return to Warband HQ and select "Log in with Battle.net" to complete the switch.

### Character Retrieval --- US-02

- Retrieve characters associated with the authenticated Blizzard account.
- Display available characters and import selected characters into Warband HQ.
- Store imported characters in MySQL.
- Prevent duplicate imports for the same user.
- Retrieve the authenticated user's imported characters.

### Character Overview --- US-03

- Display imported characters in a centralized collection.
- Show character portraits and visual references for classes, races, and factions.
- Display character media, name, level, class, race, gender, realm, and faction.
- Switch between grid and list views.

### Main Character Information --- US-04

- Display the main information about a selected character.
- Retrieve character information from the Blizzard API.
- Present relevant character information in the character overview.

### Error Handling --- US-05

- Handle invalid or unavailable Blizzard profile data.
- Return appropriate API errors when character information cannot be retrieved.
- Display relevant loading and error states in the frontend.

### Character Details --- US-06

- Open a dedicated details page for a selected character.
- Display an updated character identity header.
- Show character equipment.
- Display primary and secondary character statistics.
- Present detailed character information in an improved page layout.

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

- Provide a shared tag catalogue for character organization.
- Manage the available tags through administrative operations.
- Persist tags and character-tag associations in the database.
- Assign tags to characters.

### Personal Goals --- US-10

- Create and manage personal goals.
- Associate goals with the user's Warband or with a specific character.
- Define goal titles, descriptions, and statuses.
- Update and delete existing goals.
- Persist personal goals in the database.

### Tasks --- US-11

- Create tasks within personal goals.
- Define task titles and descriptions.
- Mark tasks as completed or incomplete.
- Update and delete existing tasks.
- Persist tasks and their association with goals in the database.

### Character Tag Management & Performance --- US-20

- Display assigned character tags in the My Warband overview.
- Manage tag assignments from the Character Details page.
- Retrieve assigned tags through grouped queries.
- Reduce unnecessary network requests when displaying character tags.

### Planned Features

- Character progression tracking.
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
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   └── services/
│   │
│   ├── database/
│   │   ├── schema.sql
│   │   └── setup.sql
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── data/
│   │   ├── pages/
│   │   ├── services/
│   │   └── styles/
│   │
│   ├── package.json
│   └── vite.config.js
│
├── docs/
│   ├── coming-next.md
│   ├── product-backlog.md
│   └── sprint-plan.md
│
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

Check the backend health endpoint:

```bash
curl http://127.0.0.1:8000/health
```

A successful response should look like:

```json
{
  "status": "ok",
  "database": "available"
}
```

## API Documentation

Warband HQ provides a REST API built with **FastAPI**. All API endpoints use JSON for request and response bodies, unless otherwise specified.

The interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### Authentication API

Base path: `/api/auth`

| Method | Endpoint    | Description                                              |
| ------ | ----------- | -------------------------------------------------------- |
| GET    | `/login`    | Initiates Blizzard OAuth authentication.                 |
| GET    | `/callback` | Handles the OAuth callback and creates the user session. |
| GET    | `/me`       | Retrieves the currently authenticated user.              |
| POST   | `/logout`   | Ends the current user session.                           |
| POST   | `/switch`   | Initiates a Battle.net account switch.                   |

### Characters API

Base path: `/api/characters`

| Method | Endpoint                        | Description                                                       |
| ------ | ------------------------------- | ----------------------------------------------------------------- |
| GET    | `/available`                    | Retrieves characters available on the connected Blizzard account. |
| POST   | `/import`                       | Imports selected characters into Warband HQ.                      |
| GET    | `/`                             | Retrieves the user's imported characters.                         |
| GET    | `/{character_id}`               | Retrieves detailed information about a character.                 |
| PATCH  | `/{character_id}/favorite`      | Updates a character's favorite status.                            |
| GET    | `/{character_id}/tags`          | Retrieves tags assigned to a character.                           |
| POST   | `/{character_id}/tags/{tag_id}` | Assigns a tag to a character.                                     |
| DELETE | `/{character_id}/tags/{tag_id}` | Removes a tag from a character.                                   |

### Tags API

Base path: `/api/tags`

| Method | Endpoint    | Description                   |
| ------ | ----------- | ----------------------------- |
| GET    | `/`         | Retrieves the available tags. |
| GET    | `/{tag_id}` | Retrieves a specific tag.     |
| POST   | `/`         | Creates a new tag.            |
| PATCH  | `/{tag_id}` | Updates an existing tag.      |
| DELETE | `/{tag_id}` | Deletes a tag.                |

**Permissions:** All authenticated users can retrieve tags. Creating, updating and deleting tags require administrator privileges.

### Goals API

Base path: `/api/goals`

| Method | Endpoint     | Description                 |
| ------ | ------------ | --------------------------- |
| POST   | `/`          | Creates a new goal.         |
| GET    | `/`          | Retrieves the user's goals. |
| PATCH  | `/{goal_id}` | Updates an existing goal.   |
| DELETE | `/{goal_id}` | Deletes a goal.             |

Goals can be associated with a specific character or managed at Warband level.

### Tasks API

Tasks are managed through goal-related and task-specific endpoints.

| Method | Endpoint                     | Description                                      |
| ------ | ---------------------------- | ------------------------------------------------ |
| POST   | `/api/goals/{goal_id}/tasks` | Creates a task for a goal.                       |
| GET    | `/api/goals/{goal_id}/tasks` | Retrieves the tasks associated with a goal.      |
| PATCH  | `/api/tasks/{task_id}`       | Updates a task, including its completion status. |
| DELETE | `/api/tasks/{task_id}`       | Deletes a task.                                  |

### Health Check

Endpoint: `GET /health`

Checks whether the backend is running and can successfully communicate with the database.

**Successful response:**

```json
{
  "status": "ok",
  "database": "available"
}
```

If the database is unavailable, the endpoint returns an HTTP `503` response.

## Database Schema Management

Warband HQ uses MySQL and SQL scripts to manage its database structure.
Alembic migrations are not currently used.

### SQL Scripts

The `backend/database/` directory contains two SQL scripts:

- `setup.sql`: creates the development and test databases
  (`warband_hq` and `warband_hq_test`), creates a dedicated database
  user, and grants the required permissions.
- `schema.sql`: creates the application tables and their relationships.

### Database Setup

For a new environment:

1. Review `setup.sql` and replace `CHANGE_ME` with a secure database
   password before executing it.
2. Execute `setup.sql` to create the databases and database user.
3. Execute `schema.sql` against both `warband_hq` and
   `warband_hq_test` to create the application tables.

Review SQL changes before applying them to an existing database.

**Important:** Never run integration tests against the development
database (`warband_hq`). Always use `warband_hq_test`.

## Running Tests

### Backend Tests

From the `backend` directory with the virtual environment activated,
run the backend tests with pytest.

The test configuration is loaded from `backend/.env.test` through
`tests/conftest.py`. Make sure this file defines `DATABASE_URL` and
points to the dedicated test database (`warband_hq_test`).

Integration tests explicitly check the database name and fail if a
different database is selected.

For a local MAMP installation, set the test database URL for the test
process. Replace the placeholder locally with your database password;
do not share the real value:

```bash
DATABASE_URL='mysql+pymysql://warband_hq_user:YOUR_DATABASE_PASSWORD@127.0.0.1:8889/warband_hq_test' python -m pytest -v
```

Use your actual MySQL host and port if they differ. Avoid committing or
sharing commands containing real credentials.

To run only the tag integration tests:

```bash
DATABASE_URL='mysql+pymysql://warband_hq_user:YOUR_DATABASE_PASSWORD@127.0.0.1:8889/warband_hq_test' python -m pytest tests/test_tag_integration.py -v
```

The authentication tests cover account-switch initialization, session
preservation, successful session replacement, same-account detection,
Blizzard OAuth failures, and rollback when saving the replacement
session fails.

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

Check the following:

- MySQL is running.
- The database exists and the schema has been applied.
- The database account exists and has the required permissions.
- The database password is correct.
- `DATABASE_URL` uses the correct host, port, and database name.
- For MAMP, the MySQL port is commonly `8889`; confirm it in your
  local MAMP configuration.

If the connection is still refused, verify that the MySQL service is
listening on the configured host and port.

### Integration Tests Fail Before Running

The test configuration is loaded from `backend/.env.test` through
`tests/conftest.py`. Make sure this file defines `DATABASE_URL` and
points to the dedicated test database (`warband_hq_test`).

The integration tests explicitly check the database name and fail if
a different database is selected.

If the configuration is missing or incorrect, verify the contents of
`backend/.env.test` and ensure MySQL is running and accessible.

### Frontend Cannot Reach the Backend

Check the following:

- The FastAPI backend is running on port `8000`.
- The Vite frontend is running on port `5173`.
- The frontend API configuration points to the correct backend URL:

```text
http://127.0.0.1:8000
```

- The backend CORS configuration allows the frontend origin:

```text
http://127.0.0.1:5173
```

Use the same hostname consistently for both services. Browsers may
treat `localhost` and `127.0.0.1` as different origins.

If the connection still fails, check the browser console and backend
logs for network or CORS errors.

### Blizzard OAuth Fails

Check the following:

- The Blizzard client ID and client secret are correct in
  `backend/.env`.
- `BLIZZARD_REGION` is set to the intended Blizzard API region.
- `BLIZZARD_REDIRECT_URI` exactly matches the redirect URI configured
  in the Blizzard Developer Portal.
- The callback endpoint is available at
  `/api/auth/callback`.
- The backend is running and does not report OAuth or session
  configuration errors.

If authentication still fails, inspect the backend logs and verify
the OAuth configuration before trying again.

Never include the client secret in frontend code, screenshots, or
public logs.

### Session Is Not Preserved

Check the following:

- Frontend API requests include credentials where required.
- Backend session settings are correctly configured.
- CORS allows the frontend origin and supports credentials.
- The frontend and backend use the same hostname consistently.

For local development, verify the existing cookie settings before
changing them. Avoid weakening production security settings to solve
local session issues.

If the session is still not preserved, inspect the browser's
developer tools to check whether session cookies are being stored
and sent with API requests.

### Node.js Dependencies or Build Failures

From the `frontend` directory, check the Node.js and npm versions:

```bash
node --version
npm --version
```

Install the project dependencies and run the frontend checks:

```bash
npm install
npm run lint
npm run build
```

If installation or build fails:

- Check that the installed Node.js version is compatible with the
  project dependencies.
- Read the npm error output to identify the cause.
- Check for dependency or configuration issues before making changes.
- Avoid deleting package-lock.json or reinstalling packages
  unnecessarily.

## Security Notes

- Never commit `.env` files or other files containing real credentials.
- Never expose Blizzard client secrets in frontend code.
- Use a strong, randomly generated session secret.
- Use a dedicated MySQL account with limited permissions for the
  application.
- Do not expose a database service directly to the public internet.
- Restrict CORS to the origins required by the application.
- Use HTTPS and secure cookie settings when deploying outside local
  development.
- Never publish logs containing tokens, session identifiers,
  passwords, or other secrets.
- Keep real credentials out of source code, screenshots, and
  documentation.

## Project Status

Warband HQ is developed incrementally using Agile sprints and user
stories.

- **US-01 --- Blizzard Authentication:** authentication and frontend integration implemented.
- **US-02 --- Character Retrieval:** character retrieval, database persistence, and import workflow implemented.
- **US-03 --- Character Overview:** character collection displayed in grid and list views.
- **US-04 --- Main Character Information:** character information including average and equipped item levels retrieved and displayed.
- **US-05 --- Error Handling:** API errors for invalid or unavailable profile data.
- **US-06 --- Character Details:** dedicated character details page with identity header, equipment, and primary and secondary statistics.
- **US-07 --- Character Filtering and Sorting:** search, filtering, and sorting.
- **US-08 --- Character Favorites:** persistent favorite management and favorites-only filtering.
- **US-09 --- Global Character Tag Management:** global tag catalogue, administrator-only catalogue management, and character tag assignment.
- **US-10 --- Personal Goals:** creation and management of personal goals associated with the Warband or individual characters.
- **US-11 --- Tasks:** task creation, management, completion tracking, and association with personal goals.
- **US-20 --- Character Tag Management & Performance:** assigned tags displayed in My Warband and managed from the character details page.
- **US-21 --- Switch Battle.net Account:** confirmation modal, separate-tab Battle.net logout, same-account detection, and session replacement after successful OAuth. Users return manually to Warband HQ and select "Log in with Battle.net" to complete the switch.

Update project status as user stories are completed and verified.

## License

To be defined.
