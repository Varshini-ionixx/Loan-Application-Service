from app.auth import create_access_token
from app.models import Customer, User

# Sample customers from the training guide (Day 2 and Day 4).
SAMPLE_PROFILES = {
    "C101": {
        "age": 38,
        "monthly_income": 85000,
        "existing_emi": 12000,
        "credit_score": 745,
    },
    "C102": {
        "age": 29,
        "monthly_income": 60000,
        "existing_emi": 0,
        "credit_score": 790,
    },
    "C103": {
        "age": 52,
        "monthly_income": 40000,
        "existing_emi": 22000,
        "credit_score": 680,
    },
    "C105": {
        "age": 33,
        "monthly_income": 70000,
        "existing_emi": 8000,
        "credit_score": 670,
    },
}


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
    profile=None,
):
    officer_headers = create_test_user(db_session, "OFFICER")
    response = client.post(
        "/api/customers/",
        json={
            "name": "Alice Smith",
            "email": email,
            "phone": phone,
            **(profile or SAMPLE_PROFILES["C101"]),
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


def apply_for_sample_customer(
    client, db_session, sample_id, amount, tenure_months, profile=None
):
    customer_id = create_test_customer(
        client,
        db_session,
        email=f"{sample_id.lower()}@example.com",
        phone=f"98765{sample_id[1:]:0>5}",
        profile=profile or SAMPLE_PROFILES[sample_id],
    )
    headers = create_test_user(db_session, "OFFICER")

    response = client.post(
        "/api/loans/",
        json={
            "customer_id": customer_id,
            "amount": amount,
            "tenure_months": tenure_months,
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_eligible_customer_is_approved(client, db_session):
    loan = apply_for_sample_customer(client, db_session, "C101", 500000, 36)

    assert loan["status"] == "APPROVED"
    assert loan["rejection_reason"] is None


def test_amount_above_ten_lakh_is_referred(client, db_session):
    loan = apply_for_sample_customer(client, db_session, "C102", 1200000, 60)

    assert loan["status"] == "REFERRED"
    assert "senior manager approval" in loan["rejection_reason"]


def test_failed_burden_rule_is_rejected(client, db_session):
    loan = apply_for_sample_customer(client, db_session, "C103", 400000, 24)

    assert loan["status"] == "REJECTED"
    assert loan["rejection_reason"] == (
        "Existing EMI plus new EMI exceeds 50% of monthly income"
    )


def test_credit_score_between_650_and_699_is_referred(client, db_session):
    loan = apply_for_sample_customer(client, db_session, "C105", 300000, 36)

    assert loan["status"] == "REFERRED"
    assert "referred to a credit officer" in loan["rejection_reason"]


def test_rejection_lists_every_failed_rule(client, db_session):
    ineligible = {
        "age": 65,
        "monthly_income": 20000,
        "existing_emi": 15000,
        "credit_score": 600,
    }
    loan = apply_for_sample_customer(
        client, db_session, "C900", 100000, 12, profile=ineligible
    )

    assert loan["status"] == "REJECTED"
    assert loan["rejection_reason"].split("; ") == [
        "Age must be between 21 and 60",
        "Monthly income must be at least 25000",
        "Credit score must be at least 650",
        "Existing EMI plus new EMI exceeds 50% of monthly income",
    ]


def test_customer_without_eligibility_profile_cannot_apply(client, db_session):
    customer = Customer(
        name="Old Customer", email="old@example.com", phone="9000000000"
    )
    db_session.add(customer)
    db_session.commit()
    headers = create_test_user(db_session, "OFFICER")

    response = client.post(
        "/api/loans/",
        json={
            "customer_id": customer.id,
            "amount": 100000,
            "tenure_months": 12,
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Customer profile is missing: age, monthly_income, existing_emi, credit_score"
    )
