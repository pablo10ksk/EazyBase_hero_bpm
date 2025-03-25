from dataclasses import dataclass


@dataclass(frozen=True)
class Chatbot:
    name: str
    description: str
    company: str
    emoji: str = ""

    @property
    def fancy_name(self) -> str:
        if self.emoji:
            return f"{self.emoji} {self.name}"
        return self.name

    @property
    def title_name(self) -> str:
        return f"{self.name} | {self.company}"


chatbot = Chatbot(
    name="Tareas pendientes",
    description="Gestiona tus tareas pendientes.",
    company="UGROUND",
    emoji="📝",
)
