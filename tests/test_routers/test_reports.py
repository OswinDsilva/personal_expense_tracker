from datetime import date, timedelta

from fastapi import status


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


def test_get_monthly_data_no_auth(client,seed_transactions):
    response = client.get("/reports/data/2026/2")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


