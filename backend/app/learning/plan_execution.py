"""Resumable plan activities. Scores come from corrections, never the client."""
from datetime import datetime, timezone


class ActivityConflict(ValueError):
    pass


def plan_item(engine, item_id):
    plan = engine.current_learning_plan
    item = next((i for i in plan.items if i.id == item_id), None) if plan else None
    if item is None:
        raise LookupError('Activité introuvable dans le plan actif.')
    language = engine.get_learning_context().get('target_language')
    saved = item.metadata.get('language')
    if saved and saved != language:
        raise ActivityConflict('La langue du profil a changé. Générez un nouveau plan.')
    return item


def public_activity(engine, item):
    execution = item.metadata.get('execution')
    data = {'item': {k: v for k, v in item.to_dict().items() if k != 'metadata'}, 'status': 'completed' if item.completed else 'ready'}
    if not execution:
        return data
    data['kind'] = execution['kind']
    if execution['kind'] == 'lesson':
        lesson = next(i for i in engine.lessons if i.id == execution['lesson_id'])
        data['lesson'] = lesson.to_dict()
    elif execution['kind'] == 'review':
        data['review'] = execution['review']
    else:
        results = execution['results']
        pending = next((i for i in execution['exercise_ids'] if i not in results), None)
        data['progress'] = {'answered': len(results), 'total': len(execution['exercise_ids'])}
        data['results'] = results
        if pending:
            data['exercise'] = next(i for i in engine.exercises if i.id == pending).to_public_dict()
    return data


async def start_activity(engine, item_id):
    item = plan_item(engine, item_id)
    if item.completed or item.metadata.get('execution'):
        execution = item.metadata.get('execution')
        if not item.completed and execution and execution['kind'] == 'review':
            notion = engine._get_exercise_target(item.category, item.target, engine.get_learning_context().get('target_language'))
            execution['review_count'] = notion.review_count
        return public_activity(engine, item)
    context = engine.get_learning_context()
    if not context.get('target_language') or not context.get('level'):
        raise ValueError('Renseignez votre langue et votre niveau dans Mon profil.')
    item.metadata['language'] = context['target_language']
    if item.activity_type == 'review' and item.category in {'vocabulary', 'grammar'}:
        notion = engine._get_exercise_target(item.category, item.target, context['target_language'])
        execution = {'kind': 'review', 'review': {'target': item.target, 'category': item.category,
            'content': notion.translation if item.category == 'vocabulary' else notion.explanation,
            'examples': notion.examples}, 'review_count': notion.review_count}
    elif item.activity_type in {'lesson', 'review'}:
        lesson = await engine.generate_lesson(item.target)
        execution = {'kind': 'lesson', 'lesson_id': lesson.id}
    else:
        category = item.category if item.category in {'vocabulary', 'grammar'} else None
        skill = item.target if item.category == 'competency' and item.target in {'vocabulary', 'grammar', 'comprehension', 'expression'} else (category or 'expression')
        exercises = await engine.generate_exercises(topic=item.target, skill=skill, count=3,
                                                    target_category=category, target=item.target if category else None)
        if not exercises:
            raise RuntimeError('Aucun exercice généré.')
        execution = {'kind': 'exercises', 'exercise_ids': [i.id for i in exercises], 'results': {}}
    item.metadata['execution'] = execution
    return public_activity(engine, item)


def finish_reading(engine, item_id, correct=None):
    item = plan_item(engine, item_id)
    execution = item.metadata.get('execution')
    if not execution or execution['kind'] not in {'lesson', 'review'}:
        raise ValueError('Commencez une activité de lecture ou de révision.')
    if item.completed:
        return public_activity(engine, item)
    if execution['kind'] == 'review':
        if correct is None:
            raise ValueError('Indiquez si vous avez retrouvé la réponse.')
        notion = engine._get_exercise_target(item.category, item.target)
        if notion.review_count != execution['review_count']:
            raise ActivityConflict('Cette notion a été révisée ailleurs. Revenez au plan pour reprendre cette activité.')
        register = engine.register_vocabulary_answer if item.category == 'vocabulary' else engine.register_grammar_answer
        register(item.target, correct)
        item.metadata['self_assessed'] = correct
        # Self-assessment is recorded separately, never presented as an exercise score.
    item.completed = True
    item.score = None
    item.completed_at = datetime.now(timezone.utc).isoformat()
    return public_activity(engine, item)


async def answer_activity(agent, item_id, exercise_id, answer):
    engine = agent.learning_engine
    item = plan_item(engine, item_id)
    execution = item.metadata.get('execution')
    if not execution or execution['kind'] != 'exercises' or exercise_id not in execution['exercise_ids']:
        raise LookupError('Exercice étranger à cette activité.')
    results = execution['results']
    if exercise_id in results:
        if results[exercise_id]['answer'] != answer:
            raise ActivityConflict('Cet exercice a déjà été corrigé. Rechargez la suite du parcours.')
        return {'evaluation': results[exercise_id]['evaluation'], 'activity': public_activity(engine, item)}
    pending = next((i for i in execution['exercise_ids'] if i not in results), None)
    if exercise_id != pending:
        raise ActivityConflict('Répondez d’abord à l’exercice en cours.')
    exercise = next(i for i in engine.exercises if i.id == exercise_id)
    result = await agent.evaluate_exercise(exercise, answer)
    results[exercise_id] = {'answer': answer, 'evaluation': result}
    if len(results) == len(execution['exercise_ids']):
        item.complete(round(sum(r['evaluation']['score'] for r in results.values()) / len(results), 2))
    return {'evaluation': result, 'activity': public_activity(engine, item)}
