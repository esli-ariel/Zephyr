from dataclasses import dataclass, field


@dataclass
class LessonSection:
    """
    Une section d'une leçon.
    """

    title: str
    content: str
    section_type: str


@dataclass
class Lesson:
    """
    Représente une leçon pédagogique de Zéphyr.
    """

    id: str
    title: str
    language: str
    level: str
    topic: str

    objectives: list[str] = field(
        default_factory=list
    )

    sections: list[LessonSection] = field(
        default_factory=list
    )

    def add_section(
        self,
        title: str,
        content: str,
        section_type: str,
    ) -> None:
        self.sections.append(
            LessonSection(
                title=title,
                content=content,
                section_type=section_type,
            )
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "language": self.language,
            "level": self.level,
            "topic": self.topic,
            "objectives": self.objectives,
            "sections": [
                {
                    "title": section.title,
                    "content": section.content,
                    "section_type": section.section_type,
                }
                for section in self.sections
            ],
        }