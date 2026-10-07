# Changelog

## 06/10/2026

### Added
- MSD426IBSU1-10: manage team players page at /teams/<team_id>/manage, showing a team's roster
- MSD426IBSU1-10: move player route and page, to move a player to another team with the same season and age group
- MSD426IBSU1-10: remove player route, so a player returns to the unassigned list
- manage_team_players.html and move_player_to_team.html templates
- tests/test_move_remove_player.py: 9 automated tests for moving, removing and the roster page
- README: new main pages table and updated testing section

### Fixed
- add_player_to_team returned nothing on a GET request (500 error) because the final return render_template was indented inside the POST block

## 28/09/2026

### Added
- config.py: the app reads SECRET_KEY and DATABASE_URL from environment variables
- .env.example: template of the settings
- .env added to .gitignore so real settings are not committed

### Changed
- app.py now loads its settings from config.py
- conftest.py sets DATABASE_URL so tests use an in-memory database

### Fixed
- Tests were running against the real database and wiping it
- Member registration code was removed from main after a merge, and was restored through PR #3

## 21/09/2026 - 23/09/2026

### Added
- Basic Flask app with a home route
- Member and Registration models, connected to SQLite
- Registration form and /registrations/new route
- Automated test for registration (pytest)
- README with setup, run and test instructions