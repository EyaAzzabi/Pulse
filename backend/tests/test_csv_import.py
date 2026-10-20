import io

from tests.conftest import register_and_login

VALID_CSV = b"""date,amount,direction,category,description
2026-01-01,500.00,IN,sales_revenue,Payment from customer
2026-01-02,120.50,OUT,operations,Office supplies
"""

INVALID_CSV = b"""date,amount,direction,category
not-a-date,500.00,IN,sales
2026-01-02,abc,OUT,operations
2026-01-03,100.00,SIDEWAYS,operations
"""


def test_import_valid_csv(client):
    headers, org_id = register_and_login(client, "import-a@example.com", org_name="Import A")
    resp = client.post(
        f"/transactions/import?organization_id={org_id}",
        files={"file": ("transactions.csv", io.BytesIO(VALID_CSV), "text/csv")},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["imported"] == 2
    assert body["skipped_duplicates"] == 0
    assert body["errors"] == []


def test_import_is_idempotent(client):
    headers, org_id = register_and_login(client, "import-b@example.com", org_name="Import B")
    client.post(
        f"/transactions/import?organization_id={org_id}",
        files={"file": ("transactions.csv", io.BytesIO(VALID_CSV), "text/csv")},
        headers=headers,
    )
    resp = client.post(
        f"/transactions/import?organization_id={org_id}",
        files={"file": ("transactions.csv", io.BytesIO(VALID_CSV), "text/csv")},
        headers=headers,
    )
    body = resp.json()
    assert body["imported"] == 0
    assert body["skipped_duplicates"] == 2


def test_import_reports_row_errors(client):
    headers, org_id = register_and_login(client, "import-c@example.com", org_name="Import C")
    resp = client.post(
        f"/transactions/import?organization_id={org_id}",
        files={"file": ("transactions.csv", io.BytesIO(INVALID_CSV), "text/csv")},
        headers=headers,
    )
    body = resp.json()
    assert body["imported"] == 0
    assert len(body["errors"]) == 3


def test_import_requires_accountant_role_or_above(client):
    headers, org_id = register_and_login(client, "import-d@example.com", org_name="Import D")
    other_headers, _ = register_and_login(client, "import-d-outsider@example.com", org_name="Outsider")
    resp = client.post(
        f"/transactions/import?organization_id={org_id}",
        files={"file": ("transactions.csv", io.BytesIO(VALID_CSV), "text/csv")},
        headers=other_headers,
    )
    assert resp.status_code == 403
