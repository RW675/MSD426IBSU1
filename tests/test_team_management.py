import pytest
from datetime import date

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


def test_team_list_displays_existing_team(client):
    with app.app_context():
        team = Team(
            name="Warrigal Park U13 Blue",
            season="2026",
            age_group="U13",
        )

        db.session.add(team)
        db.session.commit()

    response = client.get("/teams")

    assert response.status_code == 200
    assert b"Warrigal Park U13 Blue" in response.data
    assert b"2026" in response.data
    assert b"U13" in response.data
    assert b"View roster" in response.data
    assert b"Delete team" in response.data


def test_duplicate_team_is_rejected(client):
    with app.app_context():
        team = Team(
            name="Warrigal Park U13 Blue",
            season="2026",
            age_group="U13",
        )

        db.session.add(team)
        db.session.commit()

    response = client.post(
        "/teams/new",
        data={
            "team_name": "Warrigal Park U13 Blue",
            "season": "2026",
            "age_group": "U13",
        },
    )

    assert response.status_code == 400
    assert (
        b"A team with this name, season, and age group already exists."
        in response.data
    )

    with app.app_context():
        teams = Team.query.all()

        assert len(teams) == 1


def test_duplicate_team_is_case_insensitive(client):
    with app.app_context():
        team = Team(
            name="Warrigal Park U13 Blue",
            season="2026",
            age_group="U13",
        )

        db.session.add(team)
        db.session.commit()

    response = client.post(
        "/teams/new",
        data={
            "team_name": "warrigal park u13 blue",
            "season": "2026",
            "age_group": "u13",
        },
    )

    assert response.status_code == 400

    with app.app_context():
        teams = Team.query.all()

        assert len(teams) == 1


def test_empty_team_can_be_deleted(client):
    with app.app_context():
        team = Team(
            name="Empty Team",
            season="2026",
            age_group="U13",
        )

        db.session.add(team)
        db.session.commit()

        team_id = team.id

    response = client.post(
        f"/teams/{team_id}/delete"
    )

    assert response.status_code == 302

    with app.app_context():
        deleted_team = db.session.get(
            Team,
            team_id,
        )

        assert deleted_team is None


def test_team_with_assigned_player_cannot_be_deleted(client):
    with app.app_context():
        team = Team(
            name="Protected Team",
            season="2026",
            age_group="U13",
        )

        member = Member(
            name="Protected Player",
            date_of_birth=date(2013, 5, 10),
        )

        db.session.add_all([
            team,
            member,
        ])
        db.session.flush()

        registration = Registration(
            member_id=member.id,
            season="2026",
            age_group="U13",
            team_id=team.id,
        )

        db.session.add(registration)
        db.session.commit()

        team_id = team.id
        registration_id = registration.id

    response = client.post(
        f"/teams/{team_id}/delete"
    )

    assert response.status_code == 400
    assert (
        b"This team cannot be deleted while players are assigned."
        in response.data
    )

    with app.app_context():
        existing_team = db.session.get(
            Team,
            team_id,
        )

        existing_registration = db.session.get(
            Registration,
            registration_id,
        )

        assert existing_team is not None
        assert existing_registration is not None
        assert existing_registration.team_id == team_id


def test_delete_missing_team_returns_404(client):
    response = client.post(
        "/teams/999999/delete"
    )

    assert response.status_code == 404
    assert b"Team not found" in response.data