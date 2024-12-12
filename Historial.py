from typing import Optional

from Message import Message


class Historial:
    HISTORIAL_CUTOFF = 20

    def __init__(self):
        self._messages: list[Message] = []

    def add_message(self, m: Message) -> None:
        self._messages.append(m)

    def get_last_messages(self) -> list[Message]:
        return self._messages[-self.HISTORIAL_CUTOFF :]

    def get_last_messages_except_last(self) -> list[Message]:
        return self._messages[-self.HISTORIAL_CUTOFF : -1]

    def get_last_message(self) -> Optional[Message]:
        return self._messages[-1]
