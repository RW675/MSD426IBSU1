import pytest
from datetime import datetime

from app import app, db
from models import Member, Registration, Team


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()

        yield app.test_client()

        db.session.remove()
        db.drop_all()


def test_create_registration_success(client):
    response = client.post(
        "/registrations/new",
        data={
            "member_name": "Mia Kelleher",
            "date_of_birth": "2014-09-03",
            "season": "2026",
            "age_group": "U13",
        },
    )

    assert response.status_code == 302

    with app.app_context():
        member = Member.query.filter_by(name="Mia Kelleher").first()
        assert member is not None

        registration = Registration.query.filter_by(
            member_id=member.id
        ).first()

        assert registration is not None
        assert registration.season == "2026"
        assert registration.age_group == "U13"


def test_create_registration_rejects_missing_date(client):
    response = client.post(
        "/registrations/new",
        data={
            "member_name": "Mia Kelleher",
            "season": "2026",
            "age_group": "U13",
        },
    )

    assert response.status_code == 400
    assert b"Please provide a valid" in response.data

    with app.app_context():
        assert Member.query.count() == 0


def test_client_uses_isolated_database(client):
    with app.app_context():
        assert str(db.engine.url) == "sqlite:///:memory:"


def test_registration_history_requires_selected_member(client):
    response = client.get("/registrations/history")

    assert response.status_code == 200
    assert b"Select Member" in response.data


def test_registration_history_displays_selected_member_records(client):
    with app.app_context():
        member = Member(
            name="History Player",
            date_of_birth=datetime.strptime(
                "2014-09-03",
                "%Y-%m-%d",
            ).date(),
        )

        db.session.add(member)
        db.session.flush()

        registration = Registration(
            member_id=member.id,
            season="2026",
            age_group="U13",
        )

        db.session.add(registration)
        db.session.commit()

        member_id = member.id

    response = client.get(
        f"/registrations/history?member_id={member_id}"
    )

    assert response.status_code == 200
    assert b"History Player" in response.data
    assert b"2026" in response.data
    assert b"U13" in response.data
    assert b"started" in response.data


def test_registration_history_does_not_show_another_members_records(client):
    with app.app_context():
        member_one = Member(
            name="Player One",
            date_of_birth=datetime.strptime(
                "2014-01-01",
                "%Y-%m-%d",
            ).date(),
        )

        member_two = Member(
            name="Player Two",
            date_of_birth=datetime.strptime(
                "2013-01-01",
                "%Y-%m-%d",
            ).date(),
        )

        db.session.add_all([member_one, member_two])
        db.session.flush()

        db.session.add(
            Registration(
                member_id=member_one.id,
                season="2026",
                age_group="U13",
            )
        )

        db.session.add(
            Registration(
                member_id=member_two.id,
                season="2025",
                age_group="U14",
            )
        )

        db.session.commit()

        member_one_id = member_one.id

    response = client.get(
        f"/registrations/history?member_id={member_one_id}"
    )

    assert response.status_code == 200
    assert b"Player One" in response.data
    assert b"2026" in response.data
    assert b"U13" in response.data
    assert b"Player Two" not in response.data
    assert b"2025" not in response.data


def test_create_team_success(client):
    response = client.post(
        "/teams/new",
        data={
            "team_name": "Warrigal Park U13 Blue",
            "season": "2026",
            "age_group": "U13",
        },
    )

    assert response.status_code == 302

    with app.app_context():
        team = Team.query.filter_by(
            name="Warrigal Park U13 Blue"
        ).first()

        assert team is not None
        assert team.season == "2026"
        assert team.age_group == "U13"


def test_create_team_rejects_missing_team_name(client):
    response = client.post(
        "/teams/new",
        data={
            "team_name": "",
            "season": "2026",
            "age_group": "U13",
        },
    )

    assert response.status_code == 400
    assert (
        b"Team name, season, and age group are required."
        in response.data
    )

    with app.app_context():
        assert Team.query.count() == 0


def test_create_team_rejects_missing_season(client):
    response = client.post(
        "/teams/new",
        data={
            "team_name": "Warrigal Park U13 Blue",
            "season": "",
            "age_group": "U13",
        },
    )

    assert response.status_code == 400

    with app.app_context():
        assert Team.query.count() == 0


def test_create_team_rejects_missing_age_group(client):
    response = client.post(
        "/teams/new",
        data={
            "team_name": "Warrigal Park U13 Blue",
            "season": "2026",
            "age_group": "",
        },
    )

    assert response.status_code == 400

    with app.app_context():
        assert Team.query.count() == 0


def test_add_registered_player_to_team_success(client):
    with app.app_context():
        member = Member(
            name="Team Player",
            date_of_birth=datetime.strptime(
                "2013-05-10",
                "%Y-%m-%d",
            ).date(),
        )

        db.session.add(member)
        db.session.flush()

        registration = Registration(
            member_id=member.id,
            season="2026",
            age_group="U13",
        )

        team = Team(
            name="Warrigal Park U13 Blue",
            season="2026",
            age_group="U13",
        )

        db.session.add_all([registration, team])
        db.session.commit()

        registration_id = registration.id
        team_id = team.id

    response = client.post(
        f"/teams/{team_id}/players/add",
        data={
            "registration_id": registration_id,
        },
    )

    assert response.status_code == 302

    with app.app_context():
        registration = db.session.get(
            Registration,
            registration_id,
        )

        assert registration is not None
        assert registration.team_id == team_id


def test_add_player_rejects_wrong_season(client):
    with app.app_context():
        member = Member(
            name="Wrong Season Player",
            date_of_birth=datetime.strptime(
                "2013-05-10",
                "%Y-%m-%d",
            ).date(),
        )

        db.session.add(member)
        db.session.flush()

        registration = Registration(
            member_id=member.id,
            season="2025",
            age_group="U13",
        )

        team = Team(
            name="Warrigal Park U13 Blue",
            season="2026",
            age_group="U13",
        )

        db.session.add_all([registration, team])
        db.session.commit()

        registration_id = registration.id
        team_id = team.id

    response = client.post(
        f"/teams/{team_id}/players/add",
        data={
            "registration_id": registration_id,
        },
    )

    assert response.status_code == 400
    assert b"season does not match" in response.data

    with app.app_context():
        registration = db.session.get(
            Registration,
            registration_id,
        )

        assert registration.team_id is None


def test_add_player_rejects_wrong_age_group(client):
    with app.app_context():
        member = Member(
            name="Wrong Age Player",
            date_of_birth=datetime.strptime(
                "2013-05-10",
                "%Y-%m-%d",
            ).date(),
        )

        db.session.add(member)
        db.session.flush()

        registration = Registration(
            member_id=member.id,
            season="2026",
            age_group="U14",
        )

        team = Team(
            name="Warrigal Park U13 Blue",
            season="2026",
            age_group="U13",
        )

        db.session.add_all([registration, team])
        db.session.commit()

        registration_id = registration.id
        team_id = team.id

    response = client.post(
        f"/teams/{team_id}/players/add",
        data={
            "registration_id": registration_id,
        },
    )

    assert response.status_code == 400
    assert b"age group does not match" in response.data

    with app.app_context():
        registration = db.session.get(
            Registration,
            registration_id,
        )

        assert registration.team_id is None


def test_add_player_rejects_already_assigned_player(client):
    with app.app_context():
        member = Member(
            name="Assigned Player",
            date_of_birth=datetime.strptime(
                "2013-05-10",
                "%Y-%m-%d",
            ).date(),
        )

        db.session.add(member)
        db.session.flush()

        first_team = Team(
            name="Warrigal Park U13 Blue",
            season="2026",
            age_group="U13",
        )

        second_team = Team(
            name="Warrigal Park U13 Red",
            season="2026",
            age_group="U13",
        )

        registration = Registration(
            member_id=member.id,
            season="2026",
            age_group="U13",
            team=first_team,
        )

        db.session.add_all([
            first_team,
            second_team,
            registration,
        ])
        db.session.commit()

        registration_id = registration.id
        second_team_id = second_team.id

    response = client.post(
        f"/teams/{second_team_id}/players/add",
        data={
            "registration_id": registration_id,
        },
    )

    assert response.status_code == 400
    assert b"already assigned to a team" in response.data

    with app.app_context():
        registration = db.session.get(
            Registration,
            registration_id,
        )

        assert registration.team_id is not None
        assert registration.team_id != second_team_id

