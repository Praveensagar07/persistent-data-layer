import os
import sys
import tempfile
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

tmp = tempfile.mkdtemp()
db_file = Path(tmp) / 'live_restart_test.db'
os.environ['DATABASE_URL'] = f'sqlite:///{db_file}'
os.environ['SEED_DATA_ON_STARTUP'] = 'false'

from app.core.config import get_settings
get_settings.cache_clear()

import importlib
import app.db.session
importlib.reload(app.db.session)
import app.main
importlib.reload(app.main)

from fastapi.testclient import TestClient

# Session 1: Boot application, create resources
with TestClient(app.main.app) as client:
    u = client.post('/api/v1/users', json={'name': 'Ada Lovelace', 'email': 'ada@analytical.org'}).json()['data']
    p = client.post('/api/v1/projects', json={'name': 'Analytical Engine', 'owner_id': u['id']}).json()['data']
    t = client.post('/api/v1/tasks', json={'title': 'Bernoulli Algorithm', 'project_id': p['id'], 'assignee_id': u['id']}).json()['data']
    print('Session 1 Created:')
    print('  User:', u['id'], u['name'])
    print('  Project:', p['id'], p['name'])
    print('  Task:', t['id'], t['title'])
    u_id, p_id, t_id = u['id'], p['id'], t['id']

print('Application Session 1 completely terminated.')

# Session 2: Cold restart against the same persistent database file
get_settings.cache_clear()
importlib.reload(app.db.session)
importlib.reload(app.main)

with TestClient(app.main.app) as client2:
    r_u = client2.get(f'/api/v1/users/{u_id}')
    r_p = client2.get(f'/api/v1/projects/{p_id}')
    r_t = client2.get(f'/api/v1/tasks/{t_id}')
    assert r_u.status_code == 200, 'User not found after restart!'
    assert r_p.status_code == 200, 'Project not found after restart!'
    assert r_t.status_code == 200, 'Task not found after restart!'
    print('Session 2 Retrieved after cold restart:')
    print('  User:   ', r_u.json()['data']['id'], r_u.json()['data']['name'])
    print('  Project:', r_p.json()['data']['id'], r_p.json()['data']['name'])
    print('  Task:   ', r_t.json()['data']['id'], r_t.json()['data']['title'])
    print('PERSISTENCE CONFIRMED: All records persisted across API restart!')

try:
    db_file.unlink(missing_ok=True)
except Exception:
    pass
