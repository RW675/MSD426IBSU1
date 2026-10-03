from app import app


def _post_registration(**overrides):
    data = {
        "member_name": "Test Junior New",
        "date_of_birth": "2014-09-03",
        "season": "2026",
        "age_group": "U13",
    }
    data.update(overrides)
    with app.test_client() as client:
        return client.post("/registrations/new", data=data)


def test_new_junior_without_guardian_is_rejected():
    response = _post_registration()
    assert response.status_code == 400
    assert b"guardian" in response.data.lower()


def test_new_junior_with_incomplete_guardian_is_rejected():
    response = _post_registration(guardian_name="Pat Example")
    assert response.status_code == 400
    assert b"guardian" in response.data.lower()