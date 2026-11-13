from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app import main
from app.learning.exercise import Exercise
from app.learning.lesson import Lesson, LessonSection
from app.learning.spaced_review import ReviewSchedule
from app.persistence import capture_state, restore_state


@pytest.fixture
def journey(tmp_path, monkeypatch):
    monkeypatch.setattr(main.settings, 'persistence_enabled', True)
    monkeypatch.setattr(main.settings, 'database_path', str(tmp_path / 'journey.sqlite3'))
    with TestClient(main.app) as client:
        learner = client.post('/api/learners').json()['learner_id']
        client.headers['X-Learner-ID'] = learner
        assert client.put('/api/learner/profile', json={'target_language': 'anglais', 'level': 'A1'}).status_code == 200
        agent = main.app.state.learners.get(learner).agent
        calls = {'lesson': 0, 'exercises': 0}

        async def lesson(**kwargs):
            calls['lesson'] += 1
            return Lesson(id='lesson-one', title='Greetings', language='anglais', level='A1', topic=kwargs['topic'], sections=[LessonSection('Hello', 'Say hello.', 'practice')])

        async def exercises(**kwargs):
            calls['exercises'] += 1
            return [Exercise(id=f'ex-{i}', exercise_type='fill_blank', question='Hello = ?', level='A1', skill='vocabulary', expected_answer='bonjour') for i in range(3)]

        monkeypatch.setattr(agent.learning_engine.lesson_generator, 'generate', lesson)
        monkeypatch.setattr(agent.learning_engine.exercise_generator, 'generate', exercises)
        yield client, agent, calls


def post(client, path, data=None):
    response = client.post('/api/learning/' + path, json=data or {})
    assert response.status_code == 200, response.text
    return response.json()


def test_schedule_success_failure_and_due_boundaries():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    schedule = ReviewSchedule()
    assert schedule.due(now)
    for days in [1, 3, 7, 14, 30, 60, 60]:
        schedule.record(True, now)
        assert schedule.interval_days == days
        assert not schedule.due(now + timedelta(days=days, microseconds=-1))
        assert schedule.due(now + timedelta(days=days))
        now += timedelta(days=days)
    schedule.record(False, now)
    assert schedule.consecutive_correct == 0
    assert schedule.next_review_at == (now + timedelta(minutes=10)).isoformat()
    schedule.record(True, now + timedelta(minutes=10))
    assert schedule.interval_days == 1


def test_plan_restarts_without_regeneration_and_scores_only_corrected_exercises(journey):
    client, agent, calls = journey
    plan = post(client, 'plan/generate')
    assert [i['activity_type'] for i in plan['items']] == ['lesson', 'exercise']
    first = post(client, 'plan/next')
    assert first['kind'] == 'lesson'
    assert post(client, 'plan/next') == first
    assert calls['lesson'] == 1
    assert client.post('/api/learning/plan/generate', json={}).status_code == 409
    assert client.post('/api/learning/plan/items/'+first['item']['id']+'/complete', json={'score': 100}).status_code == 404
    read = post(client, 'plan/items/'+first['item']['id']+'/read')
    assert read['status'] == 'completed' and read['item']['score'] is None
    assert post(client, 'plan/items/'+first['item']['id']+'/read') == read
    activity = post(client, 'plan/next')
    assert 'expected_answer' not in activity['exercise']
    item_id = activity['item']['id']
    for index, answer in enumerate(['bonjour', 'wrong', 'bonjour']):
        data = {'exercise_id': activity['exercise']['id'], 'answer': answer}
        result = post(client, 'plan/items/'+item_id+'/answer', data)
        before = capture_state(agent, main.app.state.learners.get(client.headers['X-Learner-ID']).assessment)
        assert post(client, 'plan/items/'+item_id+'/answer', data) == result
        assert capture_state(agent, main.app.state.learners.get(client.headers['X-Learner-ID']).assessment) == before
        assert client.post('/api/learning/plan/items/'+item_id+'/answer', json={**data, 'answer': 'changed'}).status_code == 409
        activity = result['activity']
    assert activity['item']['score'] == 66.67
    assert post(client, 'plan/next')['status'] == 'finished'
    assert calls == {'lesson': 1, 'exercises': 1}


def test_generation_error_rolls_back_without_completing_or_partially_saving(journey, monkeypatch):
    client, agent, calls = journey
    post(client, 'plan/generate')
    async def broken(**kwargs):
        raise RuntimeError('provider error')
    monkeypatch.setattr(agent.learning_engine.lesson_generator, 'generate', broken)
    assert client.post('/api/learning/plan/next', json={}).status_code == 502
    plan = client.get('/api/learning/plan/current').json()
    assert all(not i['completed'] and 'execution' not in i['metadata'] for i in plan['items'])
    assert not agent.learning_engine.lessons


def test_reviews_due_queue_does_not_reveal_answers_and_rejects_duplicate_grade(journey):
    client, agent, _ = journey
    post(client, 'vocabulary', {'word': 'hello', 'translation': 'bonjour'})
    post(client, 'grammar', {'rule': 'present', 'explanation': 'Habitudes'})
    due = client.get('/api/learning/reviews/due').json()
    assert due['count'] == 2 and 'translation' not in str(due['cards']) and 'bonjour' not in str(due)
    card = due['cards'][0]
    assert post(client, 'reviews/reveal', card)['content'] == 'bonjour'
    graded = post(client, 'reviews/grade', {**card, 'correct': True})
    assert graded['interval_days'] == 1
    assert client.post('/api/learning/reviews/grade', json={**card, 'correct': True}).status_code == 409
    due = client.get('/api/learning/reviews/due').json()
    assert due['count'] == 1 and due['upcoming_count'] == 1
    assert agent.learning_engine.vocabulary.get_word('hello').review_count == 1


def test_failed_review_is_due_again_in_ten_minutes_and_language_filtered(journey):
    client, agent, _ = journey
    post(client, 'vocabulary', {'word': 'hello', 'translation': 'bonjour'})
    card = client.get('/api/learning/reviews/due').json()['cards'][0]
    now = datetime.now(timezone.utc)
    result = post(client, 'reviews/grade', {**card, 'correct': False})
    assert 599 <= (datetime.fromisoformat(result['next_review_at']) - now).total_seconds() <= 602
    assert client.put('/api/learner/profile', json={'target_language': 'espagnol'}).status_code == 200
    assert client.get('/api/learning/reviews/due').json()['count'] == 0
    assert client.post('/api/learning/reviews/reveal', json={**card, 'review_count': 1}).status_code == 400


def test_schedule_and_activity_survive_disk_reload(journey):
    client, agent, calls = journey
    post(client, 'vocabulary', {'word': 'hello', 'translation': 'bonjour'})
    card = client.get('/api/learning/reviews/due').json()['cards'][0]
    result = post(client, 'reviews/grade', {**card, 'correct': True})
    post(client, 'plan/generate')
    first = post(client, 'plan/next')
    learner_id = client.headers['X-Learner-ID']
    del main.app.state.learners.sessions[learner_id]
    assert client.post('/api/learning/plan/next', json={}).json() == first
    restored = main.app.state.learners.get(learner_id).agent.learning_engine
    assert restored.vocabulary.get_word('hello').schedule.next_review_at == result['next_review_at']
    assert restored.vocabulary.get_word('hello').schedule.interval_days == 1


def test_isolation_and_foreign_exercise_cannot_complete_activity(journey):
    client, agent, _ = journey
    post(client, 'plan/generate')
    first = post(client, 'plan/next')
    assert client.post('/api/learning/plan/items/'+first['item']['id']+'/answer', json={'exercise_id':'foreign', 'answer':'bonjour'}).status_code == 404
    other = client.post('/api/learners').json()['learner_id']
    headers = {'X-Learner-ID': other}
    assert client.get('/api/learning/plan/items/'+first['item']['id']+'/activity', headers=headers).status_code == 404
    assert client.get('/api/learning/reviews/due', headers=headers).json()['count'] == 0


def test_linked_review_updates_schedule_once_without_fake_score(journey):
    client, agent, _ = journey
    post(client, 'vocabulary', {'word':'hello', 'translation':'bonjour'})
    engine = agent.learning_engine
    from app.learning.learning_plan import LearningPlan
    engine.current_learning_plan = LearningPlan()
    engine.current_learning_plan.add_item(category='vocabulary', target='hello', activity_type='review', priority=50)
    activity = post(client, 'plan/next');path='plan/items/'+activity['item']['id']+'/read'
    assert client.post('/api/learning/'+path,json={}).status_code == 400
    result = post(client,path,{'correct':True})
    assert result['item']['score'] is None
    assert post(client,path,{'correct':True}) == result
    assert engine.vocabulary.get_word('hello').review_count == 1
    assert engine.vocabulary.get_word('hello').schedule.interval_days == 1


def test_legacy_schedule_defaults_and_new_plan_after_language_change(journey):
    client, agent, _ = journey
    post(client, 'vocabulary', {'word':'hello', 'translation':'bonjour'})
    session=main.app.state.learners.get(client.headers['X-Learner-ID'])
    raw=capture_state(agent,session.assessment).model_dump(mode='json')
    raw['vocabulary'][0].pop('schedule')
    from app.persistence import StateSnapshot
    restore_state(StateSnapshot.model_validate(raw),agent,session.assessment)
    assert agent.learning_engine.vocabulary.get_word('hello').schedule.due()
    post(client, 'plan/generate');post(client,'plan/next')
    client.put('/api/learner/profile',json={'target_language':'espagnol'})
    assert client.post('/api/learning/plan/next',json={}).status_code == 409
    assert client.post('/api/learning/plan/generate',json={}).status_code == 200


def test_review_save_failure_rolls_back_grade_and_schedule(journey, monkeypatch):
    client, agent, _ = journey
    post(client, 'vocabulary', {'word':'hello', 'translation':'bonjour'})
    card = client.get('/api/learning/reviews/due').json()['cards'][0]
    def fail(*args):
        raise OSError('disk full')
    monkeypatch.setattr(main.app.state.store, 'save', fail)
    assert client.post('/api/learning/reviews/grade',json={**card,'correct':True}).status_code == 503
    notion = agent.learning_engine.vocabulary.get_word('hello')
    assert notion.review_count == 0 and notion.schedule.next_review_at is None
    assert client.get('/api/learning/reviews/due').json()['count'] == 1


def test_exercise_corrections_update_linked_review_schedule_exactly_once(journey):
    client, agent, _ = journey
    post(client, 'vocabulary', {'word':'hello', 'translation':'bonjour'})
    post(client, 'plan/generate')
    activity=post(client,'plan/next')
    post(client,'plan/items/'+activity['item']['id']+'/read')
    activity=post(client,'plan/next')
    assert activity['kind'] == 'exercises'
    data={'exercise_id':activity['exercise']['id'],'answer':'bonjour'}
    result=post(client,'plan/items/'+activity['item']['id']+'/answer',data)
    post(client,'plan/items/'+activity['item']['id']+'/answer',data)
    notion=agent.learning_engine.vocabulary.get_word('hello')
    assert notion.review_count == 1 and notion.schedule.interval_days == 1


def test_changed_card_revision_can_resume_after_returning_to_plan(journey):
    client, agent, _ = journey
    from app.learning.learning_plan import LearningPlan
    post(client, 'vocabulary', {'word':'hello', 'translation':'bonjour'})
    engine=agent.learning_engine;engine.current_learning_plan=LearningPlan()
    engine.current_learning_plan.add_item(category='vocabulary',target='hello',activity_type='review',priority=50)
    activity=post(client,'plan/next');path='plan/items/'+activity['item']['id']+'/read'
    post(client,'vocabulary/answer',{'word':'hello','correct':True})
    assert client.post('/api/learning/'+path,json={'correct':True}).status_code == 409
    post(client,'plan/next')
    assert post(client,path,{'correct':False})['status'] == 'completed'


def test_new_routes_keep_authentication_required(tmp_path, monkeypatch):
    monkeypatch.setattr(main.settings,'auth_enabled',True)
    monkeypatch.setattr(main.settings,'persistence_enabled',True)
    monkeypatch.setattr(main.settings,'database_path',str(tmp_path/'auth.sqlite3'))
    with TestClient(main.app,headers={'X-Zephyr-Request':'1'}) as client:
        for path in ['plan/next','plan/generate','reviews/reveal','reviews/grade']:
            assert client.post('/api/learning/'+path,json={}).status_code == 401
        assert client.get('/api/learning/reviews/due').status_code == 401
