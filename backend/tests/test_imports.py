import io
import json
from datetime import datetime

import pytest
from openpyxl import Workbook

from app.services.tabular_import import ImportSourceError, google_sheet_export_url
from tests.conftest import register_and_login


def _xlsx_bytes() -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.append(["Booking Date", "Label", "Montant"])
    ws.append([datetime(2026, 1, 5), "Customer payment", 1200.50])
    ws.append([datetime(2026, 1, 6), "Office rent", -800])
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


BANK_CSV = b"""Date;Description;Amount;Type
05/01/2026;Atlas payment;1 200,00;Credit
06/01/2026;Rent;800,00;Debit
"""


def test_xlsx_preview_suggests_mapping(client):
    headers, org = register_and_login(client, "xlsx-a@example.com", org_name="Xlsx A")
    resp = client.post(
        f"/imports/file/preview?organization_id={org}",
        files={"file": ("bank.xlsx", io.BytesIO(_xlsx_bytes()), "application/octet-stream")},
        headers=headers,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["total_rows"] == 2
    assert body["suggested_mapping"]["date"] == "Booking Date"
    assert body["suggested_mapping"]["amount"] == "Montant"
    assert body["suggested_mapping"]["description"] == "Label"
    assert body["sample_rows"][0][0] == "2026-01-05"


def test_xlsx_import_uses_amount_sign_for_direction(client):
    headers, org = register_and_login(client, "xlsx-b@example.com", org_name="Xlsx B")
    mapping = {"date": "Booking Date", "amount": "Montant", "description": "Label"}
    resp = client.post(
        f"/imports/file?organization_id={org}",
        files={"file": ("bank.xlsx", io.BytesIO(_xlsx_bytes()), "application/octet-stream")},
        data={"mapping": json.dumps(mapping)},
        headers=headers,
    )
    assert resp.json() == {"imported": 2, "skipped_duplicates": 0, "errors": []}

    txs = client.get(f"/transactions?organization_id={org}", headers=headers).json()
    by_desc = {t["description"]: t for t in txs}
    assert by_desc["Customer payment"]["direction"] == "IN"
    assert by_desc["Office rent"]["direction"] == "OUT"
    assert by_desc["Office rent"]["amount"] == "800.00"

    again = client.post(
        f"/imports/file?organization_id={org}",
        files={"file": ("bank.xlsx", io.BytesIO(_xlsx_bytes()), "application/octet-stream")},
        data={"mapping": json.dumps(mapping)},
        headers=headers,
    )
    assert again.json()["skipped_duplicates"] == 2


def test_european_csv_with_direction_column(client):
    headers, org = register_and_login(client, "csv-eu@example.com", org_name="Csv EU")
    mapping = {"date": "Date", "amount": "Amount", "direction": "Type", "description": "Description"}
    resp = client.post(
        f"/imports/file?organization_id={org}",
        files={"file": ("bank.csv", io.BytesIO(BANK_CSV), "text/csv")},
        data={"mapping": json.dumps(mapping)},
        headers=headers,
    )
    body = resp.json()
    assert body["imported"] == 2, body
    summary = client.get(f"/financial/summary?organization_id={org}", headers=headers).json()
    assert summary["current_cash"] == "400.00"


def test_import_requires_date_and_amount_mapping(client):
    headers, org = register_and_login(client, "csv-map@example.com", org_name="Csv Map")
    resp = client.post(
        f"/imports/file?organization_id={org}",
        files={"file": ("bank.csv", io.BytesIO(BANK_CSV), "text/csv")},
        data={"mapping": json.dumps({"date": "Date"})},
        headers=headers,
    )
    assert resp.status_code == 400


def test_google_sheet_url_is_rebuilt_not_fetched_as_is():
    url = "https://docs.google.com/spreadsheets/d/abc_123-XYZ/edit#gid=42"
    assert google_sheet_export_url(url) == "https://docs.google.com/spreadsheets/d/abc_123-XYZ/export?format=csv&gid=42"
    for bad in ["https://evil.example/spreadsheets/d/abc", "http://127.0.0.1/spreadsheets/d/x", "file:///etc/passwd"]:
        with pytest.raises(ImportSourceError):
            google_sheet_export_url(bad)


def test_google_sheet_import(client, monkeypatch):
    headers, org = register_and_login(client, "gsheet@example.com", org_name="Gsheet")

    class FakeResponse:
        status_code = 200
        headers = {"content-type": "text/csv; charset=utf-8"}
        content = b"date,amount,description\n2026-01-05,500,Payment\n2026-01-06,-120,Fuel\n"

    monkeypatch.setattr("app.services.tabular_import.httpx.get", lambda *a, **k: FakeResponse())
    sheet = {"url": "https://docs.google.com/spreadsheets/d/abc/edit"}

    preview = client.post(f"/imports/google-sheet/preview?organization_id={org}", json=sheet, headers=headers)
    assert preview.json()["suggested_mapping"]["amount"] == "amount"

    resp = client.post(
        f"/imports/google-sheet?organization_id={org}",
        json={**sheet, "mapping": preview.json()["suggested_mapping"]},
        headers=headers,
    )
    assert resp.json()["imported"] == 2


def test_private_google_sheet_gives_sharing_hint(client, monkeypatch):
    headers, org = register_and_login(client, "gsheet-private@example.com", org_name="Gsheet P")

    class LoginPage:
        status_code = 200
        headers = {"content-type": "text/html"}
        content = b"<html>Sign in</html>"

    monkeypatch.setattr("app.services.tabular_import.httpx.get", lambda *a, **k: LoginPage())
    resp = client.post(
        f"/imports/google-sheet/preview?organization_id={org}",
        json={"url": "https://docs.google.com/spreadsheets/d/abc/edit"},
        headers=headers,
    )
    assert resp.status_code == 400
    assert "Anyone with the link" in resp.json()["detail"]
