# Warband HQ — Sprint Plan

## 1. Sprint Planning Overview

The development of Warband HQ is divided into short and manageable sprints.

The objective is to progressively implement the MVP while keeping each sprint focused on a clearly defined scope.

The database structure will be developed progressively throughout the relevant sprints rather than being fully implemented at the beginning of the project.

The frontend and backend will be developed progressively in parallel. Each sprint will implement the frontend components required to consume and validate the corresponding backend features.

| Sprint   | Focus                                         | Duration | Main Objective                                                                             |
| -------- | --------------------------------------------- | -------: | ------------------------------------------------------------------------------------------ |
| Sprint 0 | Project Planning & Development Foundation     | 3–4 days | Define the backlog, priorities, dependencies and sprint organization                       |
| Sprint 1 | Backend Foundation                            | 5–7 days | Establish the backend technical foundation and database connectivity                       |
| Sprint 2 | Blizzard Authentication & Character Retrieval | 4–5 days | Implement authentication, character retrieval and the initial frontend authentication flow |
| Sprint 3 | Character Overview & Organization             | 4–5 days | Display and organize imported characters                                                   |
| Sprint 4 | Character Details & Progression               | 3–4 days | Implement detailed character information and progression data                              |
| Sprint 5 | Goals, Tasks & Character Notes                | 3–4 days | Implement personal organization features                                                   |
| Sprint 6 | MVP Integration, Testing & Finalization       |   3 days | Integrate, test and finalize the MVP                                                       |

The MVP development period is planned during October 2026.

Sprint durations are estimates and may be adjusted according to development progress, technical difficulties and validation results.

---

## 2. Sprint 0 — Project Planning & Development Foundation

### Objective

Establish the project foundation and define the development plan before implementing the MVP.

### Activities

- Define the project scope.
- Define the Product Backlog.
- Identify and prioritize User Stories using the MoSCoW method.
- Identify dependencies between User Stories.
- Define the sprint organization.
- Define sprint durations.
- Define project roles and responsibilities.
- Prepare the technical documentation.
- Define the technical architecture.
- Define the initial database architecture.
- Prepare the development environment.

### User Stories

Technical preparation for all MVP User Stories.

### Dependencies

- Project requirements defined.

### Deliverable

A documented project plan, Product Backlog and Sprint Plan ready for MVP development.

---

## 3. Sprint 1 — Backend Foundation

### Objective

Establish the technical foundation required to develop the Warband HQ backend.

### Activities

- Configure the Python development environment.
- Configure FastAPI and Uvicorn.
- Configure the backend dependencies.
- Set up MySQL for the development environment.
- Create the Warband HQ database.
- Create the dedicated application database user.
- Document the initial MySQL setup.
- Configure environment variables.
- Configure application settings with Pydantic Settings.
- Configure SQLAlchemy and the MySQL driver.
- Establish the backend-to-database connection.
- Implement the first `/health` endpoint.
- Make the health endpoint verify the database connection.
- Implement global API error handling.
- Set up automated backend testing.
- Add initial tests for the backend health and database connectivity.

### Database Scope

The database is intentionally not fully implemented during this sprint.

Only the infrastructure required for the backend to connect to MySQL is established.

Application data models and database tables will be introduced progressively during the sprints that require them.

### User Stories

Technical preparation for:

- US-01 — Blizzard Authentication
- US-02 — Character Retrieval
- US-05 — Error Handling

### Dependencies

- Sprint 0 completed.
- MySQL development environment available.

### Deliverable

A functional FastAPI backend capable of connecting to MySQL, with a working health endpoint, basic error handling and automated tests.

---

## 6. Sprint 4 — Character Details & Progression

### Objective

Implement the detailed character view, selected progression information, and the ability to switch the connected Battle.net account.

### Backend Activities

- Implement the character details endpoint.
- Retrieve detailed character information from Blizzard.
- Retrieve character media.
- Retrieve character equipment.
- Retrieve relevant progression information.
- Implement character synchronization where required.
- Add the required database structures for synchronization metadata.
- Implement error handling for detailed character data.
- Add automated tests for character details and progression.
- Include assigned character tags in the character listing and character details API responses.
- Retrieve character tag assignments through a grouped query to avoid per-character requests.
- Preserve existing authentication and character ownership checks for tag operations.
- Add automated tests for tag retrieval, assignment and removal, and unauthorized access.
- Implement the account-switching flow between the existing Warband HQ session and a new Battle.net authentication.
- Preserve the existing Warband HQ session until the new authentication succeeds.
- Replace the existing authentication session only after successful authentication with the selected account.
- Handle failed or cancelled authentication, OAuth state validation, and cases where the same Battle.net account is returned.
- Add automated tests for successful account switching, same-account authentication, and failed or cancelled switching.

### Frontend Activities

- Implement the Character Details page.
- Display detailed character information.
- Display character media.
- Display equipment information.
- Display selected progression information.
- Connect the Character Details page to the backend.
- Display loading and error states.
- Display assigned tag badges on My Warband character cards without tag management controls.
- Move tag assignment and removal controls to the Character Details page.
- Load the available tag catalogue only when required for tag management.
- Verify tag management behavior and loading states.
- Add a Change Battle.net Account action to the application header.
- Display a confirmation dialog before starting the account-switching flow.
- Redirect the user through the Battle.net logout and authentication flow.
- Return the user to Warband HQ after authentication and refresh the authenticated application state.
- Handle cancelled or failed account switching without leaving the interface in an inconsistent state.

### User Stories

- US-04 — Main Character Information
- US-06 — Detailed Character View
- US-20 — Character Tag Management & Performance
- US-21 — Switch Battle.net Account

### Dependencies

- Sprint 3 completed.
- Character management available.
- Existing Blizzard authentication and session management available.

### Deliverable

Users can select a character and view a detailed overview of its information and progression. Character tags remain visible in the Warband overview and can be managed from the character details page, with unnecessary per-character tag requests eliminated.

Authenticated users can also initiate a Battle.net account switch, authenticate with another account, and return to Warband HQ with the new session. Failed or cancelled switching must not prematurely invalidate the existing Warband HQ session.

---

## 5. Sprint 3 — Character Overview & Organization

### Objective

Provide a centralized interface for viewing and organizing imported characters.

### Backend Activities

- Implement the character listing endpoint.
- Retrieve imported characters from the database.
- Implement character filtering.
- Implement character sorting.
- Implement character favorites.
- Implement character tags.
- Add the required database structures for favorites and tags.
- Implement the corresponding backend services and endpoints.
- Add automated tests for character organization features.

### Frontend Activities

- Implement the Character Overview page.
- Display character cards.
- Display the main character information.
- Connect the Character Overview to the backend.
- Implement character filtering.
- Implement character sorting.
- Implement character favorites.
- Implement character tags.
- Display appropriate loading and error states.

### User Stories

- US-03 — Character Overview
- US-07 — Character Filtering and Sorting
- US-08 — Character Favorites
- US-09 — Character Tags

### Dependencies

- Sprint 2 completed.
- Character retrieval available.

### Deliverable

A centralized character overview allowing users to view, find and organize their characters.

---

## 6. Sprint 4 — Character Details & Progression

### Objective

Implement the detailed character view and selected progression information.

### Backend Activities

- Implement the character details endpoint.
- Retrieve detailed character information from Blizzard.
- Retrieve character media.
- Retrieve character equipment.
- Retrieve relevant progression information.
- Implement character synchronization where required.
- Add the required database structures for synchronization metadata.
- Implement error handling for detailed character data.
- Add automated tests for character details and progression.
- Include assigned character tags in the character listing and character details API responses.
- Retrieve character tag assignments through a grouped query to avoid per-character requests.
- Preserve existing authentication and character ownership checks for tag operations.
- Add automated tests for tag retrieval, assignment and removal, and unauthorized access.

### Frontend Activities

- Implement the Character Details page.
- Display detailed character information.
- Display character media.
- Display equipment information.
- Display selected progression information.
- Connect the Character Details page to the backend.
- Display loading and error states.
- Display assigned tag badges on My Warband character cards without tag management controls.
- Move tag assignment and removal controls to the Character Details page.
- Load the available tag catalogue only when required for tag management.
- Verify tag management behavior and loading states.

### User Stories

- US-04 — Main Character Information
- US-06 — Detailed Character View
- US-20 — Character Tag Management & Performance

### Dependencies

- Sprint 3 completed.
- Character management available.

### Deliverable

Users can select a character and view a detailed overview of its information and progression. Character tags remain visible in the Warband overview and can be managed from the character details page, with unnecessary per-character tag requests eliminated.

---

## 7. Sprint 5 — Goals, Tasks & Character Notes

### Objective

Implement personal organization features allowing users to manage goals, tasks and private character notes.

### Backend Activities

- Implement personal goals.
- Implement tasks associated with goals.
- Implement private character notes.
- Create the required database structures progressively.
- Implement the corresponding backend services and endpoints.
- Add validation and error handling.
- Add automated tests for these features.

### Frontend Activities

- Implement the Goals interface.
- Implement goal creation and management.
- Implement task creation and management.
- Implement the Character Notes interface.
- Connect goals, tasks and notes to the backend.
- Display validation and error states.

### User Stories

- US-10 — Personal Goals
- US-11 — Tasks
- US-12 — Character Notes

### Dependencies

- Sprint 3 completed.
- Character management available.

### Deliverable

Users can create and manage personal goals, tasks and private character notes.

---

## 8. Sprint 6 — MVP Integration, Testing & Finalization

### Objective

Integrate the implemented features and validate the complete MVP.

### Backend Activities

- Integrate all implemented backend features.
- Verify all backend endpoints.
- Verify authentication and session management.
- Verify character retrieval and synchronization.
- Run automated tests.
- Fix identified backend issues.

### Frontend Activities

- Integrate all implemented frontend features.
- Verify the complete authentication flow.
- Verify character retrieval and display.
- Verify character details and progression.
- Verify organization features.
- Verify goals, tasks and notes.
- Fix identified frontend issues.
- Verify loading, validation and error states.

### Integration & QA Activities

- Perform API testing.
- Perform integration testing.
- Perform end-to-end testing of the main user flows.
- Review MVP requirements.
- Verify that the implemented features match the Product Backlog and technical documentation.
- Fix identified bugs.
- Prepare the final MVP.

### User Stories

Validation of all implemented MVP User Stories.

### Dependencies

- Sprints 1–5 completed.

### Deliverable

A tested and functional Warband HQ MVP.

---

## 9. Responsibilities

Since Warband HQ is developed individually, all project roles are assumed by the same developer.

| Role                  | Responsibility                                                     |
| --------------------- | ------------------------------------------------------------------ |
| Project Manager       | Sprint planning, prioritization, deadlines and progress tracking   |
| Full Stack Developer  | Frontend, backend, database and API development                    |
| UI/UX Designer        | Interface design and user experience                               |
| Documentation Manager | Technical documentation and project records                        |
| QA / Tester           | Automated tests, manual testing, bug identification and validation |

The project documentation confirms that the project is developed individually and that these complementary roles are assumed by the same developer.
