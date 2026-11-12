"""API contracts exercised by the profile and adaptive assessment interface."""
from fastapi.testclient import TestClient
from app.main import app


def learner(client):
    identifier = client.post('/api/learners').json()['learner_id']
    client.headers['X-Learner-ID'] = identifier
    return identifier


def test_profile_and_assessment_resume_without_exposing_solution():
    with TestClient(app) as client:
        learner(client)
        profile = client.put('/api/learner/profile', json={
            'name': 'Test learner', 'target_language': 'anglais',
            'level': 'A1', 'goal': 'Préparer un entretien',
        }).json()
        assert profile['name'] == 'Test learner'
        assert 'Préparer un entretien' in profile['goals']
        start = client.post('/api/assessment/start').json()
        assert 'correct_answer' not in start['question']
        answer = client.post('/api/assessment/answer', json={'answer': 'small'})
        assert answer.status_code == 200
        assert answer.json()['evaluation']['score'] == 100
        resumed = client.get('/api/assessment/question').json()
        assert resumed['question']['id'] != start['question']['id']
        assert resumed['progress']['answered'] == 1
        assert client.get('/api/learner/profile').json()['target_language'] == 'anglais'


def test_finished_assessment_records_one_report_and_restart_keeps_history():
    with TestClient(app) as client:
        learner(client)
        client.put('/api/learner/profile', json={'target_language': 'anglais'})
        client.post('/api/assessment/start')
        for wrong_answer in ['long', 'are', 'horse']:
            response = client.post('/api/assessment/answer', json={'answer': wrong_answer})
            assert response.status_code == 200
        assert response.json()['finished'] is True
        result = client.get('/api/assessment/result')
        assert result.status_code == 200
        assert result.json()['overall_score'] == 0
        assert client.get('/api/assessment/result').json()['assessment_id'] == result.json()['assessment_id']
        assert len(client.get('/api/learner/profile').json()['assessment_history']) == 1
        restarted = client.post('/api/assessment/start').json()
        assert restarted['progress']['answered'] == 0
        assert len(client.get('/api/learner/profile').json()['assessment_history']) == 1
