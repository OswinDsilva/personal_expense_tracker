import pytest
from fastapi import status


def transaction_payload(category_id, **overrides):
    payload = {
        "transaction_date": "2026-02-24",
        "description": "Isolation test expense",
        "amount": 125,
        "payment_method": "CASH",
        "transaction_type": "EXPENSE",
        "category_id": category_id,
    }
    payload.update(overrides)
    return payload


def test_second_user_cannot_update_first_users_transaction(
    client,
    auth_headers,
    seed_second_user_with_data,
    seed_transactions,
):
    transaction = seed_transactions["all"][0]
    original_description = transaction.description

    response = client.patch(
        f"/transactions/{transaction.id}",
        headers=seed_second_user_with_data["headers"],
        json=transaction_payload(
            transaction.category_id,
            description="Changed by another user",
        ),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    read_response = client.get(f"/transactions/{transaction.id}", headers=auth_headers)
    assert read_response.status_code == status.HTTP_200_OK
    assert read_response.json()["description"] == original_description


def test_second_user_cannot_delete_first_users_transaction(
    client,
    auth_headers,
    seed_second_user_with_data,
    seed_transactions,
):
    transaction = seed_transactions["all"][0]

    response = client.delete(
        f"/transactions/{transaction.id}",
        headers=seed_second_user_with_data["headers"],
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    read_response = client.get(f"/transactions/{transaction.id}", headers=auth_headers)
    assert read_response.status_code == status.HTTP_200_OK


def test_second_user_cannot_update_first_users_category(
    client,
    auth_headers,
    seed_second_user_with_data,
    seed_categories,
):
    category = seed_categories[0]
    original_name = category.name

    response = client.patch(
        f"/categories/{category.id}",
        headers=seed_second_user_with_data["headers"],
        json={"name": "changed-by-another-user"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    read_response = client.get(f"/categories/{category.id}", headers=auth_headers)
    assert read_response.status_code == status.HTTP_200_OK
    assert read_response.json()["name"] == original_name


def test_second_user_cannot_delete_first_users_category(
    client,
    auth_headers,
    seed_second_user_with_data,
    seed_categories,
):
    category = seed_categories[0]

    response = client.delete(
        f"/categories/{category.id}",
        headers=seed_second_user_with_data["headers"],
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    read_response = client.get(f"/categories/{category.id}", headers=auth_headers)
    assert read_response.status_code == status.HTTP_200_OK


def test_second_user_cannot_update_first_users_starting_balance(
    client,
    auth_headers,
    seed_second_user_with_data,
    seed_starting_balances,
):
    starting_balance = seed_starting_balances[0]
    original_cash_balance = starting_balance.cash_balance
    original_upi_balance = starting_balance.upi_balance

    response = client.patch(
        f"/starting-balances/{starting_balance.id}",
        headers=seed_second_user_with_data["headers"],
        json={"cash_balance": 1, "upi_balance": 2},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    read_response = client.get(f"/starting-balances/{starting_balance.id}", headers=auth_headers)
    assert read_response.status_code == status.HTTP_200_OK
    assert float(read_response.json()["cash_balance"]) == float(original_cash_balance)
    assert float(read_response.json()["upi_balance"]) == float(original_upi_balance)


def test_second_user_cannot_delete_first_users_starting_balance(
    client,
    auth_headers,
    seed_second_user_with_data,
    seed_starting_balances,
):
    starting_balance = seed_starting_balances[0]

    response = client.delete(
        f"/starting-balances/{starting_balance.id}",
        headers=seed_second_user_with_data["headers"],
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    read_response = client.get(f"/starting-balances/{starting_balance.id}", headers=auth_headers)
    assert read_response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    ("resource", "path"),
    [
        ("transaction", "/transactions/{}"),
        ("category", "/categories/{}"),
        ("starting_balance", "/starting-balances/{}"),
    ],
)
def test_second_user_cannot_read_first_users_resources(
    resource,
    path,
    client,
    seed_second_user_with_data,
    seed_transactions,
    seed_categories,
    seed_starting_balances,
):
    resource_ids = {
        "transaction": seed_transactions["all"][0].id,
        "category": seed_categories[0].id,
        "starting_balance": seed_starting_balances[0].id,
    }

    response = client.get(
        path.format(resource_ids[resource]),
        headers=seed_second_user_with_data["headers"],
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    ("path", "response_key", "first_user_fixture", "second_user_key"),
    [
        ("/transactions/", "data", "seed_transactions", "transactions"),
        ("/categories/", None, "seed_categories", "categories"),
        (
            "/starting-balances/",
            None,
            "seed_starting_balances",
            "starting_balances",
        ),
    ],
)
def test_second_users_lists_only_contain_their_own_rows(
    path,
    response_key,
    first_user_fixture,
    second_user_key,
    request,
    client,
    seed_second_user_with_data,
):
    first_user_rows = request.getfixturevalue(first_user_fixture)
    if first_user_fixture == "seed_transactions":
        first_user_rows = first_user_rows["all"]

    response = client.get(path, headers=seed_second_user_with_data["headers"])

    assert response.status_code == status.HTTP_200_OK
    response_body = response.json()
    rows = response_body[response_key] if response_key else response_body
    returned_ids = {row["id"] for row in rows}
    first_user_ids = {row.id for row in first_user_rows}
    second_user_rows = seed_second_user_with_data[second_user_key]

    assert returned_ids.isdisjoint(first_user_ids)
    assert returned_ids == {row.id for row in second_user_rows}
    assert len(rows) == len(second_user_rows)


def test_second_user_cannot_create_transaction_with_first_users_category(
    client,
    seed_second_user_with_data,
    seed_categories,
):
    response = client.post(
        "/transactions/",
        headers=seed_second_user_with_data["headers"],
        json=transaction_payload(seed_categories[0].id),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Category does not exist"
    list_response = client.get("/transactions/", headers=seed_second_user_with_data["headers"])
    assert list_response.status_code == status.HTTP_200_OK
    assert len(list_response.json()["data"]) == len(seed_second_user_with_data["transactions"])


def test_second_user_cannot_update_transaction_with_first_users_category(
    client,
    seed_second_user_with_data,
    seed_categories,
):
    transaction = seed_second_user_with_data["transaction"]
    original_category_id = transaction.category_id

    response = client.patch(
        f"/transactions/{transaction.id}",
        headers=seed_second_user_with_data["headers"],
        json=transaction_payload(seed_categories[0].id),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    read_response = client.get(
        f"/transactions/{transaction.id}",
        headers=seed_second_user_with_data["headers"],
    )
    assert read_response.status_code == status.HTTP_200_OK
    assert read_response.json()["category_id"] == original_category_id


def test_category_names_are_unique_per_user(
    client,
    seed_second_user_with_data,
    seed_categories,
):
    response = client.post(
        "/categories/",
        headers=seed_second_user_with_data["headers"],
        json={"name": seed_categories[1].name},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["name"] == seed_categories[1].name


def test_starting_balance_months_are_unique_per_user(
    client,
    auth_headers,
    seed_second_user_with_data,
    seed_starting_balances,
):
    first_users_balance = seed_starting_balances[0]
    payload = {
        "month": first_users_balance.month.isoformat(),
        "cash_balance": 10,
        "upi_balance": 20,
    }

    second_user_response = client.post(
        "/starting-balances/",
        headers=seed_second_user_with_data["headers"],
        json=payload,
    )

    assert second_user_response.status_code == status.HTTP_201_CREATED

    first_user_response = client.post(
        "/starting-balances/",
        headers=auth_headers,
        json=payload,
    )

    assert first_user_response.status_code == status.HTTP_409_CONFLICT
