def create_test_customer(client):
    response = client.post(
        "/api/customers/",
        json={
            "name": "Alice Smith",
            "email": "alice@example.com",
            "phone": "9876543210",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_apply_loan(client):
    customer_id = create_test_customer(client)

    response = client.post(
        "/api/loans/",
        json={
            "customer_id": customer_id,
            "amount": 100000,
            "tenure_months": 12,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["customer_id"] == customer_id
    assert data["amount"] == 100000
    assert data["tenure_months"] == 12
    assert data["interest_rate"] == 10
    assert data["monthly_emi"] > 0
    assert data["status"] == "APPROVED"


def test_apply_loan_rejects_missing_customer(client):
    response = client.post(
        "/api/loans/",
        json={
            "customer_id": 99999,
            "amount": 100000,
            "tenure_months": 12,
        },
    )

    assert response.status_code == 404


def test_apply_loan_rejects_invalid_tenure(client):
    customer_id = create_test_customer(client)

    response = client.post(
        "/api/loans/",
        json={
            "customer_id": customer_id,
            "amount": 100000,
            "tenure_months": 18,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid tenure"


def test_list_loans(client):
    customer_id = create_test_customer(client)

    client.post(
        "/api/loans/",
        json={
            "customer_id": customer_id,
            "amount": 100000,
            "tenure_months": 12,
        },
    )

    response = client.get("/api/loans/")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_missing_loan_returns_404(client):
    response = client.get("/api/loans/99999")
    assert response.status_code == 404


def test_update_loan(client):
    customer_id = create_test_customer(client)

    created = client.post(
        "/api/loans/",
        json={
            "customer_id": customer_id,
            "amount": 100000,
            "tenure_months": 12,
        },
    )
    assert created.status_code == 201
    loan_id = created.json()["id"]

    response = client.patch(
        f"/api/loans/{loan_id}",
        json={"status": "UNDER_REVIEW"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "UNDER_REVIEW"


def test_delete_loan(client):
    customer_id = create_test_customer(client)

    created = client.post(
        "/api/loans/",
        json={
            "customer_id": customer_id,
            "amount": 100000,
            "tenure_months": 12,
        },
    )
    assert created.status_code == 201
    loan_id = created.json()["id"]

    response = client.delete(f"/api/loans/{loan_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Loan deleted successfully"

    missing = client.get(f"/api/loans/{loan_id}")
    assert missing.status_code == 404
