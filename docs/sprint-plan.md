# Warband HQ — Sprint Plan

## 1. Sprint Planning Overview

The development of Warband HQ is divided into short and manageable sprints.

The objective is to progressively implement the MVP while keeping each sprint focused on a clearly defined scope.

The database structure will be developed progressively throughout the relevant sprints rather than being fully implemented at the beginning of the project.

| Sprint   | Focus                                         | Duration | Main Objective                                                       |
| -------- | --------------------------------------------- | -------: | -------------------------------------------------------------------- |
| Sprint 0 | Project Planning & Development Foundation     | 3–4 days | Define the backlog, priorities, dependencies and sprint organization |
| Sprint 1 | Backend Foundation                            | 5–7 days | Establish the backend technical foundation and database connectivity |
| Sprint 2 | Blizzard Authentication & Character Retrieval | 4–5 days | Implement Blizzard authentication and retrieve available characters  |
| Sprint 3 | Character Overview & Organization             | 4–5 days | Display and organize imported characters                             |
| Sprint 4 | Character Details & Progression               | 3–4 days | Implement detailed character information and progression data        |
| Sprint 5 | Goals, Tasks & Character Notes                | 3–4 days | Implement personal organization features                             |
| Sprint 6 | MVP Integration, Testing & Finalization       |   3 days | Integrate, test and finalize the MVP                                 |

The MVP development period is planned during October 2026.

Sprint durations are estimates and may be adjusted according to development progress, technical difficulties and validation results.

---

## 2. Sprint 0 — Project Planning & Development Foundation

### Objective

Establish the project foundation before beginning feature development.

### Activities

- Define the Product Backlog.
- Document the User Stories.
- Apply MoSCoW prioritization.
- Define MVP scope.
- Identify dependencies between User Stories.
- Define sprint organization.
- Define sprint durations.
- Define responsibilities.
- Establish the development workflow.
- Review the technical documentation before development.

### Dependencies

None.

### Status

Completed.

---

## 3. Sprint 1 — Backend Foundation

### Objective

Establish the technical foundation required to develop the Warband HQ backend.

### Activities

- Configure the Python development environment.
- Configure FastAPI and Uvicorn.
- Configure the backend dependencies.
- Set up PostgreSQL for the development environment.
- Create the Warband HQ database.
- Create the dedicated application database user.
- Document the initial PostgreSQL setup.
- Configure environment variables.
- Configure application settings with Pydantic Settings.
- Configure SQLAlchemy and the PostgreSQL driver.
- Establish the backend-to-database connection.
- Implement the first `/health` endpoint.
- Make the health endpoint verify the database connection.
- Implement global API error handling.
- Set up automated backend testing.
- Add initial tests for the backend health and database connectivity.

### Database Scope

The database is intentionally not fully implemented during this sprint.

Only the infrastructure required for the backend to connect to PostgreSQL is established.

Application data models and database tables will be introduced progressively during the sprints that require them.

### User Stories

Technical preparation for:

- US-01 — Blizzard Authentication
- US-02 — Character Retrieval
- US-05 — Error Handling

### Dependencies

- Sprint 0 completed.
- PostgreSQL development environment available.

### Deliverable

A functional FastAPI backend capable of connecting to PostgreSQL, with a working health endpoint, basic error handling and automated tests.

---

## 4. Sprint 2 — Blizzard Authentication & Character Retrieval

### Objective

Implement Blizzard authentication and retrieve the World of Warcraft characters available to the authenticated user.

### Activities

- Implement Blizzard OAuth authentication.
- Implement the authentication callback.
- Manage the authentication session.
- Implement logout.
- Configure the Blizzard API client.
- Connect the backend to the Blizzard Profile APIs.
- Retrieve the user's WoW account profile.
- Retrieve available WoW characters.
- Implement the required database structures for authenticated users and imported characters.
- Implement character import.
- Implement error handling for authentication and character retrieval.
- Add automated tests for authentication and character retrieval.

### User Stories

- US-01 — Blizzard Authentication
- US-02 — Character Retrieval
- US-05 — Error Handling

### Dependencies

- Sprint 1 completed.

### Deliverable

A user can authenticate with Blizzard and retrieve the available World of Warcraft characters.

---

## 5. Sprint 3 — Character Overview & Organization

### Objective

Provide a centralized interface for viewing and organizing imported characters.

### Activities

- Implement the Character Overview page.
- Display the main character information.
- Retrieve imported characters from the backend.
- Implement character filtering.
- Implement character sorting.
- Implement character favorites.
- Implement character tags.
- Add the required database structures for favorites and tags.
- Implement the corresponding backend services and endpoints.
- Add automated tests for character organization features.

### User Stories

- US-03 — Character Overview
- US-07 — Character Filtering and Sorting
- US-08 — Character Favorites
- US-09 — Character Tags

### Dependencies

- Sprint 2 completed.

### Deliverable

A centralized character overview allowing users to find and organize their characters.

---

## 6. Sprint 4 — Character Details & Progression

### Objective

Implement the detailed character view and selected progression information.

### Activities

- Implement the Character Details page.
- Retrieve detailed character information from Blizzard.
- Retrieve character media.
- Retrieve equipment information.
- Retrieve selected progression information.
- Process and combine Blizzard API data.
- Display the information through the frontend.
- Implement character synchronization.
- Add the required database structures for character synchronization metadata.
- Implement error handling for unavailable character information.
- Add automated tests for character details and progression.

### User Stories

- US-04 — Main Character Information
- US-06 — Detailed Character View
- US-13 — Activity Tracking
- US-14 — Advanced Statistics
- US-15 — Clear Information Presentation

### Dependencies

- Sprint 3 completed.
- Blizzard character retrieval implemented.

### Deliverable

A functional detailed character view containing the selected progression information available through the Blizzard APIs.

---

## 7. Sprint 5 — Goals, Tasks & Character Notes

### Objective

Implement the personal organization features of Warband HQ.

### Activities

- Implement personal goals.
- Implement tasks associated with goals.
- Implement private character notes.
- Create the required database structures progressively.
- Implement the corresponding backend services and endpoints.
- Implement frontend interfaces for managing goals, tasks and notes.
- Add validation and error handling.
- Add automated tests for these features.

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

### Activities

- Integrate all implemented backend features.
- Integrate the frontend with the backend.
- Verify the complete authentication flow.
- Verify character retrieval and display.
- Verify character details and progression.
- Verify organization features.
- Verify goals, tasks and notes.
- Run automated tests.
- Perform API testing.
- Perform integration testing.
- Perform end-to-end testing of the main user flows.
- Fix identified bugs.
- Review MVP requirements.
- Verify that the implemented features match the Product Backlog and technical documentation.
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
