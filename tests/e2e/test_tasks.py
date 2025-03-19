import json


def test_assign_tasks(
    fastapi_client, create_and_validate_dummy_user, create_mock_task, admin_headers
):

    response = fastapi_client.patch(url="/api/tasks/assign", headers=admin_headers)
    assert response.json().get("message") == "Tasks distributed successfully"
    assert response.status_code == 200


def test_reject_assigned_task(
    fastapi_client,
    create_mock_task,
    admin_headers,
    user_headers,
):

    fastapi_client.patch(url="/api/tasks/assign", headers=admin_headers)
    response = fastapi_client.patch(
        url=f"/api/tasks/{create_mock_task}/reject",
        headers=user_headers,
    )
    assert response.json().get("message") == "Task rejected successfully"
    assert response.status_code == 200


def test_complete_assigned_task(
    fastapi_client,
    create_mock_task,
    admin_headers,
    user_headers,
):

    fastapi_client.patch(url="/api/tasks/assign", headers=admin_headers)
    response = fastapi_client.patch(
        url=f"/api/tasks/{create_mock_task}/complete",
        headers=user_headers,
    )
    assert response.json().get("message") == "Task completed successfully"
    assert response.status_code == 200


def test_create_task_yaml(
    fastapi_client,
    admin_headers,
):
    yaml_payload = """title: testing\ndescription: testing\ndue_date: 2025-12-12
    """
    admin_headers.update({"content-type": "application/x-yaml"})
    response = fastapi_client.post(
        url="/api/tasks",
        data=yaml_payload,
        headers=admin_headers,
    )
    assert response.json().get("message") == "Task created"
    assert response.status_code == 201


def test_create_task_json(
    fastapi_client,
    admin_headers,
):
    json_payload = {
        "title": "testing",
        "description": "testing",
        "due_date": "2025-12-12",
    }
    admin_headers.update({"content-type": "application/json"})
    response = fastapi_client.post(
        url="/api/tasks",
        data=json.dumps(json_payload),
        headers=admin_headers,
    )
    assert response.json().get("message") == "Task created"
    assert response.status_code == 201


def test_delete_task(fastapi_client, admin_headers, create_mock_task):
    response = fastapi_client.delete(
        url=f"/api/tasks/{create_mock_task}", headers=admin_headers
    )
    assert response.status_code == 204


def test_delete_assigned_task(
    fastapi_client,
    admin_headers,
    create_and_validate_dummy_user,
    create_mock_task,
):
    fastapi_client.patch(url="/api/tasks/assign", headers=admin_headers)
    response = fastapi_client.delete(
        url=f"/api/tasks/{create_mock_task}", headers=admin_headers
    )
    assert response.status_code == 403


def test_retrieve_my_assigned_tasks(
    fastapi_client,
    admin_headers,
    create_mock_task,
    user_headers,
):
    fastapi_client.patch(url="/api/tasks/assign", headers=admin_headers)
    response = fastapi_client.get(url="/api/tasks/assigned", headers=user_headers)
    assert response.json().get("message").startswith("Retrieved tasks for user")
    assert response.json().get("tasks", [{}])[0].get("title") == "Test task"
    assert response.status_code == 200


def test_get_single_task(fastapi_client, admin_headers, create_mock_task):
    response = fastapi_client.get(
        url=f"/api/tasks/{create_mock_task}", headers=admin_headers
    )
    assert response.json().get("task").get("id") == create_mock_task
    assert response.status_code == 200
