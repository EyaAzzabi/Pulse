"""Real API and Chromium evidence against the isolated synthetic demo servers."""
import json
from pathlib import Path
from decimal import Decimal
from datetime import datetime, timezone
import sys
import httpx
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "submission"
SHOTS = OUT / "screenshots"
EVIDENCE = OUT / "execution_evidence"
SHOTS.mkdir(exist_ok=True); EVIDENCE.mkdir(exist_ok=True)
state = json.loads((ROOT / ".runtime/submission/private-state.json").read_text())
API = "http://127.0.0.1:8002"
WEB = "http://127.0.0.1:5175"
records = []
client = httpx.Client(base_url=API, timeout=30)
r = client.post("/auth/login", json={"email": state["email"], "password": state["password"]})
r.raise_for_status()
token = r.json()["access_token"]
client.headers["Authorization"] = "Bearer " + token
org = state["organization_id"]


def request(method, path, payload=None, expected=200):
    r = client.request(method, path, params={"organization_id": org}, json=payload)
    records.append({"method": method, "path": path, "synthetic_organization_id": org, "request": payload,
        "status": r.status_code, "response": r.json(), "captured_at_utc": datetime.now(timezone.utc).isoformat()})
    assert r.status_code == expected, (path, r.status_code, r.text)
    return r.json()


summary = request("GET", "/financial/summary")
forecast = request("POST", "/forecast/run", {"horizon_days": 90}, 201)
baseline = request("POST", "/simulations", {"name": "Evidence baseline", "horizon_days": 90}, 201)
rescue = request("POST", "/simulations", {"name": "Extend supplier terms by 15 days", "horizon_days": 90, "supplier_payment_delay_days": 15}, 201)
purchase = request("POST", "/simulations", {"name": "EUR 8,000 inventory purchase", "horizon_days": 90, "inventory_purchase_amount": 8000}, 201)
plans = request("GET", "/recommendations")
chat = request("POST", "/copilot/chat", {"message": "What is my biggest financial risk?"})
invoices = request("GET", "/invoices")
invoice = next(i for i in invoices if i["direction"] == "RECEIVABLE")
proposal = request("POST", "/actions/propose", {"action_type": "send_invoice_reminder", "target": {"invoice_ids": [invoice["id"]]}}, 201)
request("POST", f"/actions/{proposal['id']}/execute", expected=409)

# Independently replay the raw synthetic transactions and each forecast recurrence.
sys.path.insert(0, str(OUT / "scripts"))
import demo_environment
from app.db.session import SessionLocal
from app.models.organization import BusinessProfile
from app.models.financial import Transaction, Invoice, RecurringObligation
with SessionLocal() as db:
    profile = db.query(BusinessProfile).filter_by(organization_id=org).one()
    rows = db.query(Transaction).filter_by(organization_id=org).all()
    today = datetime.now().date()
    independent_cash = profile.current_cash_balance + sum((t.amount if t.direction == "IN" else -t.amount) for t in rows if t.date <= today)
    raw_snapshot = [(i.id, str(i.amount), str(i.amount_paid), str(i.due_date)) for i in db.query(Invoice).filter_by(organization_id=org).all()]
    schema = {table.name: [{"column": c.name, "type": str(c.type), "nullable": c.nullable} for c in table.columns] for table in db.get_bind().dialect and demo_environment.__dict__.get("unused", [])}
    from app.db.session import Base
    schema = {t.name: [{"column": c.name, "type": str(c.type), "nullable": c.nullable} for c in t.columns] for t in Base.metadata.sorted_tables}
assert independent_cash.quantize(Decimal(".01")) == Decimal(summary["current_cash"])
running = Decimal(forecast["starting_cash"])
for point in forecast["points"]:
    running += Decimal(point["known_component"]) + Decimal(point["uncertain_component"])
    assert running.quantize(Decimal(".01")) == Decimal(point["projected_cash"])
assert baseline["baseline_points"] == baseline["simulated_points"]
assert len(forecast["points"]) == 90
assert Decimal(purchase["simulated_points"][0]["projected_cash"]) == Decimal(purchase["baseline_points"][0]["projected_cash"]) - Decimal("8000")
EVIDENCE.joinpath("database_schema.json").write_text(json.dumps(schema, indent=2))
EVIDENCE.joinpath("financial_validation.json").write_text(json.dumps({"independent_cash_replay": "PASS", "cash": str(independent_cash), "forecast_daily_recurrence_90_points": "PASS", "no_change_simulation_equals_baseline": "PASS", "inventory_purchase_day_one_delta": "-8000.00", "mode": "synthetic, no LLM, no external action dispatch"}, indent=2))

errors = []
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    anonymous = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1.5)
    page = anonymous.new_page()
    for path, name in [("/", "01_landing"), ("/login", "02_authentication")]:
        page.goto(WEB + path); page.wait_for_load_state("networkidle"); page.wait_for_timeout(1200)
        page.screenshot(path=str(SHOTS / (name + ".png")))
    anonymous.close()
    context = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1.5,
        record_video_dir=str(ROOT / ".runtime/submission/video"), record_video_size={"width": 1440, "height": 900})
    context.add_init_script("localStorage.setItem('pulse_token', " + json.dumps(token) + "); localStorage.setItem('pulse_current_org_id', " + json.dumps(org) + ")")
    page = context.new_page(); page.on("pageerror", lambda e: errors.append(str(e)))

    def shot(path, name, seconds=0):
        page.goto(WEB + path); page.wait_for_load_state("networkidle"); page.wait_for_timeout(1700)
        page.screenshot(path=str(SHOTS / (name + ".png")))
        if seconds: page.wait_for_timeout(seconds * 1000)

    shot("/onboarding", "03_business_onboarding")
    request("POST", "/onboarding/complete")
    shot("/dashboard", "04_financial_dashboard", 12)
    shot("/forecast", "05_cashflow_forecast", 12)
    shot("/notifications", "06_liquidity_risk_alert", 10)
    page.goto(WEB + "/copilot"); page.wait_for_load_state("networkidle")
    page.locator("form input").fill("What is my biggest financial risk?")
    page.locator('form button[type="submit"]').click()
    expect(page.get_by_text("Offline deterministic mode", exact=True)).to_be_visible(timeout=20000)
    page.wait_for_timeout(2200); page.screenshot(path=str(SHOTS / "07_ai_copilot.png")); page.wait_for_timeout(13000)
    page.goto(WEB + "/simulator"); page.wait_for_load_state("networkidle")
    numbers = page.locator('input[type="number"]')
    numbers.nth(4).fill("8000")
    page.get_by_role("button", name="Run simulation", exact=True).click()
    expect(page.get_by_text("Baseline vs. simulated forecast", exact=True)).to_be_visible(timeout=20000)
    page.wait_for_timeout(1800); page.screenshot(path=str(SHOTS / "08_digital_twin_simulator.png")); page.wait_for_timeout(12000)
    numbers.nth(4).fill("0"); numbers.nth(1).fill("15")
    page.get_by_role("button", name="Run simulation", exact=True).click(); page.wait_for_timeout(2500)
    page.screenshot(path=str(SHOTS / "09_scenario_comparison.png")); page.wait_for_timeout(12000)
    shot("/decisions", "10_human_approval", 12)
    page.get_by_role("button", name="Approve", exact=True).first.click()
    expect(page.get_by_role("button", name="Execute", exact=True).first).to_be_visible()
    page.wait_for_timeout(4000); page.get_by_role("button", name="Execute", exact=True).first.click()
    expect(page.get_by_text("QUEUED", exact=True).first).to_be_visible(timeout=20000)
    page.wait_for_timeout(1700); page.screenshot(path=str(SHOTS / "11_execution_history.png")); page.wait_for_timeout(16000)
    video_path = page.video.path()
    context.close(); browser.close()
    (ROOT / ".runtime/submission/video-path.txt").write_text(str(video_path))

actions = request("GET", "/actions")
assert next(a for a in actions if a["id"] == proposal["id"])["status"] == "QUEUED"
request("POST", f"/actions/{proposal['id']}/execute", expected=409)
with SessionLocal() as db:
    after = [(i.id, str(i.amount), str(i.amount_paid), str(i.due_date)) for i in db.query(Invoice).filter_by(organization_id=org).all()]
assert sorted(raw_snapshot) == sorted(after)
metrics = {"as_of": summary["as_of"], "summary": summary, "baseline_lowest": baseline["lowest_cash_point"], "baseline_days_below_zero": baseline["days_below_zero"],
    "baseline_runway": baseline["runway_days"], "shortfall_date": forecast["shortfall_date"], "rescue_lowest": rescue["lowest_cash_point"],
    "rescue_days_below_zero": rescue["days_below_zero"], "purchase_lowest": purchase["lowest_cash_point"], "rescue_plans": plans,
    "forecast_points": forecast["points"], "rescue_points": rescue["simulated_points"], "copilot_mode": "deterministic", "browser_errors": errors,
    "invoice_records_unchanged": True, "action_result": "QUEUED: no external delivery configured in submission demo"}
EVIDENCE.joinpath("api_requests_responses.json").write_text(json.dumps(records, indent=2))
EVIDENCE.joinpath("demo_metrics.json").write_text(json.dumps(metrics, indent=2))
EVIDENCE.joinpath("browser_results.json").write_text(json.dumps({"viewport": "1440x900", "device_scale": 1.5, "mocked_network": False, "browser_errors": errors,
    "screenshots": [p.name for p in SHOTS.glob("*.png")], "video_source": "real Playwright recording, synthetic backend only"}, indent=2))
assert not errors, errors
print(json.dumps({"screenshots": len(list(SHOTS.glob('*.png'))), "current_cash": summary["current_cash"], "baseline_lowest": baseline["lowest_cash_point"], "rescue_lowest": rescue["lowest_cash_point"], "browser_errors": errors}))
