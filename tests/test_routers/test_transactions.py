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
    assert len(response.json()["data"]) == len(seed_transactions["all"])


def test_filter_transactions_by_date_range(client, auth_headers, seed_transactions):
    response = client.get(
        "/transactions",
        params={"start_date": "2026-02-01", "end_date": "2026-02-02"},
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()["data"]

    for record in data:
        txn_date = date.fromisoformat(record["transaction_date"])
        assert date(2026, 2, 1) <= txn_date <= date(2026, 2, 2)


def test_filter_transactions_by_only_start_date(client, auth_headers, seed_transactions):
    response = client.get(
        "/transactions", params={"start_date": "2026-02-03"}, headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()["data"]

    for record in data:
        txn_date = date.fromisoformat(record["transaction_date"])
        assert txn_date >= date(2026, 2, 3)


def test_filter_transaction_by_only_end_date(client, auth_headers, seed_transactions):
    response = client.get("/transactions", params={"end_date": "2026-02-24"}, headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK

    data = response.json()["data"]

    for record in data:
        txn_date = date.fromisoformat(record["transaction_date"])
        assert txn_date <= date(2026, 2, 24)


def test_filter_transactions_by_category(client, auth_headers, seed_transactions, seed_categories):
    response = client.get(
        "/transactions", params={"category_id": seed_categories[0].id}, headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()["data"]

    for record in data:
        assert record["category_id"] == seed_categories[0].id


def test_filter_transactions_by_transaction_type(client, auth_headers, seed_transactions):
    response = client.get(
        "/transactions", params={"transaction_type": "transfer"}, headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()["data"]

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

    data = response.json()["data"]

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

    data = response.json()["data"]

    for record in data:
        txn_date = date.fromisoformat(record["transaction_date"])
        assert date(2026, 2, 1) <= txn_date <= date(2026, 2, 24)
        assert record["category_id"] == seed_categories[0].id
        assert record["transaction_type"] == "EXPENSE"
        assert record["payment_method"] == "UPI"


def test_get_all_transactions_no_auth(client, seed_transactions):
    response = client.get("/transactions")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Pagination tests
def test_pagination_first_page(client, auth_headers, seed_transactions):
    response = client.get("/transactions?limit=2", headers=auth_headers)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["pagination"]["next_cursor"] is not None
    assert data["pagination"]["has_more"] is True
    assert len(data["data"]) == 2
    assert data["data"][0]["id"] != data["data"][1]["id"]


def test_pagination_last_page(client, auth_headers, seed_transactions):
    response1 = client.get("/transactions?limit=2", headers=auth_headers)

    data1 = response1.json()
    assert data1["pagination"]["next_cursor"] is not None

    next_cursor = data1["pagination"]["next_cursor"]
    response2 = client.get(
        f"/transactions?cursor={next_cursor}",
        headers=auth_headers,
    )

    data2 = response2.json()

    assert response2.status_code == status.HTTP_200_OK
    assert data2["pagination"]["next_cursor"] is None
    assert data2["pagination"]["has_more"] is False
    assert len(data2["data"]) == len(seed_transactions["all"]) - 2

    page1_ids = {record["id"] for record in data1["data"]}
    page2_ids = {record["id"] for record in data2["data"]}
    assert page1_ids.isdisjoint(page2_ids)


def test_pagination_invalid_cursor(client, auth_headers, seed_transactions):
    response = client.get("/transactions?cursor=invalid", headers=auth_headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_pagination_with_filters(client, auth_headers, seed_transactions, seed_categories):
    response = client.get(
        "/transactions?limit=1",
        params={
            "start_date": "2026-02-01",
            "end_date": "2026-02-24",
        },
        headers=auth_headers,
    )

    next_cursor = response.json()["pagination"]["next_cursor"]

    response2 = client.get(
        f"/transactions?cursor={next_cursor}",
        params={
            "start_date": "2026-02-01",
            "end_date": "2026-02-24",
        },
        headers=auth_headers,
    )

    data = response2.json()

    assert response2.status_code == status.HTTP_200_OK

    for transaction in data["data"]:
        txn_date = date.fromisoformat(transaction["transaction_date"])
        assert date(2026, 2, 1) <= txn_date <= date(2026, 2, 24)

    assert "pagination" in data


# GET "/transactions/{id}"
def test_get_transaction_by_id_success(client, auth_headers, seed_transactions):
    response = client.get(f"/transactions/{seed_transactions['all'][0].id}", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == seed_transactions["all"][0].id


def test_get_transaction_by_id_invalid_id(client, auth_headers, seed_transactions):
    response = client.get("/transactions/9999", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_transaction_by_id_no_auth(client, seed_transactions):
    response = client.get(f"/transactions/{seed_transactions['all'][0].id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# PATCH "/transactions/{id}"
def test_update_transaction_by_id_success(client, auth_headers, seed_transactions, seed_categories):
    response = client.patch(
        f"/transactions/{seed_transactions['all'][0].id}",
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
        f"/transactions/{seed_transactions['all'][0].id}",
        headers=auth_headers,
        json={"transaction_date": future_date.isoformat()},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_update_transaction_by_id_partial_fields_success(
    client, auth_headers, seed_transactions, seed_categories
):
    response = client.patch(
        f"/transactions/{seed_transactions['all'][0].id}",
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
    transfer_response = client.post(
        "/transactions/transfer",
        headers=auth_headers,
        json={
            "transaction_date": "2026-02-24",
            "description": "Transfer to update",
            "amount": 500,
            "source_method": "UPI",
            "destination_method": "CASH",
        },
    )

    assert transfer_response.status_code == status.HTTP_201_CREATED
    transfer_debit_id = transfer_response.json()[0]["id"]

    response = client.patch(
        f"/transactions/{transfer_debit_id}",
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
        f"/transactions/{seed_transactions['all'][0].id}",
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
        f"/transactions/{seed_transactions['all'][0].id}",
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
        f"/transactions/{seed_transactions['all'][0].id}",
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
    response = client.delete(
        f"/transactions/{seed_transactions['all'][0].id}", headers=auth_headers
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_transaction_by_id_invalid_id(client, auth_headers, seed_transactions):
    response = client.delete("/transactions/9999", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_transaction_by_id_cascade_transfers(
    client, auth_headers, seed_transactions, seed_categories
):
    transfer_response = client.post(
        "/transactions/transfer",
        headers=auth_headers,
        json={
            "transaction_date": "2026-02-24",
            "description": "Transfer to delete",
            "amount": 700,
            "source_method": "UPI",
            "destination_method": "CASH",
        },
    )

    assert transfer_response.status_code == status.HTTP_201_CREATED
    transfer_data = transfer_response.json()
    debit_id = transfer_data[0]["id"]
    credit_id = transfer_data[1]["id"]

    response = client.delete(f"/transactions/{debit_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert (
        client.get(f"/transactions/{debit_id}", headers=auth_headers).status_code
        == status.HTTP_404_NOT_FOUND
    )
    assert (
        client.get(f"/transactions/{credit_id}", headers=auth_headers).status_code
        == status.HTTP_404_NOT_FOUND
    )


def test_delete_transaction_by_id_no_auth(client, seed_transactions):
    response = client.delete(f"/transactions/{seed_transactions['all'][0].id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
