from pydantic import BaseModel
from tools.XyzTool import XyzTool
from typing import Optional
import streamlit as st
from json import dumps, loads

class ResponseInput(BaseModel):
    message : Optional[str] = None
    code: Optional[str] = None 

class ResponseTool(XyzTool):
    input: ResponseInput

    def __init__(self):
        super().__init__(
            name="Respuesta Tesis/ClearNet",
            description="Herramienta para dar respuesta a peticiones de Tesis/ClearNet",
            human_name="Respuesta Tesis/ClearNet",
            human_description="Herramienta para dar respuesta a peticiones de Tesis/ClearNet",
            schema=ResponseInput,
        )

    def run(self, prompt: str) -> dict:
        return {}  

    def text(self, data: dict) -> str:
        assert self.input.message is not None
        return self.input.message

    def render(self, text: str, payload: Optional[dict]) -> None:
        st.markdown(text)
        # assert self.input.code is not None
        # print(self.input.code)
        # if self.input.code == "error":
        #     st.success( st.markdown(text) )
        # else:
        #     st.error( st.markdown(text) )