import pytest
from fastapi import status


# POST /starting-balances
def test_create_starting_balance_success(client, auth_headers):
    response = client.post(
        "/starting-balances",
        headers=auth_headers,
        json={"month": "2026-02-01", "upi_balance": 0, "cash_balance": 0},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert "id" in response.json()


def test_create_starting_balance_not_first_of_month(client, auth_headers):
    response = client.post(
        "/starting-balances",
        headers=auth_headers,
        json={"month": "2026-02-11", "upi_balance": 0, "cash_balance": 0},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.parametrize(
    "month,cash_balance,upi_balance",
    [("2026-02-01", -1, 0), ("2026-02-01", 0, -1)],
    ids=["negative_cash", "negative_upi"],
)
def test_create_starting_balance_negative_amount(
    month, cash_balance, upi_balance, client, auth_headers
):
    response = client.post(
        "/starting-balances",
        headers=auth_headers,
        json={"month": month, "cash_balance": cash_balance, "upi_balance": upi_balance},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_starting_balance_no_auth(client):
    response = client.post(
        "/starting-balances", json={"month": "2026-02-01", "cash_balance": 0, "upi_balance": 0}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_starting_balance_duplicate(client, auth_headers):
    client.post(
        "/starting-balances",
        headers=auth_headers,
        json={"month": "2026-02-01", "cash_balance": 0, "upi_balance": 0},
    )

    response = client.post(
        "/starting-balances",
        headers=auth_headers,
        json={"month": "2026-02-01", "cash_balance": 0, "upi_balance": 0},
    )

    assert response.status_code == status.HTTP_409_CONFLICT


# GET /starting-balances
def test_get_all_starting_balances_list(client, auth_headers, seed_starting_balances):
    response = client.get("/starting-balances", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == len(seed_starting_balances)


def test_get_all_starting_balances_empty_list(client, auth_headers):
    response = client.get("/starting-balances", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0


def test_get_all_starting_balances_no_auth(client, seed_starting_balances):
    response = client.get("/starting-balances")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# GET /starting-balances/{year}/{month}
def test_get_starting_balance_by_year_month_success(client, auth_headers, seed_starting_balances):
    year = (seed_starting_balances[0].month).year
    month = (seed_starting_balances[0].month).month

    response = client.get(f"/starting-balances/{year}/{month}", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert "id" in response.json()


def test_get_starting_balance_by_year_month_no_record(client, auth_headers, seed_starting_balances):
    response = client.get("/starting-balances/1900/1", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "year,month", [(-2000, 11), (2026, 13)], ids=["invalid_year", "invalid_month"]
)
def test_get_starting_balance_by_year_month_invalid_params(
    year, month, client, auth_headers, seed_starting_balances
):
    response = client.get(f"/starting-balances/{year}/{month}", headers=auth_headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_get_starting_balance_by_year_month_no_auth(client, auth_headers, seed_starting_balances):
    year = (seed_starting_balances[0].month).year
    month = (seed_starting_balances[0].month).month

    response = client.get(f"/starting-balances/{year}/{month}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# GET "/starting-balances/{id}"
def test_get_starting_balance_by_id_success(client, auth_headers, seed_starting_balances):
    response = client.get(
        f"/starting-balances/{seed_starting_balances[0].id}", headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == seed_starting_balances[0].id


def test_get_starting_balance_by_id_nonexistent(client, auth_headers, seed_starting_balances):
    response = client.get("/starting-balances/9999", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_starting_balance_by_id_no_auth(client, auth_headers, seed_starting_balances):
    response = client.get(f"/starting-balances/{seed_starting_balances[0].id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# PATCH "/starting-balances/{id}"
@pytest.mark.parametrize(
    "json_body",
    [
        ({"upi_balance": 5000}),
        ({"cash_balance": 5000}),
        ({"upi_balance": 5000, "cash_balance": 5000}),
    ],
    ids=["update_upi_only", "update_cash_only", "update_both"],
)
def test_update_starting_balance_by_id_success(
    json_body, client, auth_headers, seed_starting_balances
):
    response = client.patch(
        f"/starting-balances/{seed_starting_balances[0].id}", headers=auth_headers, json=json_body
    )

    assert response.status_code == status.HTTP_200_OK
    if "cash_balance" in json_body:
        assert float(response.json()["cash_balance"]) == json_body["cash_balance"]
    if "upi_balance" in json_body:
        assert float(response.json()["upi_balance"]) == json_body["upi_balance"]


def test_update_starting_balance_by_id_nonexistent(client, auth_headers, seed_starting_balances):
    response = client.patch(
        "/starting-balances/9999", headers=auth_headers, json={"upi_balance": 5000}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "cash_balance,upi_balance", [(-500, 500), (500, -500)], ids=["negative_cash", "negative_upi"]
)
def test_update_starting_balance_by_id_negative(
    cash_balance, upi_balance, client, auth_headers, seed_starting_balances
):
    response = client.patch(
        f"/starting-balances/{seed_starting_balances[0].id}",
        headers=auth_headers,
        json={"upi_balance": upi_balance, "cash_balance": cash_balance},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_update_starting_balance_by_id_no_auth(client, auth_headers, seed_starting_balances):
    response = client.patch(
        f"/starting-balances/{seed_starting_balances[0].id}", json={"upi_balance": 5000}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# DELETE "/starting-balances/{id}"
def test_delete_starting_balance_by_id_success(client, auth_headers, seed_starting_balances):
    response = client.delete(
        f"/starting-balances/{seed_starting_balances[0].id}", headers=auth_headers
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_starting_balance_by_id_nonexistent(client, auth_headers, seed_starting_balances):
    response = client.delete("/starting-balances/9999", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_starting_balance_by_id_no_auth(client, auth_headers, seed_starting_balances):
    response = client.delete(f"/starting-balances/{seed_starting_balances[0].id}")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
