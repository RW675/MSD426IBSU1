import pytest

from app import app, db
from models import Guardian, Member, Registration


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.app_context():
        assert ":memory:" in str(db.engine.url), "Refusing to reset a non-test database"
        db.drop_all()
        db.create_all()

    with app.test_client() as test_client:
        yield test_client

    with app.app_context():
        db.session.remove()
        db.drop_all()


def _create_guardian(name="Test Guardian"):
    with app.app_context():
        guardian = Guardian(name=name, mobile="0400 000 000")
        db.session.add(guardian)
        db.session.commit()
        return guardian.id


def _post(client, member_name, dob, **extra):
    data = {
        "member_name": member_name,
        "date_of_birth": dob,
        "season": "2026",
        "age_group": "U13",
    }
    data.update(extra)
    return client.post("/registrations/new", data=data)


def test_junior_without_guardian_is_rejected(client):
    response = _post(client, "Junior No Guardian", "2014-09-03")
    assert response.status_code == 400
    assert b"guardian" in response.data.lower()


def test_junior_with_unknown_guardian_is_rejected(client):
    response = _post(
        client, "Junior Bad Guardian", "2014-09-03", guardian_id="999999"
    )
    assert response.status_code == 400
    assert b"does not exist" in response.data.lower()


def test_junior_with_existing_guardian_is_accepted(client):
    guardian_id = _create_guardian("Pat Existing")
    response = _post(
        client, "Junior With Guardian", "2014-09-03", guardian_id=str(guardian_id)
    )
    assert response.status_code == 302

    with app.app_context():
        member = Member.query.filter_by(name="Junior With Guardian").first()
        assert member is not None
        assert member.guardian_id == guardian_id
        assert Registration.query.filter_by(member_id=member.id).count() == 1


def test_adult_without_guardian_is_accepted(client):
    response = _post(client, "Adult Player", "1990-01-15")
    assert response.status_code == 302


def test_form_lists_existing_guardians(client):
    _create_guardian("Listed Guardian")
    response = client.get("/registrations/new")
    assert response.status_code == 200
    assert b"Listed Guardian" in response.data

def test_scenario_1_blocked_registration_saves_nothing(client):
    response = _post(client, "Blocked Junior", "2014-09-03")

    assert response.status_code == 400
    assert b"guardian" in response.data.lower()

    with app.app_context():
        assert Member.query.count() == 0
        assert Registration.query.count() == 0


def test_scenario_2_member_who_just_turned_18_needs_no_guardian(client):
    from datetime import date

    today = date.today()
    birthday = date(today.year - 18, today.month, min(today.day, 28))

    response = _post(client, "Just Turned Eighteen", birthday.isoformat())

    assert response.status_code == 302