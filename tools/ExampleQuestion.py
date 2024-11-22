from dataclasses import dataclass
from typing import Optional


@dataclass
class ExampleQuestion:
    prompt: str
    label: str
    icon: Optional[str] = None
