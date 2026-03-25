from fastapi import status


def test_get_monthly_data_success(client, auth_headers, seed_transactions):
    response = client.get("/reports/data/2026/2", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["daily_breakdown"]) != 0
    assert response.json()["starting_balance"] is not None
    assert response.json()["ending_balance"] is not None


def test_get_monthly_data_with_no_starting_balance_fail(client, auth_headers, seed_transactions):
    response = client.get("/reports/data/2026/3", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_monthly_data_with_no_transactions(client, auth_headers, seed_transactions):
    response = client.get("reports/data/2026/1", headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["daily_breakdown"]) == 31
    assert response.json()["totals"]["cash_spending"] == "0"
    assert response.json()["totals"]["upi_spending"] == "0"


def test_get_monthly_data_invalid_month_fail(client, auth_headers, seed_transactions):
    response = client.get("reports/2026/13", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_monthly_data_future_month_fail(client, auth_headers, seed_transactions):
    response = client.get("reports/2026/4", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND
