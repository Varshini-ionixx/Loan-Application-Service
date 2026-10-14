from app.auth import create_access_token
from app.models import User


def create_test_user(db_session, role, customer_id=None):
    user = User(
        email=f"{role.lower()}-{customer_id or 'test'}@example.com",
        hashed_password="not-used-in-these-tests",
        role=role,
        customer_id=customer_id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"Authorization": f"Bearer {token}"}


def create_test_customer(client, headers):
    response = client.post(
        "/api/customers/",
        json={
            "name": "Alice Smith",
            "email": "alice@example.com",
            "phone": "9876543210",
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Loan Application Service is running"


def test_create_customer(client, db_session):
    headers = create_test_user(db_session, "OFFICER")
    response = client.post(
        "/api/customers/",
        json={
            "name": "Alice Smith",
            "email": "alice@example.com",
            "phone": "9876543210",
        },
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice Smith"
    assert data["email"] == "alice@example.com"
    assert data["phone"] == "9876543210"
    assert "id" in data


def test_create_customer_requires_authentication(client):
    response = client.post(
        "/api/customers/",
        json={
            "name": "Alice Smith",
            "email": "alice@example.com",
            "phone": "9876543210",
        },
    )
    assert response.status_code == 401


def test_customer_cannot_create_customer(client, db_session):
    headers = create_test_user(db_session, "CUSTOMER", customer_id=1)
    response = client.post(
        "/api/customers/",
        json={
            "name": "Another Person",
            "email": "another@example.com",
            "phone": "9876543211",
        },
        headers=headers,
    )
    assert response.status_code == 403


def test_create_customer_rejects_short_name(client, db_session):
    headers = create_test_user(db_session, "OFFICER")
    response = client.post(
        "/api/customers/",
        json={
            "name": "Al",
            "email": "al@example.com",
            "phone": "9876543210",
        },
        headers=headers,
    )
    assert response.status_code == 422


def test_create_customer_rejects_invalid_phone(client, db_session):
    headers = create_test_user(db_session, "OFFICER")
    response = client.post(
        "/api/customers/",
        json={
            "name": "Alice Smith",
            "email": "alice@example.com",
            "phone": "12345",
        },
        headers=headers,
    )
    assert response.status_code == 422


def test_create_customer_rejects_duplicate_email(client, db_session):
    headers = create_test_user(db_session, "OFFICER")
    payload = {
        "name": "Alice Smith",
        "email": "alice@example.com",
        "phone": "9876543210",
    }

    first_response = client.post("/api/customers/", json=payload, headers=headers)
    assert first_response.status_code == 201

    second_response = client.post(
        "/api/customers/",
        json={
            "name": "Another Person",
            "email": "alice@example.com",
            "phone": "9876543211",
        },
        headers=headers,
    )
    assert second_response.status_code == 409


def test_list_customers(client, db_session):
    headers = create_test_user(db_session, "OFFICER")
    create_test_customer(client, headers)

    response = client.get("/api/customers/", headers=headers)

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_customer_cannot_list_all_customers(client, db_session):
    headers = create_test_user(db_session, "CUSTOMER", customer_id=1)
    response = client.get("/api/customers/", headers=headers)
    assert response.status_code == 403


def test_get_missing_customer_returns_404(client, db_session):
    headers = create_test_user(db_session, "OFFICER")
    response = client.get("/api/customers/99999", headers=headers)
    assert response.status_code == 404


def test_customer_can_view_own_details(client, db_session):
    officer_headers = create_test_user(db_session, "OFFICER")
    customer = create_test_customer(client, officer_headers)
    customer_headers = create_test_user(
        db_session, "CUSTOMER", customer_id=customer["id"]
    )

    response = client.get(f"/api/customers/{customer['id']}", headers=customer_headers)

    assert response.status_code == 200
    assert response.json()["id"] == customer["id"]


def test_customer_cannot_view_another_customer(client, db_session):
    officer_headers = create_test_user(db_session, "OFFICER")
    customer = create_test_customer(client, officer_headers)
    customer_headers = create_test_user(
        db_session, "CUSTOMER", customer_id=customer["id"] + 100
    )

    response = client.get(f"/api/customers/{customer['id']}", headers=customer_headers)

    assert response.status_code == 403


def test_update_customer(client, db_session):
    headers = create_test_user(db_session, "OFFICER")
    created = create_test_customer(client, headers)

    response = client.patch(
        f"/api/customers/{created['id']}",
        json={"name": "Alice Jones"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Alice Jones"


def test_customer_cannot_update_customer(client, db_session):
    officer_headers = create_test_user(db_session, "OFFICER")
    customer = create_test_customer(client, officer_headers)
    customer_headers = create_test_user(
        db_session, "CUSTOMER", customer_id=customer["id"]
    )

    response = client.patch(
        f"/api/customers/{customer['id']}",
        json={"name": "Alice Jones"},
        headers=customer_headers,
    )

    assert response.status_code == 403


def test_delete_customer(client, db_session):
    headers = create_test_user(db_session, "OFFICER")
    created = create_test_customer(client, headers)

    response = client.delete(f"/api/customers/{created['id']}", headers=headers)

    assert response.status_code == 204
    assert response.content == b""

    missing = client.get(f"/api/customers/{created['id']}", headers=headers)
    assert missing.status_code == 404
