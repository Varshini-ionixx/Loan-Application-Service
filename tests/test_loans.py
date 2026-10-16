from app.auth import create_access_token
from app.models import User


def create_test_user(db_session, role, customer_id=None):
    email = f"{role.lower()}-{customer_id or 'test'}@example.com"
    user = db_session.query(User).filter(User.email == email).first()

    if user is None:
        user = User(
            email=email,
            hashed_password="not-used-in-these-tests",
            role=role,
            customer_id=customer_id,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {"Authorization": f"Bearer {token}"}


def create_test_customer(
    client,
    db_session,
    email="alice@example.com",
    phone="9876543210",
):
    officer_headers = create_test_user(db_session, "OFFICER")
    response = client.post(
        "/api/customers/",
        json={
            "name": "Alice Smith",
            "email": email,
            "phone": phone,
        },
        headers=officer_headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_apply_loan(client, db_session):
    customer_id = create_test_customer(client, db_session)
    headers = create_test_user(db_session, "CUSTOMER", customer_id)

    response = client.post(
        "/api/loans/",
        json={
            "customer_id": customer_id,
            "amount": 100000,
            "tenure_months": 12,
        },
        headers=headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["customer_id"] == customer_id
    assert data["amount"] == 100000
    assert data["tenure_months"] == 12
    assert data["interest_rate"] == 10
    assert data["monthly_emi"] > 0
    assert data["status"] == "APPROVED"


def test_apply_loan_rejects_missing_customer(client, db_session):
    headers = create_test_user(db_session, "OFFICER")

    response = client.post(
        "/api/loans/",
        json={
            "customer_id": 99999,
            "amount": 100000,
            "tenure_months": 12,
        },
        headers=headers,
    )

    assert response.status_code == 404


def test_apply_loan_rejects_invalid_tenure(client, db_session):
    customer_id = create_test_customer(client, db_session)
    headers = create_test_user(db_session, "CUSTOMER", customer_id)

    response = client.post(
        "/api/loans/",
        json={
            "customer_id": customer_id,
            "amount": 100000,
            "tenure_months": 18,
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid tenure"


def test_customer_cannot_apply_for_another_customer(client, db_session):
    customer_id = create_test_customer(client, db_session)
    other_customer_id = create_test_customer(
        client,
        db_session,
        email="bob@example.com",
        phone="9876543211",
    )
    headers = create_test_user(db_session, "CUSTOMER", customer_id)

    response = client.post(
        "/api/loans/",
        json={
            "customer_id": other_customer_id,
            "amount": 100000,
            "tenure_months": 12,
        },
        headers=headers,
    )

    assert response.status_code == 403


def test_list_loans(client, db_session):
    customer_id = create_test_customer(client, db_session)
    headers = create_test_user(db_session, "CUSTOMER", customer_id)

    created = client.post(
        "/api/loans/",
        json={
            "customer_id": customer_id,
            "amount": 100000,
            "tenure_months": 12,
        },
        headers=headers,
    )
    assert created.status_code == 201

    response = client.get("/api/loans/", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["customer_id"] == customer_id
    assert data["page"] == 1
    assert data["size"] == 10
    assert data["total"] == 1
    assert data["pages"] == 1


def test_list_loans_supports_pagination(client, db_session):
    customer_id = create_test_customer(client, db_session)
    headers = create_test_user(db_session, "OFFICER")

    for amount in (100000, 200000, 300000):
        response = client.post(
            "/api/loans/",
            json={
                "customer_id": customer_id,
                "amount": amount,
                "tenure_months": 12,
            },
            headers=headers,
        )
        assert response.status_code == 201

    first_page = client.get("/api/loans/?page=1&size=2", headers=headers)
    second_page = client.get("/api/loans/?page=2&size=2", headers=headers)

    assert first_page.status_code == 200
    assert second_page.status_code == 200

    first_data = first_page.json()
    second_data = second_page.json()

    assert len(first_data["items"]) == 2
    assert first_data["page"] == 1
    assert first_data["size"] == 2
    assert first_data["total"] == 3
    assert first_data["pages"] == 2

    assert len(second_data["items"]) == 1
    assert second_data["page"] == 2
    assert second_data["total"] == 3
    assert second_data["pages"] == 2

    first_ids = {loan["id"] for loan in first_data["items"]}
    second_ids = {loan["id"] for loan in second_data["items"]}
    assert first_ids.isdisjoint(second_ids)


def test_list_loans_filters_by_status(client, db_session):
    customer_id = create_test_customer(client, db_session)
    headers = create_test_user(db_session, "OFFICER")

    created = client.post(
        "/api/loans/",
        json={
            "customer_id": customer_id,
            "amount": 100000,
            "tenure_months": 12,
        },
        headers=headers,
    )
    assert created.status_code == 201

    loan_id = created.json()["id"]
    updated = client.patch(
        f"/api/loans/{loan_id}",
        json={"status": "UNDER_REVIEW"},
        headers=headers,
    )
    assert updated.status_code == 200

    approved_response = client.get(
        "/api/loans/?status=approved",
        headers=headers,
    )
    review_response = client.get(
        "/api/loans/?status=UNDER_REVIEW",
        headers=headers,
    )

    assert approved_response.status_code == 200
    assert approved_response.json()["total"] == 0
    assert approved_response.json()["items"] == []

    assert review_response.status_code == 200
    assert review_response.json()["total"] == 1
    assert review_response.json()["items"][0]["status"] == "UNDER_REVIEW"


def test_list_loans_rejects_invalid_pagination_parameters(client, db_session):
    headers = create_test_user(db_session, "OFFICER")

    invalid_page = client.get("/api/loans/?page=0", headers=headers)
    invalid_size = client.get("/api/loans/?size=101", headers=headers)

    assert invalid_page.status_code == 422
    assert invalid_size.status_code == 422


def test_get_missing_loan_returns_404(client, db_session):
    headers = create_test_user(db_session, "OFFICER")

    response = client.get("/api/loans/99999", headers=headers)

    assert response.status_code == 404


def test_update_loan(client, db_session):
    customer_id = create_test_customer(client, db_session)
    headers = create_test_user(db_session, "OFFICER")

    created = client.post(
        "/api/loans/",
        json={
            "customer_id": customer_id,
            "amount": 100000,
            "tenure_months": 12,
        },
        headers=headers,
    )
    assert created.status_code == 201
    loan_id = created.json()["id"]

    response = client.patch(
        f"/api/loans/{loan_id}",
        json={"status": "UNDER_REVIEW"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "UNDER_REVIEW"


def test_customer_cannot_update_loan(client, db_session):
    customer_id = create_test_customer(client, db_session)
    officer_headers = create_test_user(db_session, "OFFICER")

    created = client.post(
        "/api/loans/",
        json={
            "customer_id": customer_id,
            "amount": 100000,
            "tenure_months": 12,
        },
        headers=officer_headers,
    )
    assert created.status_code == 201
    loan_id = created.json()["id"]

    customer_headers = create_test_user(db_session, "CUSTOMER", customer_id)
    response = client.patch(
        f"/api/loans/{loan_id}",
        json={"status": "UNDER_REVIEW"},
        headers=customer_headers,
    )

    assert response.status_code == 403


def test_delete_loan(client, db_session):
    customer_id = create_test_customer(client, db_session)
    headers = create_test_user(db_session, "OFFICER")

    created = client.post(
        "/api/loans/",
        json={
            "customer_id": customer_id,
            "amount": 100000,
            "tenure_months": 12,
        },
        headers=headers,
    )
    assert created.status_code == 201
    loan_id = created.json()["id"]

    response = client.delete(f"/api/loans/{loan_id}", headers=headers)

    assert response.status_code == 204
    assert response.content == b""

    missing = client.get(f"/api/loans/{loan_id}", headers=headers)
    assert missing.status_code == 404


def test_customer_without_linked_record_cannot_apply_for_loan(client, db_session):
    headers = create_test_user(db_session, "CUSTOMER")

    response = client.post(
        "/api/loans/",
        json={
            "customer_id": 1,
            "amount": 100000,
            "tenure_months": 12,
        },
        headers=headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Your account is not linked to a customer record"
    )


def test_customer_without_linked_record_cannot_list_loans(client, db_session):
    headers = create_test_user(db_session, "CUSTOMER")

    response = client.get("/api/loans/", headers=headers)

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Your account is not linked to a customer record"
    )


def test_customer_cannot_view_another_customers_loan(client, db_session):
    customer_id = create_test_customer(client, db_session)
    officer_headers = create_test_user(db_session, "OFFICER")

    created = client.post(
        "/api/loans/",
        json={
            "customer_id": customer_id,
            "amount": 100000,
            "tenure_months": 12,
        },
        headers=officer_headers,
    )
    assert created.status_code == 201
    loan_id = created.json()["id"]

    other_customer_id = create_test_customer(
        client,
        db_session,
        email="bob@example.com",
        phone="9876543211",
    )
    other_customer_headers = create_test_user(db_session, "CUSTOMER", other_customer_id)

    response = client.get(
        f"/api/loans/{loan_id}",
        headers=other_customer_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == ("You do not have permission to view this loan")
