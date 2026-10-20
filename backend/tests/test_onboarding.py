import io

from tests.conftest import register_and_login

CSV = b"""date,amount,direction,category,description
2026-01-01,1000.00,IN,sales_revenue,Customer payment
2026-01-02,300.00,OUT,operations,Supplies
"""


def test_sample_data_loads_once(client):
    headers, org_id = register_and_login(client, "sample-a@example.com", org_name="Sample A")

    first = client.post(f"/onboarding/sample-data?organization_id={org_id}", headers=headers)
    assert first.status_code == 200
    assert first.json()["loaded"] is True

    summary = client.get(f"/financial/summary?organization_id={org_id}", headers=headers).json()
    assert summary["overdue_receivables_count"] == 3

    second = client.post(f"/onboarding/sample-data?organization_id={org_id}", headers=headers)
    assert second.status_code == 409


def test_finalize_without_history_uses_stated_cash(client):
    headers, org_id = register_and_login(client, "finalize-a@example.com", org_name="Finalize A")
    resp = client.post(
        f"/onboarding/finalize?organization_id={org_id}",
        json={"current_cash_balance": "4500.00"},
        headers=headers,
    )
    assert resp.status_code == 200
    summary = client.get(f"/financial/summary?organization_id={org_id}", headers=headers).json()
    assert summary["current_cash"] == "4500.00"


def test_finalize_after_csv_import_does_not_double_count(client):
    headers, org_id = register_and_login(client, "finalize-b@example.com", org_name="Finalize B")
    client.post(
        f"/transactions/import?organization_id={org_id}",
        files={"file": ("t.csv", io.BytesIO(CSV), "text/csv")},
        headers=headers,
    )
    client.post(
        f"/onboarding/finalize?organization_id={org_id}",
        json={"current_cash_balance": "4500.00"},
        headers=headers,
    )
    summary = client.get(f"/financial/summary?organization_id={org_id}", headers=headers).json()
    assert summary["current_cash"] == "4500.00"


def test_finalize_without_cash_keeps_sample_opening_balance(client):
    headers, org_id = register_and_login(client, "finalize-c@example.com", org_name="Finalize C")
    client.post(f"/onboarding/sample-data?organization_id={org_id}", headers=headers)
    resp = client.post(f"/onboarding/finalize?organization_id={org_id}", json={}, headers=headers)
    assert resp.json()["opening_balance"] == "5000.00"
