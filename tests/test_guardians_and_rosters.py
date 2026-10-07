from datetime import date

from app import app, db
from models import Guardian, Member, Registration, Team


def test_junior_registration_requires_linked_guardian():
    with app.app_context():
        member = Member(
            name="Junior Player",
            date_of_birth=date(2014, 9, 3),
        )
        db.session.add(member)
        db.session.flush()

        with app.test_client() as client:
            response = client.post(
                "/registrations/new",
                data={
                    "member_name": member.name,
                    "date_of_birth": "2014-09-03",
                    "season": "2026",
                    "age_group": "U13",
                    "status": "complete",
                },
            )

            assert response.status_code == 400
            assert b"guardian" in response.data.lower()


def test_guardian_linked_juniors_share_contact_updates():
    with app.app_context():
        guardian = Guardian(
            name="Dani Kelleher",
            mobile="0417 662 908",
            email="d.kelleher@example.com",
        )
        junior_one = Member(
            name="Mia Kelleher",
            date_of_birth=date(2014, 9, 3),
        )
        junior_two = Member(
            name="Rory Kelleher",
            date_of_birth=date(2017, 5, 11),
        )

        db.session.add_all([guardian, junior_one, junior_two])
        db.session.flush()

        guardian.link_members([junior_one, junior_two])
        db.session.commit()

        guardian.mobile = "0400 111 222"
        db.session.commit()

        assert junior_one.guardian_mobile == "0400 111 222"
        assert junior_two.guardian_mobile == "0400 111 222"


def test_team_roster_lists_players_with_contact_details():
    with app.app_context():
        guardian = Guardian(
            name="S. Antonopoulos",
            mobile="0438 771 226",
        )
        member = Member(
            name="Ruby Antonopoulos",
            date_of_birth=date(2014, 2, 11),
            contact="0438 771 226",
        )
        guardian.link_members([member])

        registration = Registration(
            member=member,
            season="2026",
            age_group="U13",
            status="complete",
        )

        team = Team(
            name="U13G NAVY",
            season="2026",
            age_group="U13",
        )

        db.session.add_all(
            [
                guardian,
                member,
                registration,
                team,
            ]
        )
        db.session.flush()

        registration.team_id = team.id
        db.session.commit()

        roster = team.roster_details()

        assert len(roster) == 1
        assert roster[0]["member_name"] == "Ruby Antonopoulos"
        assert roster[0]["guardian_mobile"] == "0438 771 226"


def test_guardian_details_can_be_updated():
    with app.app_context():
        guardian = Guardian(
            name="Update Test Guardian",
            mobile="0400 123 456",
            email="update@example.com",
            relationship="Parent",
            address="Old Address",
        )

        db.session.add(guardian)
        db.session.commit()

        guardian_id = guardian.id

        with app.test_client() as client:
            response = client.post(
                f"/guardians/{guardian_id}/edit",
                data={
                    "guardian_name": "Updated Test Guardian",
                    "mobile": "0400 999 888",
                    "email": "updated@example.com",
                    "relationship": "Teacher",
                    "address": "New Address",
                },
            )

            assert response.status_code == 302

        updated_guardian = db.session.get(
            Guardian,
            guardian_id,
        )

        assert updated_guardian is not None
        assert updated_guardian.name == "Updated Test Guardian"
        assert updated_guardian.mobile == "0400 999 888"
        assert updated_guardian.email == "updated@example.com"
        assert updated_guardian.relationship == "Teacher"
        assert updated_guardian.address == "New Address"

        db.session.delete(updated_guardian)
        db.session.commit()


def test_guardian_can_be_deactivated_without_being_deleted():
    with app.app_context():
        guardian = Guardian(
            name="Deactivate Test Guardian",
            mobile="0400 555 666",
            email="deactivate@example.com",
            is_active=True,
        )

        db.session.add(guardian)
        db.session.commit()

        guardian_id = guardian.id

        with app.test_client() as client:
            response = client.post(
                f"/guardians/{guardian_id}/deactivate",
            )

            assert response.status_code == 302

        deactivated_guardian = db.session.get(
            Guardian,
            guardian_id,
        )

        assert deactivated_guardian is not None
        assert deactivated_guardian.is_active is False

        db.session.delete(deactivated_guardian)
        db.session.commit()


def test_create_guardian_success():
    with app.app_context():
        with app.test_client() as client:
            response = client.post(
                "/guardians/new",
                data={
                    "guardian_name": "Creation Test Guardian",
                    "mobile": "0400 777 888",
                    "email": "creation@example.com",
                    "relationship": "Parent",
                    "address": "10 Test Street",
                },
            )

            assert response.status_code == 302

        guardian = Guardian.query.filter_by(
            email="creation@example.com",
        ).first()

        assert guardian is not None
        assert guardian.name == "Creation Test Guardian"
        assert guardian.mobile == "0400 777 888"
        assert guardian.email == "creation@example.com"
        assert guardian.relationship == "Parent"
        assert guardian.address == "10 Test Street"
        assert guardian.is_active is True

        db.session.delete(guardian)
        db.session.commit()


def test_guardian_search_returns_matching_guardian():
    with app.app_context():
        matching_guardian = Guardian(
            name="Search Test Guardian",
            mobile="0400 333 444",
            email="searchtest@example.com",
            relationship="Parent",
        )

        other_guardian = Guardian(
            name="Different Guardian",
            mobile="0400 999 000",
            email="different@example.com",
            relationship="Parent",
        )

        db.session.add_all(
            [
                matching_guardian,
                other_guardian,
            ]
        )
        db.session.commit()

        with app.test_client() as client:
            response = client.get(
                "/guardians?q=Search+Test"
            )

            assert response.status_code == 200
            assert b"Search Test Guardian" in response.data
            assert b"Different Guardian" not in response.data

        db.session.delete(matching_guardian)
        db.session.delete(other_guardian)
        db.session.commit()