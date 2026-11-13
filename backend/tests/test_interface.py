"""The public interface shares the API origin without bypassing learner isolation."""
from fastapi.testclient import TestClient
from app.main import app


def test_public_interface_and_assets():
    with TestClient(app) as client:
        page = client.get('/ui/')
        assert page.status_code == 200
        assert '<html lang="fr">' in page.text
        for asset, media in [('profile-page.js', 'javascript'), ('profile-page.css', 'text/css'), ('presence-ui.js', 'javascript'), ('presence-3d.mjs', 'javascript'), ('presence-materials.mjs', 'javascript'), ('presence.css', 'text/css'), ('vendor/three/three.module.js', 'javascript'), ('vendor/three/three.core.js', 'javascript'), ('vendor/three/MeshSurfaceSampler.js', 'javascript'), ('app.js', 'javascript'), ('visual-vocabulary.js', 'javascript'), ('style.css', 'text/css'), ('learning-ui.js', 'javascript'), ('learning-ui.css', 'text/css'), ('account-ui.js', 'javascript'), ('voice-loop.js', 'javascript'), ('account-ui.css', 'text/css'), ('oral-answer.js', 'javascript'), ('journey-ui.js', 'javascript'), ('camera-controller.js', 'javascript'), ('companion-ui.js', 'javascript'), ('companion-ui.css', 'text/css'), ('voice-tools.js', 'javascript'), ('voice-engine.js', 'javascript'), ('voice-settings.js', 'javascript'), ('voice-settings.css', 'text/css')]:
            response = client.get('/ui/' + asset)
            assert response.status_code == 200
            assert media in response.headers['content-type']


def test_interface_preserves_api_and_requires_learner():
    with TestClient(app) as client:
        assert client.get('/').json()['version'] == app.version
        assert client.get('/health').json()['status'] == 'healthy'
        assert client.get('/api/chat/memory').status_code == 400
        learner = client.post('/api/learners').json()['learner_id']
        response = client.get('/api/chat/memory', headers={'X-Learner-ID': learner})
        assert response.status_code == 200
        assert response.json()['messages'] == []


def test_interface_does_not_expose_backend_files():
    with TestClient(app) as client:
        for path in ['/ui/.env', '/ui/%2e%2e/backend/.env', '/ui/app/main.py']:
            assert client.get(path).status_code == 404
