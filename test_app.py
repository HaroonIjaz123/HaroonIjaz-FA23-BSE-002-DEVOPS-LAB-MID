import pytest
from app import create_app, load_submissions
VALID = {
    "name": "Haroon Ijaz",
    "reg_no": "FA23-BSE-002",
    "title": "Lab Assignment 2",
    "url": "https://github.com/haroon/lab2",
}

@pytest.fixture
def setup(tmp_path):
    data_file = str(tmp_path / "submissions.json")
    app = create_app(data_file)
    app.config["TESTING"] = True
    return app.test_client(), data_file

def test_valid_submission_is_saved(setup):
    client, data_file = setup
    response = client.post("/", data=VALID, follow_redirects=True)
    assert response.status_code == 200
    assert b"FA23-BSE-002" in response.data          # appears in the list
    assert len(load_submissions(data_file)) == 1     # and is stored

def test_missing_registration_number_is_rejected(setup):
    client, data_file = setup
    data = dict(VALID, reg_no="")
    response = client.post("/", data=data)
    assert response.status_code == 400
    assert b"Registration number is required" in response.data
    assert load_submissions(data_file) == []


def test_invalid_url_is_rejected_and_not_saved(setup):
    client, data_file = setup
    data = dict(VALID, url="not-a-valid-url")
    response = client.post("/", data=data)
    assert response.status_code == 400
    assert b"not a valid" in response.data
    assert load_submissions(data_file) == []
