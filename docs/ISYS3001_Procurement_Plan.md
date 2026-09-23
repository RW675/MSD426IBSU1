# ISYS3001 Procurement Plan

## 1. Project context
The Warrigal Park Football Club System is a small web application used to manage player registrations and team assignments. The project requires a low-cost, maintainable software stack that can support local development and future deployment without excessive operational complexity.

## 2. Procurement objectives
The procurement process aims to acquire the minimum viable set of tools and services required for:
- application development;
- database persistence;
- deployment support;
- collaborative source control; and
- project documentation and traceability.

## 3. Requested software and services
| Category | Product | Purpose | Selection rationale |
| --- | --- | --- | --- |
| Programming language | Python 3.12+ | Application runtime | Widely supported and suitable for Flask development |
| Web framework | Flask | Build the web application | Lightweight and suitable for a simple project |
| Database layer | Flask-SQLAlchemy + SQLite | Persistent storage for registrations and teams | Low cost, simple setup, appropriate for a small app |
| Version control | Git + GitHub | Repository management and collaboration | Best practice for software configuration management |
| Deployment support | Heroku, Render, Azure App Service, or equivalent | Host the application for access beyond local development | Flexible hosting options with small project scalability |
| Testing | pytest | Validate functionality and prevent regression | Common Python testing tool and aligns with project quality assurance |

## 4. Procurement process
The procurement process for this project follows a simple decision model based on cost, compatibility, maintainability, and project scope.

### Requirement identification
The project requirements were defined by the application features, including:
- member registration;
- registration history lookup;
- team creation;
- player assignment to teams.

### Vendor and tool evaluation
The selected stack was evaluated against practical maturity and ease of integration. Python and Flask provide a low-friction development path, while SQLite keeps costs at zero for a simple trial deployment. GitHub offers free repository hosting and public version control history suitable for academic coursework.

### Selection decision
The selected tools are appropriate for this project because they are affordable, familiar to the development workflow, and aligned with the scale of the application. They also support future expansion if the club requires a fuller online administration system later.

## 5. Procurement constraints and considerations
- Budget: low-cost or free approach preferred.
- Compatibility: tools must work with Python-based web development.
- Maintainability: solution must be simple to deploy and support future changes.
- Security: configuration values such as `SECRET_KEY` and database connection settings must not be hard-coded in the source repository.

## 6. RFP summary
Request for Proposal (RFP) summary:

Title: Small-scale web application platform and hosting support for club administration service.

Purpose:
Provide a lightweight web application platform to support member registration and team management for a football club.

Required features:
- Python-based web app hosting;
- relational data storage for registration and team records;
- easy deployment and rollback capabilities;
- low operational cost;
- support for version-controlled source code and staging deployment practices.

Expected outcome:
The selected software stack will support a reliable and maintainable registration and roster system for Warrigal Park Football Club.

## 7. Conclusion
The procurement plan adopts an economical, fit-for-purpose stack with Python, Flask, SQLite, GitHub, and optional external hosting. This approach satisfies the project scope while ensuring the solution remains maintainable, secure, and appropriate for a small software development project.
