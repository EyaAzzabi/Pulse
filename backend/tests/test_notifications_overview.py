from tests.conftest import register_and_login


def _setup(client, email, org_name):
    headers, org = register_and_login(client, email, org_name=org_name)
    client.post(f"/onboarding/sample-data?organization_id={org}", headers=headers)
    return headers, org


def test_summary_raises_alerts_once(client):
    headers, org = _setup(client, "alerts@example.com", "Alerts Co")
    client.get(f"/financial/summary?organization_id={org}", headers=headers)
    client.get(f"/financial/summary?organization_id={org}", headers=headers)

    notes = client.get(f"/notifications?organization_id={org}", headers=headers).json()
    categories = [n["category"] for n in notes]
    assert categories.count("liquidity_risk") == 1
    assert categories.count("overdue_invoices") == 1
    assert next(n for n in notes if n["category"] == "liquidity_risk")["severity"] == "critical"


def test_unread_count_and_mark_all_read(client):
    headers, org = _setup(client, "unread@example.com", "Unread Co")
    client.get(f"/financial/summary?organization_id={org}", headers=headers)

    assert client.get(f"/notifications/unread-count?organization_id={org}", headers=headers).json()["unread"] >= 2
    client.post(f"/notifications/read-all?organization_id={org}", headers=headers)
    assert client.get(f"/notifications/unread-count?organization_id={org}", headers=headers).json()["unread"] == 0


def test_overview_panels(client):
    headers, org = _setup(client, "overview@example.com", "Overview Co")
    body = client.get(f"/financial/overview?organization_id={org}", headers=headers).json()

    assert body["has_data"] is True
    aging = {a["bucket"]: a for a in body["aging"]}
    assert aging["0-30"]["count"] == 3
    assert aging["0-30"]["amount"] == "7150.00"
    kinds = {u["kind"] for u in body["upcoming"]}
    assert {"payable", "recurring", "receivable"} <= kinds
    assert body["upcoming"] == sorted(body["upcoming"], key=lambda u: u["date"])
    assert body["changes"]["inflow"] != "0"


def test_overview_requires_membership(client):
    _, org = _setup(client, "overview-a@example.com", "Overview A")
    other, _ = register_and_login(client, "overview-b@example.com", org_name="Overview B")
    assert client.get(f"/financial/overview?organization_id={org}", headers=other).status_code == 403
