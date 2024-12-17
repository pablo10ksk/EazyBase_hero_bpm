from dataclasses import dataclass, field
from typing import Optional

from Message import Message


@dataclass
class Historial:
    HISTORIAL_CUTOFF = 20
    _messages: list[Message] = field(default_factory=list)

    def __post_init__(self):
        # self._messages.append(
        #     Message(
        #         role="assistant",
        #         text="Soy un asistente llamado Juan Pedro que resuelve tareas pendientes.",
        #     )
        # )
        pass

    def add_message(self, m: Message) -> None:
        self._messages.append(m)

    def get_last_message(self) -> Optional[Message]:
        return self._messages[-1]

    def get_last_messages_except_last(self) -> list[dict]:
        res = self._messages[-self.HISTORIAL_CUTOFF : -1]
        return [{"role": m.role, "content": str(m.text)} for m in res]
