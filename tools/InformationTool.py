from pydantic import BaseModel
from tools.XyzTool import XyzTool
from typing import Optional
import streamlit as st

class InformationInput(BaseModel):
    information : Optional[str] = None
    help : Optional[str] = None

class InformationTool(XyzTool):
    input: InformationInput

    def __init__(self):
        super().__init__(
            name="information_tool",
            description="View information",
            human_name="Informacion",
            human_description="Armar la informacion de una alta de contenido de Tesis/ClearNet",
            schema=InformationInput,
        )

    def run(self, prompt: str) -> dict:
        return {}  

    def text(self, data: dict) -> str:
        assert self.input.information is not None
        return self.input.information

    def render(self, text: str, payload: Optional[dict]) -> None:
        st.info(text)
        if self.input.help is not None:
           st.markdown(self.input.help) 
        # st.success( st.markdown(text) )
        # st.error( st.markdown(text) )