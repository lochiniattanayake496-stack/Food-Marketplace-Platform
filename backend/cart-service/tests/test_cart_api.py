from unittest.mock import patch

import pytest

from app.service.product_client import ProductInfo


def _mock_product(id="prod-1", name="Chicken Breast", price=5.99, stock=10):
    """Builds a fake ProductInfo, standing in for a real Product Service
    response. Patched into product_client.fetch_product so Cart Service
    tests never need Product Service actually running."""
    return ProductInfo(id=id, name=name, price=price, stock=stock, status="APPROVED", is_active=True)


def test_get_my_cart_creates_a_new_cart_if_none_exists(client):
    response = client.get(
        "/api/v1/carts",
        headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["customerId"] == "customer-1"
    assert body["items"] == []
    assert body["totalPrice"] == 0.0


def test_get_my_cart_without_auth_returns_401(client):
    response = client.get("/api/v1/carts")

    assert response.status_code == 401


def test_get_my_cart_returns_same_cart_on_repeat_calls(client):
    """Each customer has exactly one active cart — calling GET twice
    should return the same cart id, not create a second one."""
    first = client.get("/api/v1/carts", headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"})
    second = client.get("/api/v1/carts", headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"})

    assert first.json()["id"] == second.json()["id"]


@patch("app.service.cart_service.product_client.fetch_product")
def test_add_item_to_cart_uses_real_product_price_not_client_supplied(mock_fetch, client):
    """Even though AddCartItemRequest no longer accepts a price field at
    all, this confirms the resulting cart item price matches what
    Product Service returned, not anything the client could influence."""
    mock_fetch.return_value = _mock_product(price=5.99, stock=10)

    cart = client.get("/api/v1/carts", headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"}).json()

    response = client.post(
        f"/api/v1/carts/{cart['id']}/items",
        headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"},
        json={"productId": "prod-1", "quantity": 2},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["unitPrice"] == 5.99
    assert body["items"][0]["quantity"] == 2
    assert body["totalPrice"] == 11.98


@patch("app.service.cart_service.product_client.fetch_product")
def test_adding_same_product_twice_increments_quantity(mock_fetch, client):
    mock_fetch.return_value = _mock_product(stock=10)

    cart = client.get("/api/v1/carts", headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"}).json()

    client.post(
        f"/api/v1/carts/{cart['id']}/items",
        headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"},
        json={"productId": "prod-1", "quantity": 2},
    )
    response = client.post(
        f"/api/v1/carts/{cart['id']}/items",
        headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"},
        json={"productId": "prod-1", "quantity": 3},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["quantity"] == 5


@patch("app.service.cart_service.product_client.fetch_product")
def test_add_item_exceeding_stock_returns_400(mock_fetch, client):
    mock_fetch.return_value = _mock_product(stock=3)

    cart = client.get("/api/v1/carts", headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"}).json()

    response = client.post(
        f"/api/v1/carts/{cart['id']}/items",
        headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"},
        json={"productId": "prod-1", "quantity": 5},
    )

    assert response.status_code == 400


@patch("app.service.cart_service.product_client.fetch_product")
def test_add_item_respects_stock_across_multiple_adds(mock_fetch, client):
    """2 already in cart + 2 more requested = 4, but stock is only 3 —
    should be rejected even though neither add alone exceeds stock."""
    mock_fetch.return_value = _mock_product(stock=3)

    cart = client.get("/api/v1/carts", headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"}).json()

    client.post(
        f"/api/v1/carts/{cart['id']}/items",
        headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"},
        json={"productId": "prod-1", "quantity": 2},
    )
    response = client.post(
        f"/api/v1/carts/{cart['id']}/items",
        headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"},
        json={"productId": "prod-1", "quantity": 2},
    )

    assert response.status_code == 400


def test_customer_cannot_add_item_to_another_customers_cart(client):
    cart = client.get("/api/v1/carts", headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"}).json()

    with patch("app.service.cart_service.product_client.fetch_product") as mock_fetch:
        mock_fetch.return_value = _mock_product(stock=10)
        response = client.post(
            f"/api/v1/carts/{cart['id']}/items",
            headers={"X-User-Id": "customer-2", "X-User-Role": "Customer"},
            json={"productId": "prod-1", "quantity": 1},
        )

    assert response.status_code == 403


@patch("app.service.cart_service.product_client.fetch_product")
def test_update_item_quantity(mock_fetch, client):
    mock_fetch.return_value = _mock_product(stock=10)

    cart = client.get("/api/v1/carts", headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"}).json()
    client.post(
        f"/api/v1/carts/{cart['id']}/items",
        headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"},
        json={"productId": "prod-1", "quantity": 2},
    )

    response = client.patch(
        f"/api/v1/carts/{cart['id']}/items/prod-1",
        headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"},
        json={"quantity": 7},
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["quantity"] == 7


@patch("app.service.cart_service.product_client.fetch_product")
def test_update_item_quantity_exceeding_stock_returns_400(mock_fetch, client):
    mock_fetch.return_value = _mock_product(stock=5)

    cart = client.get("/api/v1/carts", headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"}).json()
    client.post(
        f"/api/v1/carts/{cart['id']}/items",
        headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"},
        json={"productId": "prod-1", "quantity": 2},
    )

    response = client.patch(
        f"/api/v1/carts/{cart['id']}/items/prod-1",
        headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"},
        json={"quantity": 9},
    )

    assert response.status_code == 400


def test_update_item_not_in_cart_returns_404(client):
    cart = client.get("/api/v1/carts", headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"}).json()

    response = client.patch(
        f"/api/v1/carts/{cart['id']}/items/does-not-exist",
        headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"},
        json={"quantity": 1},
    )

    assert response.status_code == 404


@patch("app.service.cart_service.product_client.fetch_product")
def test_remove_item_from_cart(mock_fetch, client):
    mock_fetch.return_value = _mock_product(stock=10)

    cart = client.get("/api/v1/carts", headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"}).json()
    client.post(
        f"/api/v1/carts/{cart['id']}/items",
        headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"},
        json={"productId": "prod-1", "quantity": 2},
    )

    response = client.delete(
        f"/api/v1/carts/{cart['id']}/items/prod-1",
        headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"},
    )

    assert response.status_code == 200
    assert response.json()["items"] == []


def test_remove_item_not_in_cart_returns_404(client):
    cart = client.get("/api/v1/carts", headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"}).json()

    response = client.delete(
        f"/api/v1/carts/{cart['id']}/items/does-not-exist",
        headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"},
    )

    assert response.status_code == 404


def test_add_item_to_nonexistent_cart_returns_404(client):
    with patch("app.service.cart_service.product_client.fetch_product") as mock_fetch:
        mock_fetch.return_value = _mock_product(stock=10)
        response = client.post(
            "/api/v1/carts/does-not-exist/items",
            headers={"X-User-Id": "customer-1", "X-User-Role": "Customer"},
            json={"productId": "prod-1", "quantity": 1},
        )

    assert response.status_code == 404