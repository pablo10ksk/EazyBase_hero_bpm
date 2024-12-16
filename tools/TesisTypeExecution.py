import streamlit as st
from pydantic import BaseModel

from tools.SimpleXyzTool import SimpleXyzTool


class TesisTypeExecutionInput(BaseModel):
    type_cd: str
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
        res = st.session_state.api.insert_magic(
            tipo_num=115,
            args=self.input.args,
        )
        return res

    def text(self, data: dict) -> str:
        return data["data"]
