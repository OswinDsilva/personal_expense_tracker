from fastapi import status


# POST /categories
def test_create_category_success(client, auth_headers):
    response = client.post("/categories", headers=auth_headers, json={"name": "Food"})

    assert response.status_code == status.HTTP_201_CREATED
    # validator check
    assert response.json()["name"] == "food"
    assert "id" in response.json()


def test_create_category_duplicate(client, auth_headers):
    client.post("/categories", headers=auth_headers, json={"name": "Food"})

    response = client.post("/categories", headers=auth_headers, json={"name": "Food"})

    assert response.status_code == status.HTTP_409_CONFLICT


def test_create_category_no_auth(client):
    response = client.post("/categories", json={"name": "Food"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# GET /categories
def test_get_all_categories_list(client, auth_headers, seed_categories):
    response = client.get("/categories", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 3


def test_get_all_categories_empty_list(client, auth_headers):
    response = client.get("/categories", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_all_categories_without_token(client):
    response = client.get("/categories")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# GET categories/{id}
def test_get_by_id_success(client, auth_headers, seed_categories):
    response = client.get(f"/categories/{seed_categories[0].id}", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert "id" in response.json()
    assert response.json()["id"] == seed_categories[0].id


def test_get_by_id_nonexistent(client, auth_headers, seed_categories):
    response = client.get("/categories/9999", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_by_id_no_auth(client, seed_categories):
    response = client.get(f"/categories/{seed_categories[0].id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# PATCH /categories/{id}
def test_update_by_id_success(client, auth_headers, seed_categories):
    response = client.patch(
        f"/categories/{seed_categories[0].id}", headers=auth_headers, json={"name": "vacation"}
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "vacation"


def test_update_by_id_duplicate(client, auth_headers, seed_categories):
    response = client.patch(
        f"/categories/{seed_categories[0].id}", headers=auth_headers, json={"name": "travel"}
    )

    assert response.status_code == status.HTTP_409_CONFLICT


def test_update_by_id_nonexistent(client, auth_headers, seed_categories):
    response = client.patch("/categories/9999", headers=auth_headers, json={"name": "travel"})

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_by_id_no_auth(client, seed_categories):
    response = client.patch(f"/categories/{seed_categories[0].id}", json={"name": "vacation"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# DELETE /categories/{id}
def test_delete_by_id_success(client, auth_headers, seed_categories):
    response = client.delete(f"/categories/{seed_categories[0].id}", headers=auth_headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_by_id_nonexistent(client, auth_headers, seed_categories):
    response = client.delete("/categories/9999", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_by_id_no_auth(client, seed_categories):
    response = client.delete(f"/categories/{seed_categories[0].id}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
