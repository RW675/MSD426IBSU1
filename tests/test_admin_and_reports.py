from datetime import date

from app import app, db
from models import Member, Registration, Team


def test_duplicate_member_registration_is_blocked():
    with app.app_context():
        member = Member(
            name="Duplicate Member",
            date_of_birth=date(2015, 1, 5),
        )
        db.session.add(member)
        db.session.commit()

        with app.test_client() as client:
            response = client.post(
                "/registrations/new",
                data={
                    "member_name": "duplicate member",
                    "date_of_birth": "2015-01-05",
                    "season": "2026",
                    "age_group": "U11",
                },
            )

            assert response.status_code == 400
            assert b"already exists" in response.data.lower()


def test_reports_page_and_csv_export_work():
    with app.app_context():
        team = Team(
            name="U13 Gold",
            season="2026",
            age_group="U13",
        )
        member = Member(
            name="Report Player",
            date_of_birth=date(2014, 4, 12),
        )
        registration = Registration(
            member=member,
            season="2026",
            age_group="U13",
            team=team,
        )

        db.session.add_all([team, member, registration])
        db.session.commit()

        with app.test_client() as client:
            page = client.get("/reports")

            assert page.status_code == 200
            assert b"Registration and Roster Report" in page.data

            csv_response = client.get(
                "/reports/registrations.csv"
            )

            assert csv_response.status_code == 200
            assert b"member_name" in csv_response.data
            assert b"Report Player" in csv_response.data


def test_admin_login_and_session_work():
    original_enabled = app.config.get("ADMIN_ENABLED")
    original_username = app.config.get("ADMIN_USERNAME")
    original_password = app.config.get("ADMIN_PASSWORD")

    try:
        app.config["ADMIN_ENABLED"] = True
        app.config["ADMIN_USERNAME"] = "clubadmin"
        app.config["ADMIN_PASSWORD"] = "securepass"

        with app.test_client() as client:
            invalid = client.post(
                "/login",
                data={
                    "username": "wrong",
                    "password": "wrong",
                },
            )

            assert invalid.status_code == 401

            valid = client.post(
                "/login",
                data={
                    "username": "clubadmin",
                    "password": "securepass",
                },
                follow_redirects=False,
            )

            assert valid.status_code == 302

            with client.session_transaction() as session:
                assert session.get("is_admin") is True

    finally:
        app.config["ADMIN_ENABLED"] = original_enabled
        app.config["ADMIN_USERNAME"] = original_username
        app.config["ADMIN_PASSWORD"] = original_password