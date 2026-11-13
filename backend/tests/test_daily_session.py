from datetime import datetime, timezone
from fastapi.testclient import TestClient
import pytest

from app import main
from app.learning.learning_engine import LearningEngine
from app.learning.learner_manager import LearnerProfileManager
from app.learning.learning_plan import LearningPlan
from app.learning.daily_session import daily_summary


def engine():
    learner = LearnerProfileManager()
    learner.set_target_language('anglais');learner.set_level('A1')
    return LearningEngine(learner_manager=learner)


def test_empty_day_is_read_only_and_does_not_generate_a_plan():
    item=engine();result=daily_summary(item,now=datetime(2026,11,13,tzinfo=timezone.utc))
    assert result['profile_ready'] is True
    assert result['plan'] == {'exists':False,'stale':False,'total':0,'completed':0,'completed_today':0,'remaining_minutes':0,'next':None}
    assert result['reviews']['due'] == 0 and item.current_learning_plan is None


def test_pending_plan_and_due_reviews_come_from_real_state():
    item=engine();word=item.add_vocabulary('hello','bonjour')
    item.current_learning_plan=LearningPlan()
    first=item.current_learning_plan.add_item(category='vocabulary',target='hello',activity_type='lesson',priority=50,estimated_minutes=10,metadata={'language':'anglais'})
    second=item.current_learning_plan.add_item(category='vocabulary',target='hello',activity_type='exercise',priority=40,estimated_minutes=15,metadata={'language':'anglais','execution':{'kind':'exercises'}})
    first.completed=True;first.completed_at='2026-11-13T10:00:00+00:00'
    result=daily_summary(item,now=datetime(2026,11,13,11,tzinfo=timezone.utc))
    assert result['plan']['completed']==1 and result['plan']['completed_today']==1
    assert result['plan']['next']['id']==second.id and result['plan']['next']['started'] is True
    assert result['plan']['remaining_minutes']==15 and result['reviews']['due']==1
    assert 'translation' not in str(result)


def test_local_day_boundaries_and_unique_notions_reviewed_today():
    item=engine();word=item.add_vocabulary('hello','bonjour')
    now=datetime(2026,11,13,0,30,tzinfo=timezone.utc)
    word.schedule.record(True,datetime(2026,11,12,23,tzinfo=timezone.utc))
    # At UTC-2 it is still November 12; the same completed review belongs to today.
    local=daily_summary(item,-120,now)
    utc=daily_summary(item,0,now)
    assert local['date']=='2026-11-12' and local['reviews']['reviewed_today']==1
    assert utc['date']=='2026-11-13' and utc['reviews']['reviewed_today']==0
    assert local['reviews']['due']==0 and local['reviews']['next_review_at']==word.schedule.next_review_at


def test_stale_plan_and_other_languages_do_not_count_as_current_progress():
    item=engine();item.add_vocabulary('hello','bonjour')
    item.current_learning_plan=LearningPlan()
    item.current_learning_plan.add_item(category='vocabulary',target='hello',activity_type='exercise',priority=40,metadata={'language':'anglais'})
    item.learner.set_target_language('espagnol')
    result=daily_summary(item)
    assert result['plan']['stale'] and result['plan']['next'] is None
    assert result['plan']['total']==0 and result['reviews']['due']==0


def test_today_api_is_private_isolated_and_does_not_mutate(tmp_path,monkeypatch):
    monkeypatch.setattr(main.settings,'persistence_enabled',True)
    monkeypatch.setattr(main.settings,'database_path',str(tmp_path/'daily.sqlite3'))
    with TestClient(main.app) as client:
        ids=[client.post('/api/learners').json()['learner_id'] for _ in range(2)]
        headers={'X-Learner-ID':ids[0]}
        client.put('/api/learner/profile',json={'target_language':'anglais','level':'A1'},headers=headers)
        client.post('/api/learning/vocabulary',json={'word':'hello','translation':'bonjour'},headers=headers)
        before=main.app.state.store.load(ids[0])
        response=client.get('/api/learning/today',headers=headers)
        assert response.status_code==200 and response.json()['reviews']['due']==1
        assert response.headers['cache-control']=='no-store'
        assert main.app.state.store.load(ids[0])==before
        other=client.get('/api/learning/today',headers={'X-Learner-ID':ids[1]}).json()
        assert other['reviews']['due']==0 and not other['profile_ready']
        assert client.get('/api/learning/today?utc_offset_minutes=841',headers=headers).status_code==422
        assert client.get('/api/learning/today',headers={}).status_code==400


def test_today_requires_login_when_accounts_enabled(tmp_path,monkeypatch):
    monkeypatch.setattr(main.settings,'auth_enabled',True)
    monkeypatch.setattr(main.settings,'persistence_enabled',True)
    monkeypatch.setattr(main.settings,'database_path',str(tmp_path/'auth.sqlite3'))
    with TestClient(main.app) as client:
        assert client.get('/api/learning/today').status_code==401
