from datetime import date, timedelta

from fastapi import status


# POST "/transactions"
def test_create_transaction_success(client, auth_headers, seed_categories):
    response = client.post(
        "/transactions",
        headers=auth_headers,
        json={
            "transaction_date": "2026-02-24",
            "description": "Test",
            "amount": 5,
            "payment_method": "CASH",
            "transaction_type": "EXPENSE",
            "category_id": seed_categories[0].id,
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.json()
    assert response.json()["category"] is not None


def test_create_transaction_future_date_fails(client, auth_headers, seed_categories):
    future_date = date.today() + timedelta(days=1)

    response = client.post(
        "/transactions",
        headers=auth_headers,
        json={
            "transaction_date": future_date.isoformat(),
            "description": "Future transaction",
            "amount": "50.00",
            "payment_method": "CASH",
            "transaction_type": "EXPENSE",
            "category_id": seed_categories[0].id,
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_invalid_category_transaction(client, auth_headers, seed_categories):
    response = client.post(
        "/transactions",
        headers=auth_headers,
        json={
            "transaction_date": "2026-02-24",
            "description": "Test",
            "amount": 5,
            "payment_method": "CASH",
            "transaction_type": "EXPENSE",
            "category_id": 9999,
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_invalidate_transfer_transactions(client, auth_headers, seed_categories):
    response = client.post(
        "/transactions",
        headers=auth_headers,
        json={
            "transaction_date": "2026-02-24",
            "description": "Test",
            "amount": 5,
            "payment_method": "CASH",
            "transaction_type": "TRANSFER",
            "category_id": seed_categories[0].id,
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_expense_without_category_failure(client, auth_headers, seed_categories):
    response = client.post(
        "/transactions",
        headers=auth_headers,
        json={
            "transaction_date": "2026-02-24",
            "description": "Test",
            "amount": 5,
            "payment_method": "CASH",
            "transaction_type": "EXPENSE",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_transaction_no_auth(client, seed_categories):
    response = client.post(
        "/transactions",
        json={
            "transaction_date": "2026-02-24",
            "description": "Test",
            "amount": 5,
            "payment_method": "CASH",
            "transaction_type": "EXPENSE",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# POST "/transactions/transfer"
def test_create_transfer_success(client, auth_headers):
    response = client.post(
        "/transactions/transfer",
        headers=auth_headers,
        json={
            "transaction_date": "2026-02-24",
            "description": "Test",
            "amount": 5,
            "source_method": "UPI",
            "destination_method": "CASH",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert len(response.json()) == 2

    data = response.json()

    assert data[0]["linked_transfer_id"] == data[1]["id"]
    assert data[1]["linked_transfer_id"] == data[0]["id"]

    assert data[0]["transaction_type"] == "TRANSFER"
    assert data[1]["transaction_type"] == "TRANSFER"

    assert data[0]["is_debit"] is True
    assert data[1]["is_debit"] is False

    assert data[0]["payment_method"] == "UPI"
    assert data[1]["payment_method"] == "CASH"


def test_create_transfer_future_date_fails(client, auth_headers):
    future_date = date.today() + timedelta(days=1)

    response = client.post(
        "/transactions/transfer",
        headers=auth_headers,
        json={
            "transaction_date": future_date.isoformat(),
            "description": "Future transfer",
            "amount": "100.00",
            "source_method": "UPI",
            "destination_method": "CASH",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_same_methods_failure(client, auth_headers):
    response = client.post(
        "/transactions/transfer",
        headers=auth_headers,
        json={
            "transaction_date": "2026-02-24",
            "description": "Test",
            "amount": 5,
            "source_method": "UPI",
            "destination_method": "UPI",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_transfer_no_auth(client):
    response = client.post(
        "/transactions/transfer",
        json={
            "transaction_date": "2026-02-24",
            "description": "Test",
            "amount": 5,
            "source_method": "UPI",
            "destination_method": "CASH",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# GET "/transactions"
def test_get_all_transactions_success(client, auth_headers, seed_transactions):
    response = client.get("/transactions", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == len(seed_transactions)


def test_filter_transactions_by_date_range(client, auth_headers, seed_transactions):
    response = client.get(
        "/transactions",
        params={"start_date": "2026-02-01", "end_date": "2026-02-02"},
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    returned_ids = [r["id"] for r in response.json()]

    assert seed_transactions[0].id in returned_ids

    assert seed_transactions[1].id not in returned_ids
    assert seed_transactions[2].id not in returned_ids
    assert seed_transactions[3].id not in returned_ids


def test_filter_transactions_by_only_start_date(client, auth_headers, seed_transactions):
    response = client.get(
        "/transactions", params={"start_date": "2026-02-03"}, headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK

    returned_ids = [r["id"] for r in response.json()]

    assert seed_transactions[0].id not in returned_ids

    assert seed_transactions[1].id in returned_ids
    assert seed_transactions[2].id in returned_ids
    assert seed_transactions[3].id in returned_ids


def test_filter_transaction_by_only_end_date(client, auth_headers, seed_transactions):
    response = client.get("/transactions", params={"end_date": "2026-02-24"}, headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK

    returned_ids = [r["id"] for r in response.json()]

    assert seed_transactions[0].id in returned_ids
    assert seed_transactions[1].id in returned_ids
    assert seed_transactions[2].id in returned_ids

    assert seed_transactions[3].id not in returned_ids


def test_filter_transactions_by_category(client, auth_headers, seed_transactions, seed_categories):
    response = client.get(
        "/transactions", params={"category_id": seed_categories[0].id}, headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    for record in data:
        assert record["category_id"] == seed_categories[0].id


def test_filter_transactions_by_transaction_type(client, auth_headers, seed_transactions):
    response = client.get(
        "/transactions", params={"transaction_type": "transfer"}, headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    for record in data:
        assert record["transaction_type"] == "TRANSFER"


def test_filter_transactions_invalid_transaction_type(client, auth_headers, seed_transactions):
    response = client.get(
        "/transactions", params={"transaction_type": "wrong"}, headers=auth_headers
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_filter_transactions_by_payment_method(client, auth_headers, seed_transactions):
    response = client.get("/transactions", params={"payment_method": "upi"}, headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    for record in data:
        assert record["payment_method"] == "UPI"


def test_filter_transactions_invalid_payment_method(client, auth_headers, seed_transactions):
    response = client.get("/transactions", params={"payment_method": "wrong"}, headers=auth_headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_filter_transactions_by_multiple_filters(
    client, auth_headers, seed_transactions, seed_categories
):
    response = client.get(
        "/transactions",
        params={
            "start_date": "2026-02-01",
            "end_date": "2026-02-24",
            "category_id": seed_categories[0].id,
            "transaction_type": "expense",
            "payment_method": "upi",
        },
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK

    returned_ids = [r["id"] for r in response.json()]

    assert seed_transactions[0].id in returned_ids

    assert seed_transactions[1].id not in returned_ids
    assert seed_transactions[2].id not in returned_ids
    assert seed_transactions[3].id not in returned_ids


def test_get_all_transactions_no_auth(client, seed_transactions):
    response = client.get("/transactions")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# GET "/transactions/{id}"
def test_get_transaction_by_id_success(client, auth_headers, seed_transactions):
    response = client.get(f"/transactions/{seed_transactions[0].id}", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == seed_transactions[0].id


def test_get_transaction_by_id_invalid_id(client, auth_headers, seed_transactions):
    response = client.get("/transactions/9999", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_transaction_by_id_no_auth(client, seed_transactions):
    response = client.get(f"/transactions/{seed_transactions[0].id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# PATCH "/transactions/{id}"
def test_update_transaction_by_id_success(client, auth_headers, seed_transactions, seed_categories):
    response = client.patch(
        f"/transactions/{seed_transactions[0].id}",
        headers=auth_headers,
        json={
            "transaction_date": "2026-02-24",
            "description": "Updating expense",
            "amount": 5000,
            "category_id": seed_categories[0].id,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["category_id"] == seed_categories[0].id


def test_update_transaction_future_date_fails(client, auth_headers, seed_transactions):
    future_date = date.today() + timedelta(days=1)

    response = client.patch(
        f"/transactions/{seed_transactions[0].id}",
        headers=auth_headers,
        json={"transaction_date": future_date.isoformat()},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_update_transaction_by_id_partial_fields_success(
    client, auth_headers, seed_transactions, seed_categories
):
    response = client.patch(
        f"/transactions/{seed_transactions[0].id}",
        headers=auth_headers,
        json={
            "transaction_date": "2026-02-24",
            "category_id": seed_categories[0].id,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["category_id"] == seed_categories[0].id


def test_update_transaction_by_id_invalid_id(
    client, auth_headers, seed_transactions, seed_categories
):
    response = client.patch(
        "/transactions/9999",
        headers=auth_headers,
        json={
            "transaction_date": "2026-02-24",
            "description": "Updating expense",
            "amount": 5000,
            "category_id": seed_categories[0].id,
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_transaction_by_id_update_transfer_failure(
    client, auth_headers, seed_transactions, seed_categories
):
    response = client.patch(
        f"/transactions/{seed_transactions[1].id}",
        headers=auth_headers,
        json={
            "transaction_date": "2026-02-24",
            "description": "Updating transfer",
            "amount": 5000,
            "category_id": seed_categories[0].id,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_transaction_by_id_null_category_for_expense(
    client, auth_headers, seed_transactions
):
    response = client.patch(
        f"/transactions/{seed_transactions[0].id}",
        headers=auth_headers,
        json={
            "transaction_date": "2026-02-24",
            "description": "Updating expense",
            "amount": 5000,
            "category_id": None,
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_update_transaction_by_id_nonexistent_category(client, auth_headers, seed_transactions):
    response = client.patch(
        f"/transactions/{seed_transactions[0].id}",
        headers=auth_headers,
        json={
            "transaction_date": "2026-02-24",
            "description": "Updating expense",
            "amount": 5000,
            "category_id": 9999,
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_transaction_by_id_no_auth(client, seed_transactions, seed_categories):
    response = client.patch(
        f"/transactions/{seed_transactions[0].id}",
        json={
            "transaction_date": "2026-02-24",
            "description": "Updating expense",
            "amount": 5000,
            "category_id": seed_categories[0].id,
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# DELETE "/transactions/{id}"
def test_delete_transaction_by_id_success(client, auth_headers, seed_transactions):
    response = client.delete(f"/transactions/{seed_transactions[0].id}", headers=auth_headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_transaction_by_id_invalid_id(client, auth_headers, seed_transactions):
    response = client.delete("/transactions/9999", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_transaction_by_id_cascade_transfers(
    client, auth_headers, seed_transactions, seed_categories
):
    # seed_transactions[1] is the transfer debit and seed_transactions[2] is the transfer credit
    response = client.delete(f"/transactions/{seed_transactions[1].id}", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert (
        client.get(f"/transactions/{seed_transactions[1].id}", headers=auth_headers).status_code
        == status.HTTP_404_NOT_FOUND
    )
    assert (
        client.get(f"/transactions/{seed_transactions[2].id}", headers=auth_headers).status_code
        == status.HTTP_404_NOT_FOUND
    )


def test_delete_transaction_by_id_no_auth(client, seed_transactions):
    response = client.delete(f"/transactions/{seed_transactions[0].id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
