import streamlit as st

from tools.ExampleQuestion import ExampleQuestion
from tools.SimpleXyzTool import SimpleXyzTool
from utils.utils import Utils


class TesisAvailableTypesTool(SimpleXyzTool):
    def __init__(self):
        super().__init__(
            name="tesis_available_types",
            description="",
            human_name="Ver acciones disponibles en ClearNet",
            human_description="Por ejemplo, tomar vacaciones",
            example_questions=[
                ExampleQuestion(
                    label="Alta de tipos en ClearNet",
                    prompt="Dime qué puedo dar de alta en Tesis",
                    icon="🌐",
                )
            ],
        )

    def run(self, prompt: str) -> dict:
        return {"available_types": st.session_state.api.get_tesis_types()}

    def text(self, data: dict) -> str:
        tipos = [f"**{t['name']}**" for t in data["available_types"]]
        tipos = Utils.join_spanish(tipos)
        res = f"En ClearNet puedes dar de alta: {tipos}."
        return res
