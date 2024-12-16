import streamlit as st
from pydantic import BaseModel

from tools.SimpleXyzTool import SimpleXyzTool


class TesisTypeExecutionInput(BaseModel):
    type_name: str
    args: dict


class TesisTypeExecutionTool(SimpleXyzTool):
    input: TesisTypeExecutionInput

    def __init__(self):
        super().__init__(
            name="tesis_type_execution",
            description="",
            human_name="Ejecutar una acción en Tesis",
            human_description="Por ejemplo, dar de alta un periodo de vaaciones",
            schema=TesisTypeExecutionInput,
        )

    def run(self, prompt: str) -> dict:
        return {}

    def text(self, data: dict) -> str:
        return str(self.input.model_dump())
