import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from app.main import app
with TestClient(app) as client:
    response=client.post('/api/auth/demo');response.raise_for_status();data=response.json()
    print('Fresh isolated synthetic demo created.')
    print('Organization ID:',data['organization']['id'])
    print('Use Explore Interactive Demo in the frontend for a new authenticated session.')
