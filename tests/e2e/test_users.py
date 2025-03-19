import json


def test_create_user(fastapi_client):
    payload = {"username": "testin_user", "password": "Dummy_password"}
    response = fastapi_client.post(url="/api/users/register", data=json.dumps(payload))

    assert response.json().get("message") == "New user created successfully"
    assert response.status_code == 201


def test_validate_user(fastapi_client, create_invalid_user, admin_headers):

    response = fastapi_client.patch(
        url=f"/api/users/{create_invalid_user}/validate", headers=admin_headers
    )

    assert response.json().get("message") == "User has been validated"
    assert response.status_code == 200


def test_get_users(fastapi_client, admin_headers, create_and_validate_dummy_user):
    response = fastapi_client.get(url="/api/users", headers=admin_headers)
    assert response.json().get("message") == "Users retrieved"
    assert len(response.json().get("users")) == 1
    assert response.status_code == 200
