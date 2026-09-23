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

        team = Team(name="U13G NAVY", season="2026", age_group="U13")
        db.session.add_all([guardian, member, registration, team])
        db.session.flush()

        registration.team_id = team.id
        db.session.commit()

        roster = team.roster_details()
        assert len(roster) == 1
        assert roster[0]["member_name"] == "Ruby Antonopoulos"
        assert roster[0]["guardian_mobile"] == "0438 771 226"
