import pytest
from fastapi.testclient import TestClient


class TestCreateUser:

    def test_create_user_success(self, client: TestClient, sample_user_payload: dict):
        response = client.post("/api/v1/users/", json=sample_user_payload)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == sample_user_payload["username"]
        assert data["email"] == sample_user_payload["email"]
        assert data["first_name"] == sample_user_payload["first_name"]
        assert data["last_name"] == sample_user_payload["last_name"]
        assert data["role"] == sample_user_payload["role"]
        assert data["active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_user_duplicate_username(self, client: TestClient, sample_user_payload: dict):
        client.post("/api/v1/users/", json=sample_user_payload)
        payload = {**sample_user_payload, "email": "other@example.com"}
        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 409
        assert "username" in response.json()["detail"]

    def test_create_user_duplicate_email(self, client: TestClient, sample_user_payload: dict):
        client.post("/api/v1/users/", json=sample_user_payload)
        payload = {**sample_user_payload, "username": "other_user"}
        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 409
        assert "email" in response.json()["detail"]

    def test_create_user_invalid_email(self, client: TestClient, sample_user_payload: dict):
        payload = {**sample_user_payload, "email": "not-an-email"}
        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 422

    def test_create_user_username_too_short(self, client: TestClient, sample_user_payload: dict):
        payload = {**sample_user_payload, "username": "ab"}
        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 422

    def test_create_user_invalid_role(self, client: TestClient, sample_user_payload: dict):
        payload = {**sample_user_payload, "role": "superadmin"}
        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 422

    def test_create_user_default_role_is_user(self, client: TestClient, sample_user_payload: dict):
        payload = {k: v for k, v in sample_user_payload.items() if k != "role"}
        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 201
        assert response.json()["role"] == "user"

    @pytest.mark.parametrize("role", ["admin", "user", "guest"])
    def test_create_user_valid_roles(self, client: TestClient, sample_user_payload: dict, role: str):
        payload = {**sample_user_payload, "role": role, "username": f"user_{role}", "email": f"{role}@example.com"}
        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 201
        assert response.json()["role"] == role


class TestGetUser:

    def test_get_user_success(self, client: TestClient, created_user: dict):
        user_id = created_user["id"]
        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["id"] == user_id

    def test_get_user_not_found(self, client: TestClient):
        response = client.get("/api/v1/users/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404

    def test_get_user_invalid_uuid(self, client: TestClient):
        response = client.get("/api/v1/users/not-a-uuid")
        assert response.status_code == 422


class TestListUsers:

    def test_list_users_empty(self, client: TestClient):
        response = client.get("/api/v1/users/")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_users_returns_all(self, client: TestClient, sample_user_payload: dict):
        client.post("/api/v1/users/", json=sample_user_payload)
        second = {**sample_user_payload, "username": "jane_doe", "email": "jane@example.com"}
        client.post("/api/v1/users/", json=second)
        response = client.get("/api/v1/users/")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_list_users_pagination(self, client: TestClient, sample_user_payload: dict):
        for i in range(5):
            payload = {**sample_user_payload, "username": f"user_{i}", "email": f"user{i}@example.com"}
            client.post("/api/v1/users/", json=payload)
        response = client.get("/api/v1/users/?skip=0&limit=3")
        assert response.status_code == 200
        assert len(response.json()) == 3


class TestUpdateUser:

    def test_update_user_success(self, client: TestClient, created_user: dict):
        user_id = created_user["id"]
        response = client.put(f"/api/v1/users/{user_id}", json={"first_name": "Johnny", "role": "admin"})
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Johnny"
        assert data["role"] == "admin"
        assert data["username"] == created_user["username"]

    def test_update_user_not_found(self, client: TestClient):
        response = client.put("/api/v1/users/00000000-0000-0000-0000-000000000000", json={"first_name": "Ghost"})
        assert response.status_code == 404

    def test_update_user_duplicate_username(self, client: TestClient, sample_user_payload: dict):
        client.post("/api/v1/users/", json=sample_user_payload)
        second_payload = {**sample_user_payload, "username": "jane_doe", "email": "jane@example.com"}
        second = client.post("/api/v1/users/", json=second_payload).json()
        response = client.put(f"/api/v1/users/{second['id']}", json={"username": sample_user_payload["username"]})
        assert response.status_code == 409

    def test_update_user_duplicate_email(self, client: TestClient, sample_user_payload: dict):
        client.post("/api/v1/users/", json=sample_user_payload)
        second_payload = {**sample_user_payload, "username": "jane_doe", "email": "jane@example.com"}
        second = client.post("/api/v1/users/", json=second_payload).json()
        response = client.put(f"/api/v1/users/{second['id']}", json={"email": sample_user_payload["email"]})
        assert response.status_code == 409

    def test_update_user_partial(self, client: TestClient, created_user: dict):
        user_id = created_user["id"]
        response = client.put(f"/api/v1/users/{user_id}", json={"active": False})
        assert response.status_code == 200
        assert response.json()["active"] is False
        assert response.json()["username"] == created_user["username"]


class TestDeleteUser:

    def test_delete_user_success(self, client: TestClient, created_user: dict):
        user_id = created_user["id"]
        response = client.delete(f"/api/v1/users/{user_id}")
        assert response.status_code == 204

    def test_delete_user_not_found_after_deletion(self, client: TestClient, created_user: dict):
        user_id = created_user["id"]
        client.delete(f"/api/v1/users/{user_id}")
        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 404

    def test_delete_user_not_found(self, client: TestClient):
        response = client.delete("/api/v1/users/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404
