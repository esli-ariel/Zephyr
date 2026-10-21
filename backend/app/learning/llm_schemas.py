"""Contrats stricts des réponses structurées du modèle, sans coercition silencieuse."""
import json
from typing import Annotated, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

Text = Annotated[str, Field(min_length=1, max_length=5000)]
Level = Literal["A1", "A2", "B1", "B2", "C1", "C2"]
Skill = Literal["vocabulary", "grammar", "comprehension", "expression", "translation"]


class StrictResponse(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", str_strip_whitespace=True)


class EvaluationResponse(StrictResponse):
    score: int = Field(ge=0, le=100)
    correct: bool
    feedback: Text
    errors: list[Text] = Field(max_length=50)
    strengths: list[Text] = Field(max_length=50)
    weak_points: list[Text] = Field(max_length=50)


class ProfileResponse(StrictResponse):
    name: Text | None
    target_language: Text | None
    level: Level | None
    goals: list[Text] = Field(max_length=50)


class LessonSectionResponse(StrictResponse):
    title: Text
    content: Text
    section_type: Literal["introduction", "vocabulary", "grammar", "examples", "practice", "summary"]


class LessonResponse(StrictResponse):
    title: Text
    language: Text
    level: Level
    topic: Text
    objectives: list[Text] = Field(max_length=50)
    sections: list[LessonSectionResponse] = Field(min_length=1, max_length=30)


class GeneratedExercise(StrictResponse):
    id: Text | None = None  # Toléré pour les anciens prompts, remplacé côté serveur.
    exercise_type: Literal["multiple_choice", "fill_blank", "translation", "writing", "reading"]
    question: Text
    level: Level
    skill: Skill
    options: list[Text] = Field(default_factory=list, max_length=20)
    expected_answer: Text | None = None
    difficulty: int = Field(ge=1, le=5)

    @model_validator(mode="after")
    def validate_closed_exercise(self):
        if self.exercise_type in {"multiple_choice", "fill_blank"} and self.expected_answer is None:
            raise ValueError("Réponse attendue obligatoire pour un exercice fermé.")
        if self.exercise_type == "multiple_choice":
            options = [option.casefold() for option in self.options]
            if len(options) < 3 or len(set(options)) != len(options):
                raise ValueError("Un QCM exige au moins trois options distinctes.")
            if self.expected_answer.casefold() not in options:
                raise ValueError("La réponse attendue doit être une option du QCM.")
        return self


class ExerciseBatch(StrictResponse):
    exercises: list[GeneratedExercise] = Field(min_length=1, max_length=20)


ResponseType = TypeVar("ResponseType", bound=StrictResponse)


def parse_response(model: type[ResponseType], response: str) -> dict:
    try:
        def unique_fields(pairs):
            data = {}
            for key, value in pairs:
                if key in data:
                    raise ValueError("Champ JSON dupliqué.")
                data[key] = value
            return data

        data = json.loads(response, object_pairs_hook=unique_fields)
        return model.model_validate(data).model_dump()
    except (ValidationError, ValueError, TypeError, RecursionError) as exc:
        # Ne pas recopier la réponse du fournisseur dans l'erreur exposée à l'API.
        raise RuntimeError("Réponse IA invalide : le format attendu n'est pas respecté.") from exc
