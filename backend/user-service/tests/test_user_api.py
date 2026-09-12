def test_sync_user_creates_profile_from_authenticated_identity(client):
    """id and role come from the auth headers, not the request body —
    the body only supplies email and name."""
    response = client.post(
        "/api/v1/users",
        headers={"X-User-Id": "cog-usr-001", "X-User-Role": "Customer"},
        json={"email": "customer1@example.com", "name": "Nirasha Customer"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == "cog-usr-001"
    assert body["role"] == "Customer"
    assert body["email"] == "customer1@example.com"
    assert body["status"] == "ACTIVE"


def test_sync_user_without_auth_returns_401(client):
    response = client.post(
        "/api/v1/users",
        json={"email": "test@example.com", "name": "Test"},
    )

    assert response.status_code == 401


def test_sync_user_is_idempotent_and_updates_existing_profile(client):
    """Calling sync twice for the same identity should update, not
    create a duplicate or error."""
    headers = {"X-User-Id": "cog-usr-001", "X-User-Role": "Customer"}

    client.post("/api/v1/users", headers=headers, json={"email": "old@example.com", "name": "Old Name"})
    response = client.post("/api/v1/users", headers=headers, json={"email": "new@example.com", "name": "New Name"})

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == "cog-usr-001"
    assert body["email"] == "new@example.com"
    assert body["name"] == "New Name"


def test_sync_user_cannot_self_assign_role_via_body(client):
    """UserSyncRequest has no role field at all, so even attempting to
    pass one in the body is ignored — role always comes from the
    X-User-Role header (the Cognito group claim, in the real system)."""
    response = client.post(
        "/api/v1/users",
        headers={"X-User-Id": "cog-usr-002", "X-User-Role": "Supplier"},
        json={"email": "supplier1@example.com", "name": "Sahan Supplier", "role": "DataSteward"},
    )

    assert response.status_code == 201
    assert response.json()["role"] == "Supplier"  # header role wins, body's "role" is ignored


def test_user_can_view_own_profile(client):
    headers = {"X-User-Id": "cog-usr-001", "X-User-Role": "Customer"}
    client.post("/api/v1/users", headers=headers, json={"email": "customer1@example.com", "name": "Nirasha"})

    response = client.get("/api/v1/users/cog-usr-001", headers=headers)

    assert response.status_code == 200
    assert response.json()["id"] == "cog-usr-001"


def test_user_cannot_view_another_users_profile(client):
    client.post(
        "/api/v1/users",
        headers={"X-User-Id": "cog-usr-001", "X-User-Role": "Customer"},
        json={"email": "customer1@example.com", "name": "Nirasha"},
    )

    response = client.get(
        "/api/v1/users/cog-usr-001",
        headers={"X-User-Id": "cog-usr-999", "X-User-Role": "Customer"},
    )

    assert response.status_code == 403


def test_data_steward_can_view_any_profile(client):
    client.post(
        "/api/v1/users",
        headers={"X-User-Id": "cog-usr-001", "X-User-Role": "Customer"},
        json={"email": "customer1@example.com", "name": "Nirasha"},
    )

    response = client.get(
        "/api/v1/users/cog-usr-001",
        headers={"X-User-Id": "steward-1", "X-User-Role": "DataSteward"},
    )

    assert response.status_code == 200


def test_get_nonexistent_user_returns_404(client):
    response = client.get(
        "/api/v1/users/does-not-exist",
        headers={"X-User-Id": "does-not-exist", "X-User-Role": "Customer"},
    )

    assert response.status_code == 404


def test_list_users_requires_data_steward_role(client):
    response = client.get(
        "/api/v1/users",
        headers={"X-User-Id": "cog-usr-001", "X-User-Role": "Customer"},
    )

    assert response.status_code == 403


def test_data_steward_can_list_users(client):
    client.post(
        "/api/v1/users",
        headers={"X-User-Id": "cog-usr-001", "X-User-Role": "Customer"},
        json={"email": "customer1@example.com", "name": "Nirasha"},
    )
    client.post(
        "/api/v1/users",
        headers={"X-User-Id": "cog-usr-002", "X-User-Role": "Supplier"},
        json={"email": "supplier1@example.com", "name": "Sahan"},
    )

    response = client.get(
        "/api/v1/users",
        headers={"X-User-Id": "steward-1", "X-User-Role": "DataSteward"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_user_can_update_own_name(client):
    headers = {"X-User-Id": "cog-usr-001", "X-User-Role": "Customer"}
    client.post("/api/v1/users", headers=headers, json={"email": "customer1@example.com", "name": "Old Name"})

    response = client.patch(
        "/api/v1/users/cog-usr-001",
        headers=headers,
        json={"name": "New Name"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


def test_user_cannot_update_another_users_profile(client):
    client.post(
        "/api/v1/users",
        headers={"X-User-Id": "cog-usr-001", "X-User-Role": "Customer"},
        json={"email": "customer1@example.com", "name": "Nirasha"},
    )

    response = client.patch(
        "/api/v1/users/cog-usr-001",
        headers={"X-User-Id": "cog-usr-999", "X-User-Role": "Customer"},
        json={"name": "Hacked Name"},
    )

    assert response.status_code == 403


def test_update_request_cannot_change_role_or_status(client):
    """UserUpdateRequest has no role/status fields — confirms a user
    can't escalate their own privileges via this endpoint."""
    headers = {"X-User-Id": "cog-usr-001", "X-User-Role": "Customer"}
    client.post("/api/v1/users", headers=headers, json={"email": "customer1@example.com", "name": "Nirasha"})

    response = client.patch(
        "/api/v1/users/cog-usr-001",
        headers=headers,
        json={"name": "Nirasha", "role": "DataSteward", "status": "INACTIVE"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["role"] == "Customer"   # unchanged, extra fields silently ignored
    assert body["status"] == "ACTIVE"   # unchanged


def test_user_can_deactivate_own_account(client):
    headers = {"X-User-Id": "cog-usr-001", "X-User-Role": "Customer"}
    client.post("/api/v1/users", headers=headers, json={"email": "customer1@example.com", "name": "Nirasha"})

    response = client.patch("/api/v1/users/cog-usr-001/deactivate", headers=headers)

    assert response.status_code == 200


def test_deactivated_user_no_longer_appears_in_steward_list(client):
    headers = {"X-User-Id": "cog-usr-001", "X-User-Role": "Customer"}
    client.post("/api/v1/users", headers=headers, json={"email": "customer1@example.com", "name": "Nirasha"})
    client.patch("/api/v1/users/cog-usr-001/deactivate", headers=headers)

    response = client.get(
        "/api/v1/users",
        headers={"X-User-Id": "steward-1", "X-User-Role": "DataSteward"},
    )

    assert response.status_code == 200
    user_ids = [u["id"] for u in response.json()]
    assert "cog-usr-001" not in user_ids


def test_user_cannot_deactivate_another_users_account(client):
    client.post(
        "/api/v1/users",
        headers={"X-User-Id": "cog-usr-001", "X-User-Role": "Customer"},
        json={"email": "customer1@example.com", "name": "Nirasha"},
    )

    response = client.patch(
        "/api/v1/users/cog-usr-001/deactivate",
        headers={"X-User-Id": "cog-usr-999", "X-User-Role": "Customer"},
    )

    assert response.status_code == 403


def test_data_steward_can_deactivate_any_account(client):
    client.post(
        "/api/v1/users",
        headers={"X-User-Id": "cog-usr-001", "X-User-Role": "Customer"},
        json={"email": "customer1@example.com", "name": "Nirasha"},
    )

    response = client.patch(
        "/api/v1/users/cog-usr-001/deactivate",
        headers={"X-User-Id": "steward-1", "X-User-Role": "DataSteward"},
    )

    assert response.status_code == 200