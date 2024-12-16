import streamlit as st

from tools.ExampleQuestion import ExampleQuestion
from tools.SimpleXyzTool import SimpleXyzTool
from tools.utils import Utils


class TesisAvailableTypesTool(SimpleXyzTool):
    def __init__(self):
        super().__init__(
            name="tesis_available_types",
            description="",
            human_name="Ver acciones disponibles en Tesis",
            human_description="Por ejemplo, tomar vacaciones",
            example_questions=[
                ExampleQuestion(
                    label="Alta de tipos en Tesis",
                    prompt="Dime qué tipos están disponibles en Tesis",
                    icon="🌐",
                )
            ],
        )

    def run(self, prompt: str) -> dict:
        return {"available_types": st.session_state.api.get_tesis_types()}

    def text(self, data: dict) -> str:
        tipos = [f"**{t['name']}**" for t in data["available_types"]]
        tipos = Utils.join_spanish(tipos)
        res = f"En Tesis puedes dar de alta: {tipos}."
        return res
