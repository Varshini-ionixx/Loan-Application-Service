def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Loan Application Service is running"


def test_create_customer(client):
    response = client.post(
        "/api/customers/",
        json={
            "name": "Alice Smith",
            "email": "alice@example.com",
            "phone": "9876543210",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice Smith"
    assert data["email"] == "alice@example.com"
    assert data["phone"] == "9876543210"
    assert "id" in data


def test_create_customer_rejects_short_name(client):
    response = client.post(
        "/api/customers/",
        json={
            "name": "Al",
            "email": "al@example.com",
            "phone": "9876543210",
        },
    )

    assert response.status_code == 422


def test_create_customer_rejects_invalid_phone(client):
    response = client.post(
        "/api/customers/",
        json={
            "name": "Alice Smith",
            "email": "alice@example.com",
            "phone": "12345",
        },
    )

    assert response.status_code == 422


def test_create_customer_rejects_duplicate_email(client):
    payload = {
        "name": "Alice Smith",
        "email": "alice@example.com",
        "phone": "9876543210",
    }

    first_response = client.post("/api/customers/", json=payload)
    assert first_response.status_code == 201

    second_response = client.post(
        "/api/customers/",
        json={
            "name": "Another Person",
            "email": "alice@example.com",
            "phone": "9876543211",
        },
    )

    assert second_response.status_code == 409


def test_list_customers(client):
    client.post(
        "/api/customers/",
        json={
            "name": "Alice Smith",
            "email": "alice@example.com",
            "phone": "9876543210",
        },
    )

    response = client.get("/api/customers/")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_missing_customer_returns_404(client):
    response = client.get("/api/customers/99999")
    assert response.status_code == 404


def test_update_customer(client):
    created = client.post(
        "/api/customers/",
        json={
            "name": "Alice Smith",
            "email": "alice@example.com",
            "phone": "9876543210",
        },
    )
    customer_id = created.json()["id"]

    response = client.patch(
        f"/api/customers/{customer_id}",
        json={"name": "Alice Jones"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Alice Jones"


def test_delete_customer(client):
    created = client.post(
        "/api/customers/",
        json={
            "name": "Alice Smith",
            "email": "alice@example.com",
            "phone": "9876543210",
        },
    )
    customer_id = created.json()["id"]

    response = client.delete(f"/api/customers/{customer_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Customer deleted successfully"

    missing = client.get(f"/api/customers/{customer_id}")
    assert missing.status_code == 404
