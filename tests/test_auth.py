from datetime import timedelta

from app.auth import create_access_token
from app.models import User
from app.security import hash_password


def create_test_user(db_session):
    user = User(
        email="login@example.com",
        hashed_password=hash_password("CorrectPassword123!"),
        role="CUSTOMER",
        customer_id=None,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_login_success(client, db_session):
    create_test_user(db_session)

    response = client.post(
        "/api/auth/login",
        data={
            "username": "login@example.com",
            "password": "CorrectPassword123!",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"


def test_login_rejects_unknown_email(client):
    response = client.post(
        "/api/auth/login",
        data={
            "username": "unknown@example.com",
            "password": "SomePassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_rejects_incorrect_password(client, db_session):
    create_test_user(db_session)

    response = client.post(
        "/api/auth/login",
        data={
            "username": "login@example.com",
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_invalid_token_is_rejected(client):
    response = client.get(
        "/api/customers/",
        headers={"Authorization": "Bearer invalid.token.value"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired access token"


def test_expired_token_is_rejected(client):
    expired_token = create_access_token(
        {"sub": "1", "role": "OFFICER"},
        expires_delta=timedelta(seconds=-1),
    )

    response = client.get(
        "/api/customers/",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired access token"


def test_token_without_user_id_is_rejected(client):
    token = create_access_token({"role": "OFFICER"})

    response = client.get(
        "/api/customers/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"


def test_token_for_deleted_user_is_rejected(client):
    token = create_access_token({"sub": "999999", "role": "OFFICER"})

    response = client.get(
        "/api/customers/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "User no longer exists"


def test_token_with_non_numeric_user_id_is_rejected(client):
    token = create_access_token({"sub": "not-a-number", "role": "OFFICER"})

    response = client.get(
        "/api/customers/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid access token"
