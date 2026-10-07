import pytest
from datetime import date

from app import app, db
from models import Member


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.app_context():
        db.create_all()

        yield app.test_client()

        db.session.remove()
        db.drop_all()


def test_members_page_displays_members(client):
    with app.app_context():
        member_one = Member(
            name="Alice Player",
            date_of_birth=date(2012, 5, 10),
        )

        member_two = Member(
            name="Benjamin Player",
            date_of_birth=date(2011, 8, 15),
        )

        db.session.add_all([
            member_one,
            member_two,
        ])
        db.session.commit()

    response = client.get("/members")

    assert response.status_code == 200
    assert b"Alice Player" in response.data
    assert b"Benjamin Player" in response.data


def test_member_search_finds_matching_member(client):
    with app.app_context():
        member_one = Member(
            name="Alice Player",
            date_of_birth=date(2012, 5, 10),
        )

        member_two = Member(
            name="Benjamin Player",
            date_of_birth=date(2011, 8, 15),
        )

        db.session.add_all([
            member_one,
            member_two,
        ])
        db.session.commit()

    response = client.get("/members?search=Alice")

    assert response.status_code == 200
    assert b"Alice Player" in response.data
    assert b"Benjamin Player" not in response.data


def test_member_search_is_case_insensitive(client):
    with app.app_context():
        member = Member(
            name="Alice Player",
            date_of_birth=date(2012, 5, 10),
        )

        db.session.add(member)
        db.session.commit()

    response = client.get("/members?search=alice")

    assert response.status_code == 200
    assert b"Alice Player" in response.data


def test_member_search_supports_partial_name(client):
    with app.app_context():
        member = Member(
            name="Benjamin Player",
            date_of_birth=date(2011, 8, 15),
        )

        db.session.add(member)
        db.session.commit()

    response = client.get("/members?search=Ben")

    assert response.status_code == 200
    assert b"Benjamin Player" in response.data


def test_member_search_shows_no_results_message(client):
    with app.app_context():
        member = Member(
            name="Alice Player",
            date_of_birth=date(2012, 5, 10),
        )

        db.session.add(member)
        db.session.commit()

    response = client.get("/members?search=Nobody")

    assert response.status_code == 200
    assert b"No members found." in response.data
    assert b"Alice Player" not in response.data