"""Sauvegarde atomique de l'état des apprenants."""
import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from app.learning.exercise import Exercise
from app.learning.grammar import GrammarRule
from app.learning.learner import LearnerProfile
from app.learning.lesson import Lesson
from app.learning.learning_plan import LearningPlan
from app.learning.vocabulary import VocabularyItem


class AssessmentState(BaseModel):
    assessment_id: str
    final_result: dict | None = None
    current_level: Literal["A1", "A2", "B1", "B2", "C1", "C2"]
    question_index: int = Field(ge=0)
    answers: list[dict]
    level_scores: dict[str, list[int]]
    level_question_counts: dict[str, int]
    pending_answer_index: int | None = None
    finished: bool
    stop_reason: str | None = None


class StateSnapshot(BaseModel):
    version: Literal[1] = 1
    profile: LearnerProfile
    conversation: list[dict[str, str]]
    lessons: list[Lesson]
    exercises: list[Exercise]
    vocabulary: list[VocabularyItem]
    grammar: list[GrammarRule]
    learning_plan: LearningPlan | None = None
    assessment: AssessmentState


def capture_state(agent, assessment) -> StateSnapshot:
    session = assessment.session
    return StateSnapshot.model_validate({
        "profile": agent.learner.get_profile(),
        "conversation": agent.memory.get_conversation(),
        "lessons": [item.to_dict() for item in agent.learning_engine.lessons],
        "exercises": [item.to_dict() for item in agent.learning_engine.exercises],
        "vocabulary": [item.to_dict() for item in agent.learning_engine.vocabulary.get_all_words()],
        "grammar": [item.to_dict() for item in agent.learning_engine.grammar.get_all_rules()],
        "learning_plan": agent.learning_engine.current_learning_plan,
        "assessment": {
            "assessment_id": assessment.assessment_id,
            "final_result": assessment.final_result,
            **{key: getattr(session, key) for key in (
                "current_level", "question_index", "answers", "level_scores",
                "level_question_counts", "pending_answer_index", "finished", "stop_reason",
            )},
        },
    }).model_copy(deep=True)


def restore_state(snapshot: StateSnapshot, agent, assessment) -> None:
    # Détacher les objets restaurés pour conserver le snapshot de rollback intact.
    snapshot = snapshot.model_copy(deep=True)
    agent.learner.profile = snapshot.profile
    agent.memory.short_term.messages = snapshot.conversation[-agent.memory.short_term.max_messages:]
    engine = agent.learning_engine
    engine.lessons = snapshot.lessons
    engine.exercises = snapshot.exercises
    engine.current_learning_plan = snapshot.learning_plan
    engine.vocabulary.items = {
        engine.vocabulary._normalize(item.word): item for item in snapshot.vocabulary
    }
    engine.grammar.rules = {
        engine.grammar._normalize(item.rule): item for item in snapshot.grammar
    }
    assessment.assessment_id = snapshot.assessment.assessment_id
    assessment.final_result = snapshot.assessment.final_result
    for key, value in snapshot.assessment.model_dump().items():
        if key not in {"assessment_id", "final_result"}:
            setattr(assessment.session, key, value)


LEGACY_LEARNER_ID = "00000000-0000-0000-0000-000000000001"


class StateStore:
    def __init__(self, path: str):
        self.path = Path(path).expanduser()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                "CREATE TABLE IF NOT EXISTS learner_states "
                "(learner_id TEXT PRIMARY KEY, payload TEXT NOT NULL)"
            )
            legacy = connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'app_state'"
            ).fetchone()
            if legacy:
                row = connection.execute("SELECT payload FROM app_state WHERE id = 1").fetchone()
                if row:
                    # Valider avant de migrer ; une erreur annule toute la transaction.
                    StateSnapshot.model_validate_json(row[0])
                    connection.execute(
                        "INSERT OR IGNORE INTO learner_states VALUES (?, ?)",
                        (LEGACY_LEARNER_ID, row[0]),
                    )
                connection.execute("DROP TABLE app_state")

    def load(self, learner_id: str) -> StateSnapshot | None:
        with closing(sqlite3.connect(self.path)) as connection:
            row = connection.execute(
                "SELECT payload FROM learner_states WHERE learner_id = ?", (learner_id,)
            ).fetchone()
        return StateSnapshot.model_validate_json(row[0]) if row else None

    def save(self, snapshot: StateSnapshot, learner_id: str) -> None:
        payload = json.dumps(snapshot.model_dump(mode="json"), ensure_ascii=False)
        with closing(sqlite3.connect(self.path)) as connection, connection:
            connection.execute(
                "INSERT INTO learner_states(learner_id, payload) VALUES (?, ?) "
                "ON CONFLICT(learner_id) DO UPDATE SET payload = excluded.payload",
                (learner_id, payload),
            )
