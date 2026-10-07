# Warband HQ — Product Backlog

## Product Backlog V1

The Product Backlog contains all User Stories identified for the Warband HQ project.

User Stories are prioritized using the MoSCoW method:

- **Must Have** — Essential functionality required for the MVP to operate.
- **Should Have** — Important functionality that improves the MVP but is not essential.
- **Could Have** — Useful functionality that may be implemented if time and resources allow.
- **Won't Have** — Functionality intentionally excluded from the current MVP.

The backlog will be progressively refined during development. Technical tasks will be defined when the corresponding User Stories are selected for a sprint.

---

## Must Have

| ID    | User Story                                                                                                                                 | Priority  | Dependency   | Status  |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------ | --------- | ------------ | ------- |
| US-01 | As a World of Warcraft player, I want to log in with my Blizzard account so that I can access my character information.                    | Must Have | —            | Backlog |
| US-02 | As a logged-in player, I want to retrieve my World of Warcraft characters so that I can see the characters available on my account.        | Must Have | US-01        | Backlog |
| US-03 | As a player, I want to view my characters in a centralized interface so that I can quickly get an overview of my characters.               | Must Have | US-02        | Backlog |
| US-04 | As a player, I want to view the main information about a character so that I can better understand its current status and progression.     | Must Have | US-03        | Backlog |
| US-05 | As a player, I want to be informed when information cannot be retrieved so that I can understand why my character data is unavailable.     | Must Have | US-01, US-02 | Backlog |
| US-06 | As a player, I want to select a character so that I can view a more detailed overview of its information and progression.                  | Must Have | US-03, US-04 | Backlog |
| US-07 | As a player, I want to filter or sort my characters so that I can find a specific character more easily.                                   | Must Have | US-03        | Backlog |
| US-08 | As a player, I want to mark characters as favorites so that I can quickly identify the characters I use or track most often.               | Must Have | US-03        | Backlog |
| US-09 | As a player, I want to assign tags to my characters so that I can organize and categorize them according to my needs.                      | Must Have | US-03        | Backlog |
| US-10 | As a player, I want to create and manage personal goals so that I can organize what I want to accomplish in the game.                      | Must Have | US-01        | Backlog |
| US-11 | As a player, I want to create and manage tasks within my goals so that I can break my objectives into smaller actions.                     | Must Have | US-10        | Backlog |
| US-12 | As a player, I want to create and manage a private note for each character so that I can record personal information about that character. | Must Have | US-03        | Backlog |

---

## Should Have

| ID    | User Story                                                                                                                                  | Priority    | Dependency   | Status  |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ------------ | ------- |
| US-13 | As a player, I want to track my Mythic+, raid, and PvP activities so that I can centralize all my progression in the game.                  | Should Have | US-03, US-06 | Backlog |
| US-14 | As a player, I want to view advanced statistics about my progression so that I can analyze my performance.                                  | Should Have | US-06        | Backlog |
| US-15 | As a player, I want my character information to be presented in a clear and understandable way so that I can quickly review my progression. | Should Have | US-03, US-06 | Backlog |

---

## Could Have

| ID    | User Story                                                                                                                                  | Priority   | Dependency | Status  |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------- | ---------- | ---------- | ------- |
| US-16 | As a player, I want to create custom collections so that I can organize characters or game-related objectives according to my own criteria. | Could Have | US-03      | Backlog |
| US-17 | As a player, I want to share selected information publicly so that I can allow other players to view parts of my Warband HQ progression.    | Could Have | US-03      | Backlog |
| US-18 | As a player, I want to compare two or more characters so that I can easily identify differences in their progression and equipment.         | Could Have | US-06      | Backlog |

---

## Won't Have

| ID    | User Story                                                                                                                                                   | Priority   | Dependency | Status       |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------- | ---------- | ------------ |
| US-19 | As a player, I want to be able to view my character information even when the Blizzard API is unavailable so that I can access the latest synchronized data. | Won't Have | —          | Out of Scope |

---

## Backlog Status

| Status       | Description                                         |
| ------------ | --------------------------------------------------- |
| Backlog      | User Story identified but not yet scheduled         |
| In Progress  | Currently being developed                           |
| Testing      | Implementation completed and currently being tested |
| Done         | User Story completed and validated                  |
| Out of Scope | Intentionally excluded from the current MVP         |

---

## Notes

- Warband HQ is developed individually, so all responsibilities are assigned to Arnaud Messenet.
- The Product Backlog represents the functional scope of the project.
- Technical implementation tasks will be defined when User Stories are selected for a sprint.
- Sprint assignment will be defined in the Sprint Plan.
