from fastapi import status


def test_register_first_user_as_admin(client):
    response = client.post("/auth/register", json={"username": "test", "password": "test1234"})

    assert response.status_code == status.HTTP_201_CREATED
    assert "access_token" in response.json()


def test_register_subsequent_user_fails(client):
    client.post("/auth/register", json={"username": "test", "password": "test1234"})

    response = client.post("/auth/register", json={"username": "test", "password": "test1234"})

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_login_success(
    client,
):
    client.post("/auth/register", json={"username": "test", "password": "test1234"})

    response = client.post("/auth/login", json={"username": "test", "password": "test1234"})

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={"username": "test", "password": "test1234"})

    response = client.post("/auth/login", json={"username": "test", "password": "wrongpass"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_nonexistent_user(client):
    response = client.post("/auth/login", json={"username": "test", "password": "wrongpass"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_me_with_token(client, auth_headers):
    response = client.get("/auth/me", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert "username" in response.json()
    assert "role" in response.json()
    assert "password" not in response.json()
    assert "password_hash" not in response.json()


def test_get_me_without_token(client):
    response = client.get("/auth/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
