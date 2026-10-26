from fastapi.testclient import TestClient


def test_health_check_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_list_tasks(client: TestClient) -> None:
    create_response = client.post("/api/tasks", json={"title": "Plan the week"})

    assert create_response.status_code == 201
    created_task = create_response.json()
    assert created_task["title"] == "Plan the week"
    assert created_task["completed"] is False

    list_response = client.get("/api/tasks")

    assert list_response.status_code == 200
    assert list_response.json() == [created_task]


def test_create_task_trims_title(client: TestClient) -> None:
    response = client.post("/api/tasks", json={"title": "  Read a book  "})

    assert response.status_code == 201
    assert response.json()["title"] == "Read a book"


def test_create_task_rejects_blank_title(client: TestClient) -> None:
    response = client.post("/api/tasks", json={"title": "   "})

    assert response.status_code == 422


def test_task_can_be_completed_and_reopened(client: TestClient) -> None:
    created_task = client.post(
        "/api/tasks",
        json={"title": "Practice testing"},
    ).json()

    completed_response = client.patch(
        f"/api/tasks/{created_task['id']}",
        json={"completed": True},
    )
    reopened_response = client.patch(
        f"/api/tasks/{created_task['id']}",
        json={"completed": False},
    )

    assert completed_response.status_code == 200
    assert completed_response.json()["completed"] is True
    assert reopened_response.status_code == 200
    assert reopened_response.json()["completed"] is False


def test_delete_task_removes_it(client: TestClient) -> None:
    created_task = client.post(
        "/api/tasks",
        json={"title": "Remove this task"},
    ).json()

    delete_response = client.delete(f"/api/tasks/{created_task['id']}")

    assert delete_response.status_code == 204
    assert client.get("/api/tasks").json() == []


def test_unknown_task_returns_not_found(client: TestClient) -> None:
    update_response = client.patch(
        "/api/tasks/999",
        json={"completed": True},
    )
    delete_response = client.delete("/api/tasks/999")

    assert update_response.status_code == 404
    assert delete_response.status_code == 404
