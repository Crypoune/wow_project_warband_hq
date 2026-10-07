# Warband HQ - Sprint Plan

## 1. Sprint Planning

The Warband HQ development is divided into short iterations in order to progressively build and validate the MVP.

The sprint organization is based on:

- User Story priorities defined using the MoSCoW method.
- Dependencies between features.
- The technical architecture of the application.
- Progressive integration between the backend, Blizzard APIs, database and frontend.
- Testing and validation of each major feature before moving to the next stage.

Warband HQ is developed individually by myself. Therefore, all development, project management, UI/UX, documentation and testing responsibilities are assigned to me.

---

## 2. Sprint Overview

| Sprint   | Duration | Main Objective                                  | Priority  | Status  |
| -------- | -------- | ----------------------------------------------- | --------- | ------- |
| Sprint 0 | 3-4 days | Project planning and development foundation     | Must Have | Planned |
| Sprint 1 | 5-7 days | Backend foundation                              | Must Have | Planned |
| Sprint 2 | 4-5 days | Blizzard authentication and character retrieval | Must Have | Planned |
| Sprint 3 | 4-5 days | Character overview and organization             | Must Have | Planned |
| Sprint 4 | 3-4 days | Character details and progression               | Must Have | Planned |
| Sprint 5 | 3-4 days | Goals, tasks and character notes                | Must Have | Planned |
| Sprint 6 | 3 days   | MVP integration, testing and finalization       | Must Have | Planned |

---

### Sprint Duration

The MVP development is planned across the month of October 2026.

Sprints are intentionally kept short, with a duration of approximately 3 to 7 days depending on the scope and dependencies of each iteration.

The exact dates may be adjusted during development according to progress, blockers and validation results.

---

## 3. Sprint 0 - Planning and Foundation

### Objective

Prepare the project structure, requirements and development plan before implementing the main MVP features.

### Main Activities

- Define and validate the Product Backlog.
- Define the Sprint Plan.
- Review the Technical Documentation.
- Confirm the MVP scope.
- Confirm technical architecture and development environment.
- Identify dependencies between User Stories.

### Deliverables

- Product Backlog
- Sprint Plan
- Validated MVP scope
- Development environment ready

### User Stories

No User Story is implemented during this sprint.

### Dependencies

This sprint provides the planning foundation for all subsequent sprints.

---

## 4. Sprint 1 - Backend Foundation

### Objective

Establish the backend foundation required for authentication, Blizzard API integration and application data management.

### Main Activities

- Set up the backend application.
- Configure the application environment.
- Configure PostgreSQL.
- Establish the backend project structure.
- Prepare database models required by the application.
- Prepare the Blizzard API integration layer.
- Establish the basic API structure.
- Prepare error handling.

### User Stories

Technical preparation for:

- US-01 - Blizzard Authentication
- US-02 - Character Retrieval
- US-05 - Error Handling

### Dependencies

Sprint 0.

---

## 5. Sprint 2 - Blizzard Authentication and Character Retrieval

### Objective

Allow a player to authenticate with Blizzard and retrieve the characters available on their World of Warcraft account.

### Main Activities

- Implement Blizzard OAuth authentication.
- Handle the OAuth callback.
- Manage the authenticated session.
- Connect the backend to the Blizzard Profile APIs.
- Retrieve the player's World of Warcraft account information.
- Retrieve available characters.
- Adapt Blizzard API responses for the application.
- Implement character retrieval errors.
- Test the authentication and character retrieval flow.

### User Stories

- US-01 - Blizzard Authentication
- US-02 - Character Retrieval
- US-05 - Error Handling

### Dependencies

- Sprint 1
- US-01 before US-02

---

## 6. Sprint 3 - Character Overview and Organization

### Objective

Provide the player with a centralized view of their characters and basic organization features.

### Main Activities

- Implement the Character Overview interface.
- Display character cards.
- Display main character information.
- Implement character filtering.
- Implement character sorting.
- Implement character favorites.
- Implement character tags.

### User Stories

- US-03 - Character Overview
- US-04 - Main Character Information
- US-07 - Character Filtering and Sorting
- US-08 - Character Favorites
- US-09 - Character Tags

### Dependencies

- Sprint 2
- US-02 before US-03
- US-03 before organization features

---

## 7. Sprint 4 - Character Details and Progression

### Objective

Allow the player to select a character and access more detailed information about its progression.

### Main Activities

- Implement the Character Details interface.
- Retrieve detailed character information.
- Retrieve character media.
- Retrieve equipment information.
- Retrieve achievement progression.
- Retrieve profession information.
- Display detailed character progression.
- Implement character synchronization.
- Test the detailed character flow.

### User Stories

- US-06 - Detailed Character View

### Dependencies

- Sprint 3
- US-03 and US-04

---

## 8. Sprint 5 - Goals, Tasks and Character Notes

### Objective

Add the personal organization features included in the MVP.

### Main Activities

- Implement personal goals.
- Implement task management.
- Associate tasks with goals.
- Track task completion.
- Implement private character notes.
- Validate access to user-owned data.

### User Stories

- US-10 - Personal Goals
- US-11 - Tasks
- US-12 - Character Notes

### Dependencies

- Sprint 3
- US-10 before US-11

---

## 9. Sprint 6 - MVP Integration, Testing and Finalization

### Objective

Integrate the complete MVP and validate that the implemented features satisfy the project requirements.

### Main Activities

- Integrate frontend and backend features.
- Perform end-to-end testing.
- Test authentication.
- Test character retrieval.
- Test character overview.
- Test character details.
- Test filtering and sorting.
- Test favorites and tags.
- Test goals and tasks.
- Test character notes.
- Test error handling.
- Fix identified bugs.
- Review MVP requirements.
- Update project documentation.
- Prepare the final project presentation.

### User Stories

Validation of:

- US-01 to US-12

### Dependencies

All previous sprints.

---

## 10. Future Backlog

The following User Stories are not part of the initial Must Have implementation scope.

### Should Have

- US-13 - Activity Tracking
- US-14 - Advanced Statistics
- US-15 - Clear Information Presentation

### Could Have

- US-16 - Custom Collections
- US-17 - Public Sharing
- US-18 - Character Comparison

### Won't Have

- US-19 - Data Persistence

These features may be considered for future iterations depending on the available development time and project scope.

---

## 11. Responsibilities

Because Warband HQ is an individual project, all sprint responsibilities are assigned to Arnaud Messenet.

| Responsibility           | Assigned To     |
| ------------------------ | --------------- |
| Project Management       | Arnaud Messenet |
| Backend Development      | Arnaud Messenet |
| Frontend Development     | Arnaud Messenet |
| Blizzard API Integration | Arnaud Messenet |
| Database Development     | Arnaud Messenet |
| UI/UX Design             | Arnaud Messenet |
| Testing / QA             | Arnaud Messenet |
| Documentation            | Arnaud Messenet |

---

## 12. Sprint Status

Sprint status will be updated during development.

Possible statuses:

- Planned
- In Progress
- Testing
- Completed
- Blocked
