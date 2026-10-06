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


def create_team(name, season="2026", age_group="U13"):
    team = Team(name=name, season=season, age_group=age_group)
    db.session.add(team)
    db.session.flush()
    return team


def create_registration(
    name,
    team=None,
    season="2026",
    age_group="U13",
):
    member = Member(
        name=name,
        date_of_birth=datetime.strptime("2013-05-10", "%Y-%m-%d").date(),
    )
    db.session.add(member)
    db.session.flush()

    registration = Registration(
        member_id=member.id,
        season=season,
        age_group=age_group,
        team_id=team.id if team else None,
    )
    db.session.add(registration)
    db.session.flush()
    return registration


def test_move_player_to_another_team_success(client):
    with app.app_context():
        blue = create_team("Warrigal Park U13 Blue")
        red = create_team("Warrigal Park U13 Red")
        registration = create_registration("Move Player", team=blue)
        db.session.commit()

        blue_id = blue.id
        red_id = red.id
        registration_id = registration.id

    response = client.post(
        f"/teams/{blue_id}/players/{registration_id}/move",
        data={"target_team_id": red_id},
    )

    assert response.status_code == 302

    with app.app_context():
        registration = db.session.get(Registration, registration_id)
        assert registration.team_id == red_id


def test_move_player_rejects_team_with_different_age_group(client):
    with app.app_context():
        blue = create_team("Warrigal Park U13 Blue", age_group="U13")
        other = create_team("Warrigal Park U14 Blue", age_group="U14")
        registration = create_registration("Move Player", team=blue)
        db.session.commit()

        blue_id = blue.id
        other_id = other.id
        registration_id = registration.id

    response = client.post(
        f"/teams/{blue_id}/players/{registration_id}/move",
        data={"target_team_id": other_id},
    )

    assert response.status_code == 400
    assert b"must match the season and age group" in response.data

    with app.app_context():
        registration = db.session.get(Registration, registration_id)
        assert registration.team_id == blue_id


def test_move_player_rejects_missing_destination_team(client):
    with app.app_context():
        blue = create_team("Warrigal Park U13 Blue")
        registration = create_registration("Move Player", team=blue)
        db.session.commit()

        blue_id = blue.id
        registration_id = registration.id

    response = client.post(
        f"/teams/{blue_id}/players/{registration_id}/move",
        data={},
    )

    assert response.status_code == 400
    assert b"valid destination team" in response.data

    with app.app_context():
        registration = db.session.get(Registration, registration_id)
        assert registration.team_id == blue_id


def test_move_player_returns_404_when_player_not_on_team(client):
    with app.app_context():
        blue = create_team("Warrigal Park U13 Blue")
        red = create_team("Warrigal Park U13 Red")
        registration = create_registration("Red Player", team=red)
        db.session.commit()

        blue_id = blue.id
        registration_id = registration.id

    response = client.post(
        f"/teams/{blue_id}/players/{registration_id}/move",
        data={"target_team_id": blue_id},
    )

    assert response.status_code == 404


def test_move_page_loads_for_player_on_team(client):
    with app.app_context():
        blue = create_team("Warrigal Park U13 Blue")
        create_team("Warrigal Park U13 Red")
        registration = create_registration("Move Player", team=blue)
        db.session.commit()

        blue_id = blue.id
        registration_id = registration.id

    response = client.get(
        f"/teams/{blue_id}/players/{registration_id}/move"
    )

    assert response.status_code == 200
    assert b"Warrigal Park U13 Red" in response.data


def test_remove_player_from_team_success(client):
    with app.app_context():
        blue = create_team("Warrigal Park U13 Blue")
        registration = create_registration("Remove Player", team=blue)
        db.session.commit()

        blue_id = blue.id
        registration_id = registration.id

    response = client.post(
        f"/teams/{blue_id}/players/{registration_id}/remove"
    )

    assert response.status_code == 302

    with app.app_context():
        registration = db.session.get(Registration, registration_id)
        assert registration is not None
        assert registration.team_id is None


def test_remove_player_returns_404_when_player_not_on_team(client):
    with app.app_context():
        blue = create_team("Warrigal Park U13 Blue")
        red = create_team("Warrigal Park U13 Red")
        registration = create_registration("Red Player", team=red)
        db.session.commit()

        blue_id = blue.id
        red_id = red.id
        registration_id = registration.id

    response = client.post(
        f"/teams/{blue_id}/players/{registration_id}/remove"
    )

    assert response.status_code == 404

    with app.app_context():
        registration = db.session.get(Registration, registration_id)
        assert registration.team_id == red_id


def test_remove_player_returns_404_when_team_not_found(client):
    response = client.post("/teams/999/players/1/remove")

    assert response.status_code == 404


def test_manage_team_page_lists_only_players_on_that_team(client):
    with app.app_context():
        blue = create_team("Warrigal Park U13 Blue")
        create_registration("Roster Player", team=blue)
        create_registration("Unassigned Player")
        db.session.commit()

        blue_id = blue.id

    response = client.get(f"/teams/{blue_id}/manage")

    assert response.status_code == 200
    assert b"Roster Player" in response.data
    assert b"Unassigned Player" not in response.data