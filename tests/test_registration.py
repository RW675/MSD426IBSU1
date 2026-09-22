import pytest
from app import app, db
from models import Member, Registration

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_create_registration_success(client):
    response = client.post("/registrations/new", data={
        "member_name": "Mia Kelleher",
        "date_of_birth": "2014-09-03",
        "season": "2026",
        "age_group": "U13",
    })

    assert response.status_code == 302

    with app.app_context():
        member = Member.query.filter_by(name="Mia Kelleher").first()
        assert member is not None

        registration = Registration.query.filter_by(member_id=member.id).first()
        assert registration is not None
        assert registration.season == "2026"
        assert registration.age_group == "U13"