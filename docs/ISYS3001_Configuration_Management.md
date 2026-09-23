# ISYS3001 Configuration Management Report

## 1. Project identity
- Project name: Warrigal Park Football Club System
- GitHub repository: https://github.com/RW675/MSD426IBSU1
- GitHub account name: RW675
- Application purpose: member registration, registration history review, team creation, and team assignment for club administration.

## 2. Configuration management approach
This project applies a lightweight but practical configuration management structure to support controlled changes and maintainable deployment.

### Version control
The project is stored in Git and linked to a GitHub repository. The repository history shows staged feature development across separate branches rather than direct ad hoc changes to the main branch.

### Branching strategy
- `main`: stable production baseline.
- `feature/benjamin-registration-history`: active feature branch for registration and roster enhancements.
- Each feature was developed and committed separately before being merged into the branch flow, supporting traceability and a clean progression of changes.

### Commit discipline and change tracking
The repository history records specific changes such as:
- registration system setup;
- registration history implementation;
- team creation logic;
- assignment of registered players to teams.

This demonstrates a configuration management discipline where code changes are grouped by feature and are documented with commit messages that reflect the purpose of the work.

## 3. Application configuration management
The application uses environment-based configuration to keep deployment settings separate from source code.

### Relevant configuration elements
- `config.py` defines application-level settings.
- `app.py` reads runtime values from environment variables and falls back to sensible local defaults.
- `.env.example` provides a template for environment configuration.
- `Procfile` outlines the application process for deployment systems.

This reduces the risk of hard-coded secrets or environment-specific values being accidentally committed to the repository.

## 4. Deployment configuration
The application uses a standard Flask deployment configuration with a locally configured database and a runtime port value. In development, the app defaults to SQLite for simplicity and portability. In more advanced deployment environments, the `DATABASE_URL` and `SECRET_KEY` values can be injected through environment variables without changing the source code.

## 5. Change log summary
| Stage | Change | Purpose |
| --- | --- | --- |
| Initial setup | Project creation and README | Establish repository baseline |
| Registration feature | Member registration logic | Support player intake |
| History feature | Registration history view | Allow staff review of member records |
| Team feature | Team creation flow | Add team administration |
| Assignment feature | Add player to team | Link registrations to team rosters |

## 6. Evidence of project activity
The repository history shows a clear progression of feature-based commits and branch-based development. The current branch in this workspace is `feature/benjamin-registration-history`, which confirms the use of version control workflows aligned with configuration management practice.

## 7. Conclusion
This project follows configuration management best practice by applying Git version control, feature-based branching, environment variable separation, and deployment configuration files. These controls support reliability, maintainability, and safer software delivery.
