from datetime import date, timedelta

from fastapi import status


# GET /reports/data/{year}/{month}
def test_get_monthly_data_success(client, auth_headers, seed_transactions):
    response = client.get("/reports/data/2026/2", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["daily_breakdown"]) == 28
    assert float(response.json()["starting_balance"]["cash"]) == 3500.00


def test_get_monthly_data_with_no_starting_balance_success(client, auth_headers, seed_transactions):
    response = client.get("/reports/data/2026/3", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK


def test_get_monthly_data_with_no_transactions(client, auth_headers, seed_transactions):
    response = client.get("reports/data/2026/4", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["daily_breakdown"]) == 30
    assert float(response.json()["totals"]["cash_spending"]) == 0
    assert float(response.json()["totals"]["upi_spending"]) == 0


def test_get_monthly_data_invalid_month_fail(client, auth_headers, seed_transactions):
    response = client.get("reports/data/2026/13", headers=auth_headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_monthly_data_future_month_success(client, auth_headers, seed_transactions):
    test = date.today() + timedelta(days=31)

    response = client.get(f"reports/data/{test.year}/{test.month}", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK


def test_get_monthly_data_calculations_no_propogation(client, auth_headers, seed_transactions):
    response = client.get("reports/data/2026/2", headers=auth_headers)

    assert float(response.json()["starting_balance"]["cash"]) == 3500.00
    assert float(response.json()["starting_balance"]["upi"]) == 12000.00
    assert float(response.json()["totals"]["cash_spending"]) == 1650.00
    assert float(response.json()["totals"]["upi_spending"]) == 10450.00
    assert float(response.json()["totals"]["cash_income"]) == 2000.00
    assert float(response.json()["totals"]["upi_income"]) == 50000.00
    assert float(response.json()["ending_balance"]["cash"]) == 3850.00
    assert float(response.json()["ending_balance"]["upi"]) == 51550.00


def test_get_monthly_data_calculations_with_propagation(client, auth_headers, seed_transactions):
    response = client.get("reports/data/2026/3", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert float(response.json()["starting_balance"]["cash"]) == 3850.00
    assert float(response.json()["starting_balance"]["upi"]) == 51550.00
    assert float(response.json()["totals"]["cash_spending"]) == 500.00
    assert float(response.json()["totals"]["upi_spending"]) == 0.00
    assert float(response.json()["totals"]["cash_income"]) == 0.00
    assert float(response.json()["totals"]["upi_income"]) == 5000.00
    assert float(response.json()["ending_balance"]["cash"]) == 3350.00
    assert float(response.json()["ending_balance"]["upi"]) == 56550.00


def test_get_monthly_data_no_base_balance_fails(client, auth_headers, seed_transactions):
    response = client.get("reports/data/2024/1", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_monthly_data_no_auth(client, seed_transactions):
    response = client.get("/reports/data/2026/2")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# GET /reports/data/{year}
def test_get_yearly_data_success(client, auth_headers, seed_transactions):
    response = client.get("reports/data/2026", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert float(response.json()["final_balance"]["cash"]) == 4600.00
    # This value is different compared to the ending_balance of march because the logic takes the starting balance from jan and since there's no balance for jan, it
    # propogates back to december of 2025, which doesnt have the transactions that add up to the starting balance of jan - feb
    assert float(response.json()["final_balance"]["upi"]) == 68750.00


def test_get_yearly_data_no_auth(client, seed_transactions):
    response = client.get("reports/data/2026")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# GET /reports/exports/{year}/{month}
def test_get_month_report_success(client, auth_headers, seed_transactions):
    response = client.get("reports/exports/2026/2", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert "attachment" in response.headers["content-disposition"]
    assert len(response.content) > 0


def test_get_month_report_invalid_month(client, auth_headers, seed_transactions):
    response = client.get("reports/exports/2026/13", headers=auth_headers)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_month_report_no_auth(client, seed_transactions):
    response = client.get("reports/exports/2026/2")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# GET /reports/exports/{year}
def test_get_year_report_success(client, auth_headers, seed_transactions):
    response = client.get("reports/exports/2026", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert "attachment" in response.headers["content-disposition"]
    assert len(response.content) > 0


def test_get_year_report_no_auth(client, seed_transactions):
    response = client.get("reports/exports/2026")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# GET /reports/exports/{year}/full
def test_get_full_year_report_success(client, auth_headers, seed_transactions):
    response = client.get("reports/exports/2026/full", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert "attachment" in response.headers["content-disposition"]
    assert len(response.content) > 0


def test_get_full_year_report_no_auth(client, seed_transactions):
    response = client.get("reports/exports/2026/full")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
