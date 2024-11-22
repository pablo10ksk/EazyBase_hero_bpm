from dataclasses import dataclass


@dataclass
class GlobalPayload:
    token: str
    userId: str
