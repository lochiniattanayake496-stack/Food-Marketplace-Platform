def test_list_products_when_empty_returns_empty_list(client):
    """With a freshly reset database, no products exist yet."""
    response = client.get("/api/v1/products")

    assert response.status_code == 200
    assert response.json() == []


def test_submit_product_as_supplier_returns_201(client):
    """A Supplier submitting a valid product should succeed and
    default to PENDING status (not yet visible to customers)."""
    response = client.post(
        "/api/v1/products",
        headers={"X-User-Id": "supplier-1", "X-User-Role": "Supplier"},
        json={
            "name": "Chicken Breast",
            "description": "Fresh",
            "price": 5.99,
            "category": "Meats",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Chicken Breast"
    assert body["status"] == "PENDING"
    assert body["supplierId"] == "supplier-1"


def test_submit_product_without_user_id_header_returns_401(client):
    """Missing auth headers entirely should be rejected with 401,
    not FastAPI's generic 422."""
    response = client.post(
        "/api/v1/products",
        headers={"X-User-Role": "Supplier"},  # missing X-User-Id
        json={"name": "Test", "price": 1, "category": "Meats"},
    )

    assert response.status_code == 401


def test_submit_product_with_unrecognized_role_returns_400(client):
    """A role value that isn't Customer/Supplier/DataSteward should
    be rejected as a bad request, not silently accepted."""
    response = client.post(
        "/api/v1/products",
        headers={"X-User-Id": "supplier-1", "X-User-Role": "Astronaut"},
        json={"name": "Test", "price": 1, "category": "Meats"},
    )

    assert response.status_code == 400


def test_get_product_by_id_that_does_not_exist_returns_404(client):
    response = client.get("/api/v1/products/does-not-exist")

    assert response.status_code == 404


def _create_product(client, supplier_id="supplier-1"):
    """Small helper, not a test itself — pytest ignores functions that
    don't start with test_. Saves repeating this setup in every test
    below that needs an existing product to work with."""
    response = client.post(
        "/api/v1/products",
        headers={"X-User-Id": supplier_id, "X-User-Role": "Supplier"},
        json={"name": "Chicken Breast", "price": 5.99, "category": "Meats"},
    )
    return response.json()["id"]


def test_supplier_cannot_edit_another_suppliers_product(client):
    product_id = _create_product(client, supplier_id="supplier-1")

    response = client.patch(
        f"/api/v1/products/{product_id}",
        headers={"X-User-Id": "supplier-2", "X-User-Role": "Supplier"},
        json={"price": 9.99},
    )

    assert response.status_code == 403


def test_supplier_can_edit_own_product(client):
    product_id = _create_product(client, supplier_id="supplier-1")

    response = client.patch(
        f"/api/v1/products/{product_id}",
        headers={"X-User-Id": "supplier-1", "X-User-Role": "Supplier"},
        json={"price": 9.99},
    )

    assert response.status_code == 200
    assert response.json()["price"] == 9.99


def test_supplier_cannot_review_a_submission(client):
    """Only a Data Steward should be able to approve/reject —
    a supplier attempting this on their own product should be blocked."""
    product_id = _create_product(client, supplier_id="supplier-1")

    response = client.patch(
        f"/api/v1/products/{product_id}/review",
        headers={"X-User-Id": "supplier-1", "X-User-Role": "Supplier"},
        json={"status": "APPROVED"},
    )

    assert response.status_code == 403


def test_data_steward_can_approve_a_submission(client):
    product_id = _create_product(client)

    response = client.patch(
        f"/api/v1/products/{product_id}/review",
        headers={"X-User-Id": "steward-1", "X-User-Role": "DataSteward"},
        json={"status": "APPROVED"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "APPROVED"


def test_approved_product_becomes_visible_in_public_list(client):
    product_id = _create_product(client)
    client.patch(
        f"/api/v1/products/{product_id}/review",
        headers={"X-User-Id": "steward-1", "X-User-Role": "DataSteward"},
        json={"status": "APPROVED"},
    )

    response = client.get("/api/v1/products")

    product_ids_in_list = [p["id"] for p in response.json()]
    assert product_id in product_ids_in_list


def test_pending_product_is_not_visible_in_public_list(client):
    """A product that hasn't been reviewed yet should stay hidden —
    this is the core 'Product visibility' business rule from the guide."""
    _create_product(client)

    response = client.get("/api/v1/products")

    assert response.json() == []


def test_data_steward_can_reject_with_reason(client):
    product_id = _create_product(client)

    response = client.patch(
        f"/api/v1/products/{product_id}/review",
        headers={"X-User-Id": "steward-1", "X-User-Role": "DataSteward"},
        json={"status": "REJECTED", "rejectionReason": "Missing compliance info"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "REJECTED"
    assert body["rejectionReason"] == "Missing compliance info"


def test_supplier_can_deactivate_own_product(client):
    product_id = _create_product(client, supplier_id="supplier-1")

    response = client.patch(
        f"/api/v1/products/{product_id}/deactivate",
        headers={"X-User-Id": "supplier-1", "X-User-Role": "Supplier"},
    )

    assert response.status_code == 200

def test_anonymous_user_cannot_filter_by_pending_status(client):
    _create_product(client)  # creates a PENDING product

    response = client.get("/api/v1/products?status=PENDING")

    assert response.status_code == 403

def test_owning_supplier_can_view_own_pending_product_by_id(client):
    """A PENDING product isn't publicly visible yet, but the supplier
    who submitted it must still be able to fetch it directly (e.g. to
    check its status or prepare an edit)."""
    product_id = _create_product(client, supplier_id="supplier-1")

    response = client.get(
        f"/api/v1/products/{product_id}",
        headers={"X-User-Id": "supplier-1", "X-User-Role": "Supplier"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == product_id


def test_data_steward_can_view_pending_product_by_id(client):
    """A Data Steward needs to view a PENDING product directly in
    order to review it, even before it's approved."""
    product_id = _create_product(client, supplier_id="supplier-1")

    response = client.get(
        f"/api/v1/products/{product_id}",
        headers={"X-User-Id": "steward-1", "X-User-Role": "DataSteward"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == product_id


def test_unrelated_supplier_cannot_view_another_suppliers_pending_product(client):
    """A different supplier has no ownership claim on this product and
    it isn't approved yet, so it should look exactly like it doesn't
    exist — 404, not 403, so the ID's existence isn't confirmed."""
    product_id = _create_product(client, supplier_id="supplier-1")

    response = client.get(
        f"/api/v1/products/{product_id}",
        headers={"X-User-Id": "supplier-2", "X-User-Role": "Supplier"},
    )

    assert response.status_code == 404


def test_anonymous_user_cannot_view_pending_product_by_id(client):
    """No auth headers at all: same as above, should 404 rather than
    leak that a pending product with this ID exists."""
    product_id = _create_product(client, supplier_id="supplier-1")

    response = client.get(f"/api/v1/products/{product_id}")

    assert response.status_code == 404


def test_anyone_can_view_approved_product_by_id(client):
    """Once a product is APPROVED, it's publicly visible — no auth
    headers required at all."""
    product_id = _create_product(client, supplier_id="supplier-1")
    client.patch(
        f"/api/v1/products/{product_id}/review",
        headers={"X-User-Id": "steward-1", "X-User-Role": "DataSteward"},
        json={"status": "APPROVED"},
    )

    response = client.get(f"/api/v1/products/{product_id}")

    assert response.status_code == 200
    assert response.json()["status"] == "APPROVED"


def test_supplier_can_filter_own_products_by_status(client):
    """A supplier scoping the status filter to their own supplier_id
    should be allowed to see their own PENDING submissions — this is
    how they'd 'track approval status' per the guide."""
    product_id = _create_product(client, supplier_id="supplier-1")

    response = client.get(
        "/api/v1/products?status=PENDING&supplier_id=supplier-1",
        headers={"X-User-Id": "supplier-1", "X-User-Role": "Supplier"},
    )

    assert response.status_code == 200
    product_ids_in_list = [p["id"] for p in response.json()]
    assert product_id in product_ids_in_list


def test_supplier_cannot_filter_by_status_for_another_suppliers_products(client):
    """Scoping supplier_id to someone else while filtering by status
    should still be blocked — a supplier can only use the status
    filter on their own products, not to browse others'."""
    _create_product(client, supplier_id="supplier-1")

    response = client.get(
        "/api/v1/products?status=PENDING&supplier_id=supplier-1",
        headers={"X-User-Id": "supplier-2", "X-User-Role": "Supplier"},
    )

    assert response.status_code == 403