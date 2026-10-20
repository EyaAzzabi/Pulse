"""Exercise a running development API without reading or deleting existing data."""
import json
import os
from decimal import Decimal
from pathlib import Path
import httpx


def main():
    base = os.getenv('PULSE_API_URL', 'http://127.0.0.1:8000/api')
    with httpx.Client(base_url=base, timeout=30) as client:
        response = client.post('/auth/demo')
        response.raise_for_status()
        session = response.json()
        client.headers.update({
            'Authorization': 'Bearer ' + session['token'],
            'X-Organization-ID': session['organization']['id'],
        })
        before = client.get('/financial/summary').json()
        forecast = client.get('/forecast/latest').json()
        assert forecast['shortfall_date'], 'Demo must expose an actual calculated shortfall'
        results = {}
        for fixture in sorted((Path(__file__).resolve().parent.parent / 'demo/scenarios').glob('*.json')):
            response = client.post('/simulations', json=json.loads(fixture.read_text(encoding='utf-8')))
            response.raise_for_status()
            results[fixture.stem] = response.json()
        purchase = results['inventory-purchase']
        assert Decimal(str(purchase['impact'])) == Decimal('-8000')
        assert results['recovery']['min_balance'] > forecast['min_balance']
        after = client.get('/financial/summary').json()
        assert before['metrics'] == after['metrics'], 'Scenarios must not change source balances'
        invoice = next(i for i in before['invoices'] if i['direction'] == 'receivable' and i['status'] == 'overdue')
        response = client.post('/actions/propose', json={'invoice_ids': [invoice['id']]})
        response.raise_for_status()
        action_id = response.json()['id']
        assert client.post(f'/actions/{action_id}/execute').status_code == 409
        response = client.post(f'/actions/{action_id}/approve')
        response.raise_for_status()
        # Do not dispatch configured external integrations during this verification.
        health = client.get('/health').json()
        execution = 'skipped: external integration configured'
        if health.get('automation_mode') == 'local_queue':
            response = client.post(f'/actions/{action_id}/execute')
            response.raise_for_status()
            execution = response.json()['status']
            assert execution == 'QUEUED'
            assert client.post(f'/actions/{action_id}/execute').json()['status'] == 'QUEUED'
        print(json.dumps({
            'current_cash': before['metrics']['current_cash'],
            'baseline_minimum': forecast['min_balance'],
            'first_shortfall': forecast['shortfall_date'],
            'purchase_impact': purchase['impact'],
            'recovery_minimum': results['recovery']['min_balance'],
            'reminder_execution': execution,
            'scenario_isolation': 'verified',
        }, indent=2))


if __name__ == '__main__':
    main()
