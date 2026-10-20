"""Browser smoke test. Run after starting both services. Requires playwright."""
import json
import os
from pathlib import Path
import httpx
from playwright.sync_api import sync_playwright, expect


def main():
    health = httpx.get(os.getenv('PULSE_API_URL', 'http://127.0.0.1:8000/api') + '/health').json()
    assert health.get('automation_mode') == 'local_queue', 'Browser test only supports an offline delivery queue'
    destination = Path(__file__).resolve().parent.parent / 'docs/screenshots'
    destination.mkdir(parents=True, exist_ok=True)
    errors = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1440, 'height': 1000}, device_scale_factor=1)
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.goto(os.getenv('PULSE_WEB_URL', 'http://127.0.0.1:5173'), wait_until='networkidle')
        page.screenshot(path=str(destination / 'landing.png'), full_page=True)
        page.get_by_role('button', name='Explore the live demo').click()
        page.wait_for_url('**/dashboard')
        expect(page.get_by_text('Available cash', exact=True)).to_be_visible(timeout=30000)
        expect(page.get_by_text('€18,000', exact=True).first).to_be_visible()
        page.wait_for_timeout(1600)  # Allow Recharts' entry animation to finish before capture.
        page.screenshot(path=str(destination / 'dashboard.png'), full_page=True)
        page.get_by_role('link', name='Digital twin', exact=True).click()
        purchase = page.locator('label.slider-control').filter(has_text='One-time investment').locator('input')
        purchase.fill('8000')
        page.get_by_role('button', name='Run simulation').click()
        expect(page.get_by_text('Minimum scenario cash', exact=True)).to_be_visible(timeout=30000)
        expect(page.get_by_text('-€8,000', exact=True)).to_be_visible()
        page.wait_for_timeout(1600)
        page.screenshot(path=str(destination / 'digital-twin.png'), full_page=True)
        page.get_by_role('link', name='Invoices', exact=True).click()
        page.locator('table input[type=checkbox]').first.check()
        page.get_by_role('button', name='Prepare reminders').click()
        expect(page.get_by_text('PENDING_APPROVAL', exact=True)).to_be_visible(timeout=30000)
        page.get_by_role('button', name='Approve proposal').click()
        expect(page.get_by_text('APPROVED', exact=True)).to_be_visible()
        page.get_by_role('button', name='Execute approved action').click()
        expect(page.get_by_text('QUEUED', exact=True)).to_be_visible()
        page.screenshot(path=str(destination / 'decision-center.png'), full_page=True)
        page.get_by_role('link', name='AI copilot', exact=False).first.click()
        page.get_by_role('button', name='What is my biggest financial risk?').click()
        expect(page.get_by_text('offline', exact=True)).to_be_visible(timeout=30000)
        page.screenshot(path=str(destination / 'copilot.png'), full_page=True)
        for route in ['forecast', 'transactions', 'financing', 'documents', 'notifications', 'settings', 'team', 'automations']:
            page.goto('http://127.0.0.1:5173/' + route, wait_until='networkidle')
            expect(page.locator('main')).to_be_visible()
            assert not page.get_by_text('We couldn’t load this view', exact=True).count(), route
        page.set_viewport_size({'width': 390, 'height': 844})
        page.goto('http://127.0.0.1:5173/dashboard', wait_until='networkidle')
        expect(page.get_by_role('button', name='Open navigation')).to_be_visible()
        page.screenshot(path=str(destination / 'mobile.png'), full_page=True)
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Mobile page overflows'
        assert not errors, errors
        browser.close()
    print(json.dumps({'browser_errors': errors, 'screenshots': str(destination), 'result': 'passed'}, indent=2))


if __name__ == '__main__':
    main()
