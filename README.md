# Warrigal Park Football Club System

Member registration and team roster management system for Warrigal Park Football Club.

## Project overview
The application supports club administration for player registration and team assignment. It allows staff to:
- register a member with date of birth, season, and age group;
- review a full registration history by selected member;
- create a team for a season and age group; and
- assign unassigned registrations to the relevant team.

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
- The current repository branch is `feature/benjamin-registration-history`, which demonstrates a branch-based workflow for implementing the registration history feature.

### Deployment configuration
- `app.py` loads runtime configuration from the `config.py` module.
- `config.py` centralises app settings such as the database URI and secret key.
- `.env.example` provides a sample environment definition for local or deployment usage.
- `Procfile` provides a simple process configuration for deployment platforms that support it.

### Documentation and change tracking
- Commit history records feature-based work such as registration, team creation, history view, and team assignment updates.
- Descriptive commit messages are used to make the project history auditable and easy to trace.

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
`pytest -q`

## Notes for assessment submission
The project includes supporting assignment documentation for configuration management and procurement plan, alongside the application code and version-control evidence required for the assessment.
