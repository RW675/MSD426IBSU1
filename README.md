# Warrigal Park Football Club System

Member registration and team roster management system for Warrigal Park Football Club.

## Project overview
The application supports club administration for player registration and team assignment. It allows staff to:
- register a member with date of birth, season, and age group;
- review a full registration history by selected member;
- create a team for a season and age group;
- assign unassigned registrations to the relevant team;
- view and manage a team's roster;
- move a player to another team with the same season and age group; and
- remove a player from a team so they return to the unassigned list.

## Main pages
| Page | Address | Purpose |
|------|---------|---------|
| Home | `/` | Confirms the app is running |
| New registration | `/registrations/new` | Register a member for a season and age group |
| Registration history | `/registrations/history` | View registrations for a selected member |
| New guardian | `/guardians/new` | Record a guardian |
| New team | `/teams/new` | Create a team for a season and age group |
| Add player to team | `/teams/<team_id>/players/add` | Assign an unassigned registration to a team |
| Manage team players | `/teams/<team_id>/manage` | View the roster, with move and remove actions |
| Move player | `/teams/<team_id>/players/<registration_id>/move` | Move a player to another matching team |

Players can only be added to, or moved between, teams with the same season and age group.

## Local setup
1. Create and activate a virtual environment.
2. Install dependencies:
   `pip install -r requirements.txt`
3. Start the application:
   `python app.py`
4. Open the app in a browser at `http://127.0.0.1:5000`.

## Configuration management
This project uses Git for version control and stores environment-specific values in environment variables instead of hard-coding them in source files.

### Branching strategy
- `main` contains the production-ready baseline.
- Feature branches are used for each enhancement to keep work isolated and reviewable.
- Branches are named after the Jira story key, for example `MSD426IBSU1-10-move-remove-player`.
- The `feature/benjamin-registration-history` branch was used to implement the registration history feature and was reviewed and merged into `main` through a pull request.

### Deployment configuration
- `app.py` loads runtime configuration from the `config.py` module.
- `config.py` centralises app settings such as the database URI and secret key.
- `Procfile` provides a simple process configuration for deployment platforms that support it.

### Documentation and change tracking
- Commit history records feature-based work such as registration, team creation, history view, team assignment, and move and remove player updates.
- Descriptive commit messages that start with the Jira story key are used to make the project history auditable and easy to trace.

## Procurement management summary
The application uses a small technology stack:
- Python 3.12+
- Flask for the web application
- Flask-SQLAlchemy for persistence
- SQLite for the default local database
- GitHub for repository hosting and version control
- optional deployment hosting or runtime environment (for example, Render, Heroku, or Azure App Service)

This procurement approach keeps the system low cost, easy to maintain, and compatible with the current project scope while supporting future scaling.

## Repository reference
The project repository is hosted at:
https://github.com/RW675/MSD426IBSU1

## Testing
Run the test suite with:
`python -m pytest -q`

Tests are in the `tests` folder:
- `test_registration.py` covers registration, registration history, team creation, and adding players to teams.
- `test_guardians_and_rosters.py` covers guardians and rosters.
- `test_move_remove_player.py` covers moving and removing players, and the team roster page.

## Notes for assessment submission
The project includes supporting assignment documentation for configuration management and procurement plan, alongside the application code and version-control evidence required for the assessment.