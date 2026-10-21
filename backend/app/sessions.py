"""Une instance de l'agent et de l'évaluation pour chaque apprenant."""
import asyncio
from dataclasses import dataclass, field
from uuid import uuid4

from app.agent.zephyr import ZephyrAgent
from app.learning.adaptive_assessment import AdaptiveAssessment
from app.persistence import StateStore, capture_state, restore_state


@dataclass
class LearnerSession:
    learner_id: str
    agent: ZephyrAgent = field(default_factory=ZephyrAgent)
    assessment: AdaptiveAssessment = field(default_factory=AdaptiveAssessment)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)


class LearnerSessions:
    def __init__(self, store: StateStore | None = None):
        self.store = store
        self.sessions: dict[str, LearnerSession] = {}

    def create(self) -> LearnerSession:
        session = LearnerSession(learner_id=str(uuid4()))
        # Publier l'identifiant seulement après la sauvegarde de son état initial.
        if self.store is not None:
            self.store.save(capture_state(session.agent, session.assessment), session.learner_id)
        self.sessions[session.learner_id] = session
        return session

    def get(self, learner_id: str) -> LearnerSession | None:
        if learner_id in self.sessions:
            return self.sessions[learner_id]
        snapshot = self.store.load(learner_id) if self.store is not None else None
        if snapshot is None:
            return None
        session = LearnerSession(learner_id=learner_id)
        restore_state(snapshot, session.agent, session.assessment)
        self.sessions[learner_id] = session
        return session
