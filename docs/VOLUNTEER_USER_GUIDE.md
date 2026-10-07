# Warrigal Park Football Club System
## Volunteer User Guide

This guide explains how club volunteers can use the Warrigal Park Football Club system to manage members, guardians, registrations, teams, rosters, and reports.

## 1. Starting the Application

From the project folder, start the application with:

    python app.py

Open a web browser and go to:

    http://127.0.0.1:5000

The home page provides access to the main club administration functions.

## 2. Search and View Members

Use the Members page to find existing member records.

1. Open the Members page.
2. Enter all or part of the member's name in the search field.
3. Submit the search.
4. Review the matching member records.

Search is case-insensitive and supports partial names.

Check for an existing member before creating another registration to help avoid duplicate records.

## 3. Create and Manage Guardians

Guardian records are used for junior members.

### Create a guardian

1. Open the guardian creation page.
2. Enter the guardian's name and available contact information.
3. Enter the relationship and address where applicable.
4. Submit the form.
5. Confirm that the guardian record was created successfully.

### Find a guardian

Use the Guardians page to search existing guardian records by available identifying information such as name or contact details.

### Update a guardian

Open the guardian record, select the edit option, update the required details, and save the changes.

### Deactivate a guardian

Where administration access permits, a guardian can be deactivated instead of being deleted.

Deactivation keeps the existing record and its history while preventing the inactive guardian from being selected for new junior registrations.

## 4. Register a Member

1. Open New Registration.
2. Enter the member's name.
3. Enter the member's date of birth.
4. Enter the registration season.
5. Enter the age group.
6. For a junior member, select an existing active guardian.
7. Submit the registration.

The system validates the information before saving the registration.

A junior registration cannot be completed without a valid linked guardian.

If the system reports that a matching member already exists, check the existing member and registration history rather than creating a duplicate record.

## 5. View Registration History

1. Open Registration History.
2. Select the member whose history is required.
3. Submit the selection.
4. Review the registration records displayed for that member.

This allows volunteers to review registration information across seasons.

## 6. Create a Team

1. Open New Team.
2. Enter the team name.
3. Enter the season.
4. Enter the age group.
5. Submit the form.

The system prevents creation of another team with the same team name, season, and age group.

## 7. View and Manage Team Rosters

Open the Teams page and select the required team.

The team roster displays the team name, season, age group, player count, and assigned players.

Players are displayed in alphabetical order to make the roster easier to review.

## 8. Add a Player to a Team

1. Open the required team.
2. Select Add Player.
3. Choose an available registered player.
4. Submit the selection.

A player can only be assigned when the registration season and age group match the team.

Players who are already assigned to a team cannot be added again without first being moved or removed.

## 9. Move a Player

1. Open the player's current team roster.
2. Select Move beside the player.
3. Select the destination team.
4. Submit the change.

The destination team must have the same season and age group as the player's current team registration.

## 10. Remove a Player from a Team

1. Open the team roster.
2. Select Remove beside the player.
3. Confirm the action.

Removing a player from a team does not delete the member or registration record. The player returns to the unassigned list and can later be assigned to another suitable team.

## 11. Reports

Open the Reports page to review registration and team information.

The report provides:

- total registration information;
- registration counts by season;
- season and age-group information; and
- team roster information.

Registration information can also be exported as a CSV file.

## 12. Print Reports

1. Open the Reports page.
2. Select Print Report.
3. Review the browser print preview.
4. If the browser adds unwanted page URLs, dates, or times, turn off the browser's Headers and footers option.
5. Select the required printer or Save as PDF.
6. Complete the print or save operation.

The print layout is designed to exclude navigation controls and other screen-only actions.

## 13. Print a Team Roster

1. Open the required team roster.
2. Select Print Roster.
3. Review the print preview.
4. Turn off browser Headers and footers if required.
5. Print the roster or save it as a PDF.

The printed roster includes the team details and player list while excluding management buttons such as Move and Remove.

## 14. Download a Team Roster

Select Download Roster CSV from the team roster page.

The downloaded file contains the roster information in a spreadsheet-compatible CSV format.

When opened in spreadsheet software, a column may need to be widened if a date or other value is not fully visible. This does not mean the CSV data is damaged.

## 15. Common Validation Messages

### Junior registration requires a guardian

Select an existing active guardian before completing the junior registration.

### Duplicate member or registration

Check the existing member record and registration history before attempting to create another record.

### Duplicate team

A team with the same name, season, and age group already exists. Use the existing team or enter different team details.

### Player cannot be added or moved

Confirm that the player's registration season and age group match the destination team.

### Team cannot be deleted

A team with assigned players cannot be deleted. Move or remove its players first.

## 16. Administration and Data Safety

Volunteers should avoid deleting or changing records unless the action is required.

Important data-handling rules include:

- search for existing records before creating new ones;
- use existing guardian records where appropriate;
- keep guardian contact information accurate;
- confirm the season and age group before assigning or moving a player;
- use deactivation where provided instead of deleting historical guardian information; and
- remember that removing a player from a team does not delete the member.

Some administrative actions may require an authorised administrator to sign in.

## 17. Getting Help

If an unexpected error occurs:

1. Record what action was being performed.
2. Record any message displayed by the application.
3. Avoid repeatedly submitting the same form.
4. Contact the project administrator or development team with the information.

This helps protect club records and makes problems easier to investigate.
