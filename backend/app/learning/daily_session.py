"""Read-only summary of the learner's actual plan and review schedule."""
from datetime import datetime, timedelta, timezone


def daily_summary(engine, utc_offset_minutes=0, now=None):
    now = now or datetime.now(timezone.utc)
    local_zone = timezone(timedelta(minutes=utc_offset_minutes))
    today = now.astimezone(local_zone).date()
    context = engine.get_learning_context()
    language = context.get('target_language')
    completed_today = 0
    reviewed_today = 0
    due_count = 0
    next_review = None

    def on_today(value):
        return bool(value) and datetime.fromisoformat(value).astimezone(local_zone).date() == today

    for items in (engine.vocabulary.get_all_words(), engine.grammar.get_all_rules()):
        for item in items:
            if item.language.strip().casefold() != (language or '').strip().casefold():
                continue
            if on_today(item.schedule.last_review_at):
                reviewed_today += 1
            if item.schedule.due(now):
                due_count += 1
            elif next_review is None or item.schedule.next_review_at < next_review:
                next_review = item.schedule.next_review_at

    plan = engine.current_learning_plan
    items = plan.items if plan else []
    stale = any(item.metadata.get('language') and item.metadata['language'] != language for item in items)
    active_items = [] if stale else items
    pending = [item for item in active_items if not item.completed]
    completed_today = sum(1 for item in active_items if item.completed and on_today(item.completed_at))
    next_item = pending[0] if pending else None
    return {
        'date': today.isoformat(), 'target_language': language, 'level': context.get('level'),
        'profile_ready': bool(language and context.get('level')),
        'reviews': {'due': due_count, 'reviewed_today': reviewed_today, 'next_review_at': next_review},
        'plan': {'exists': plan is not None, 'stale': stale, 'total': len(active_items),
                 'completed': sum(item.completed for item in active_items), 'completed_today': completed_today,
                 'remaining_minutes': sum(item.estimated_minutes for item in pending),
                 'next': {'id': next_item.id, 'target': next_item.target, 'activity_type': next_item.activity_type,
                          'estimated_minutes': next_item.estimated_minutes,
                          'started': bool(next_item.metadata.get('execution'))} if next_item else None},
    }
