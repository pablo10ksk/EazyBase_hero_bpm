import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

import streamlit as st
from pydantic import BaseModel

from tools.ExampleQuestion import ExampleQuestion


@dataclass
class XyzTool(ABC):
    name: str
    description: str
    human_name: str
    human_description: str

    message_id: str

    example_questions: list[ExampleQuestion] = field(default_factory=list)
    schema: Optional[type[BaseModel]] = None
    input: Any = None

    def __init__(
        self,
        name: str,
        description: str,
        human_name: str,
        human_description: str,
        schema: Optional[type[BaseModel]] = None,
        example_questions: list[ExampleQuestion] = [],
    ):
        self.name = name
        self.description = description
        self.human_name = human_name
        self.human_description = human_description

        self.message_id = ""
        self.schema = schema
        self.example_questions = example_questions

        self.input = None

    @abstractmethod
    def run(self, prompt: str) -> dict:
        pass

    @abstractmethod
    def text(self, payload: dict) -> str:
        return str(payload)

    def render(self, text: str, payload: Optional[dict]) -> None:
        st.markdown(text)
        st.divider()
        st.markdown(
            "There was the following payload. If you want to hide it, extend the SimpleXyzTool class instead or define your own render method."
        )
        st.json(payload)

    def get_input_schema_description(self) -> str:
        if self.schema:
            schema = self.schema.model_json_schema()
            schema = json.dumps(schema)
            return f"This tool has the this schema: {schema}."
        return "(This tool has no schema)"

    def set_input(self, obj: Any) -> None:
        try:
            if self.schema:
                if 'prompt' in obj:
                    self.input = self.schema(**(obj["prompt"]))
                else: 
                    self.input = self.schema(**obj)
        except Exception as e:
            st.error(f"Error: {e}")
            st.error(f"Could not set input for tool {self.name}.")
            st.error(f"Input was: {obj}")
            st.error(f"Schema was: {self.schema}")
            st.error(f"Schema was: {self.schema.__dict__}")
