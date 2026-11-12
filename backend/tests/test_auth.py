import sqlite3
import time

import pytest
from fastapi.testclient import TestClient

from app import auth
from app.config import settings
from app.main import app
from app.persistence import StateStore, capture_state
from app.sessions import LearnerSession

PASSWORD = 'A long test-only passphrase 42!'
HEADERS = {'X-Zephyr-Request': '1'}


@pytest.fixture
def account_database(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, 'auth_enabled', True)
    monkeypatch.setattr(settings, 'auth_cookie_secure', False)
    monkeypatch.setattr(settings, 'persistence_enabled', True)
    monkeypatch.setattr(settings, 'database_path', str(tmp_path / 'accounts.sqlite3'))
    monkeypatch.setattr(auth, 'SCRYPT_N', 2**14)  # Faster fixture; production parameters tested separately.
    return tmp_path / 'accounts.sqlite3'


@pytest.fixture
def client(account_database):
    with TestClient(app, headers=HEADERS) as client:
        yield client


def register(client, email='alice@example.invalid'):
    response = client.post('/api/auth/register', json={'email': email, 'password': PASSWORD, 'name': 'Alice'})
    assert response.status_code == 201
    return response


def test_production_password_hashes_are_salted_and_verifiable():
    one, two = auth.hash_password(PASSWORD), auth.hash_password(PASSWORD)
    assert one != two
    assert one.startswith('scrypt$131072$8$1$')
    assert auth.verify_password(PASSWORD, one)
    assert not auth.verify_password('wrong password', one)
    assert not auth.verify_password(PASSWORD, 'invalid hash')


def test_registration_cookie_and_no_plaintext_credentials(client, account_database):
    assert client.get('/api/learner/profile', headers={'X-Learner-ID': '00000000-0000-0000-0000-000000000001'}).status_code == 401
    response = register(client)
    assert 'httponly' in response.headers['set-cookie'].lower()
    assert 'samesite=strict' in response.headers['set-cookie'].lower()
    assert response.headers['cache-control'] == 'no-store'
    data = response.json()
    assert data['user']['email'] == 'alice@example.invalid'
    assert PASSWORD not in response.text and 'password_hash' not in response.text
    token = client.cookies[auth.COOKIE_NAME]
    with sqlite3.connect(account_database) as db:
        stored_hash = db.execute('SELECT password_hash FROM accounts').fetchone()[0]
        stored_session = db.execute('SELECT token_hash FROM auth_sessions').fetchone()[0]
    assert PASSWORD not in stored_hash and stored_session != token
    assert client.get('/api/learner/profile', headers={'X-Learner-ID': data['learner_id']}).json()['name'] == 'Alice'
    extra = client.post('/api/learners').json()['learner_id']
    assert client.get('/api/learner/profile', headers={'X-Learner-ID': extra}).status_code == 200


def test_login_rotation_logout_and_replay(client):
    data = register(client).json()
    old = client.cookies[auth.COOKIE_NAME]
    response = client.post('/api/auth/login', json={'email': 'ALICE@EXAMPLE.INVALID', 'password': PASSWORD})
    assert response.status_code == 200
    new = client.cookies[auth.COOKIE_NAME]
    assert new != old
    assert not app.state.auth.authenticate(old)
    assert client.post('/api/auth/logout').status_code == 200
    assert not app.state.auth.authenticate(new)
    assert client.get('/api/auth/session').status_code == 401
    assert client.get('/api/learner/profile', headers={'X-Learner-ID': data['learner_id'], 'Cookie': f'{auth.COOKIE_NAME}={new}'}).status_code == 401


def test_accounts_cannot_read_or_mutate_other_learners(client):
    alice = register(client).json()['learner_id']
    client.post('/api/auth/logout')
    bob = register(client, 'bob@example.invalid').json()['learner_id']
    assert alice != bob
    for method, path, payload in [('GET', '/api/learner/profile', None), ('PUT', '/api/learner/profile', {'name': 'intruder'}), ('DELETE', '/api/chat/memory', None)]:
        response = client.request(method, path, json=payload, headers={'X-Learner-ID': alice})
        assert response.status_code == 404
    assert client.get('/api/learner/profile', headers={'X-Learner-ID': bob}).status_code == 200


def test_duplicate_and_invalid_registration_leave_no_orphan_state(client, account_database):
    register(client)
    duplicate = client.post('/api/auth/register', json={'email': 'Alice@Example.Invalid', 'password': PASSWORD, 'name': 'Other'})
    assert duplicate.status_code == 409
    invalid = client.post('/api/auth/register', json={'email': 'bad', 'password': 'secret', 'name': ' '})
    assert invalid.status_code == 422
    assert 'secret' not in invalid.text
    with sqlite3.connect(account_database) as db:
        assert db.execute('SELECT COUNT(*) FROM learner_states').fetchone()[0] == 1
        assert db.execute('SELECT COUNT(*) FROM accounts').fetchone()[0] == 1


def test_csrf_and_login_throttle(client):
    assert client.post('/api/auth/login', headers={'X-Zephyr-Request': ''}, json={'email': 'a@example.invalid', 'password': PASSWORD}).status_code == 403
    assert client.post('/api/auth/login', headers={'Origin': 'https://foreign.example'}, json={'email': 'a@example.invalid', 'password': PASSWORD}).status_code == 403
    for _ in range(10):
        assert client.post('/api/auth/login', json={'email': 'missing@example.invalid', 'password': PASSWORD}).status_code == 401
    limited = client.post('/api/auth/login', json={'email': 'missing@example.invalid', 'password': PASSWORD})
    assert limited.status_code == 429 and limited.headers['retry-after'] == '900'


def test_session_survives_restart_and_expires(account_database):
    with TestClient(app, headers=HEADERS) as client:
        data = register(client).json()
        token = client.cookies[auth.COOKIE_NAME]
    with TestClient(app, headers={**HEADERS, 'Cookie': f'{auth.COOKIE_NAME}={token}'}) as client:
        assert client.get('/api/auth/session').json()['learner_id'] == data['learner_id']
        with sqlite3.connect(account_database) as db:
            db.execute('UPDATE auth_sessions SET expires_at=?', (time.time()-1,))
        assert client.get('/api/auth/session').status_code == 401


def test_legacy_profiles_need_local_assignment_and_existing_owners_are_protected(account_database):
    store = StateStore(str(account_database))
    legacy = LearnerSession(learner_id='00000000-0000-0000-0000-000000000001')
    legacy.agent.learner.set_name('Legacy learner')
    store.save(capture_state(legacy.agent, legacy.assessment), legacy.learner_id)
    with TestClient(app, headers=HEADERS) as client:
        owned = register(client).json()['learner_id']
        assert client.get('/api/learner/profile', headers={'X-Learner-ID': legacy.learner_id}).status_code == 404
        with pytest.raises(ValueError):
            app.state.auth.link_legacy('alice@example.invalid', owned)
        app.state.auth.link_legacy('alice@example.invalid', legacy.learner_id)
        assert client.get('/api/auth/session').status_code == 401
        client.post('/api/auth/login', json={'email': 'alice@example.invalid', 'password': PASSWORD})
        assert client.get('/api/auth/session').json()['learner_id'] == legacy.learner_id
        assert client.get('/api/learner/profile', headers={'X-Learner-ID': legacy.learner_id}).json()['name'] == 'Legacy learner'


def test_secure_cookies_and_production_configuration(account_database, monkeypatch):
    monkeypatch.setattr(settings, 'app_env', 'production')
    with pytest.raises(RuntimeError):
        with TestClient(app):
            pass
    monkeypatch.setattr(settings, 'auth_cookie_secure', True)
    with TestClient(app, base_url='https://testserver', headers=HEADERS) as client:
        response = register(client)
        assert 'secure' in response.headers['set-cookie'].lower()
        assert client.get('/api/auth/session').status_code == 200


def test_auth_routes_do_not_require_a_learner_header_and_document_request_marker(client):
    schema = client.get('/openapi.json').json()
    for path in ['/api/auth/register', '/api/auth/login', '/api/auth/session', '/api/auth/logout']:
        for operation in schema['paths'][path].values():
            names = [item['name'].lower() for item in operation.get('parameters', [])]
            assert 'x-learner-id' not in names
            assert 'x-zephyr-request' in names


def test_registration_accepts_eight_characters_and_rejects_seven(client):
    rejected = client.post('/api/auth/register', json={'name': 'Boundary test', 'email': 'boundary@example.invalid', 'password': 'abcdef7'})
    assert rejected.status_code == 422
    accepted = client.post('/api/auth/register', json={'name': 'Boundary test', 'email': 'boundary@example.invalid', 'password': 'abcdefg8'})
    assert accepted.status_code == 201
    assert client.post('/api/auth/logout').status_code == 200
    assert client.post('/api/auth/login', json={'email': 'boundary@example.invalid', 'password': 'abcdefg8'}).status_code == 200
