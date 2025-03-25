import streamlit as st
from pydantic import BaseModel

from tools.ExampleQuestion import ExampleQuestion
from tools.SimpleXyzTool import SimpleXyzTool
from utils.TesisConcept import TesisConcept


class TesisTypeDescriptionsInput(BaseModel):
    type_name: str


class TesisTypeDescriptionsTool(SimpleXyzTool):
    input: TesisTypeDescriptionsInput

    def __init__(self):
        super().__init__(
            name="tesis_type_description",
            description="",
            human_name="Saber más sobre una acción en ClearNet",
            human_description="Por ejemplo, saber qué hace falta para dar de alta un periodo de vacaciones",
            example_questions=[
                ExampleQuestion(
                    label="Pedir vacaciones",
                    prompt="Explícame qué valores tengo que aportar para dar de alta Vacaciones en Tesis",
                    icon="🏖️",
                )
            ],
            schema=TesisTypeDescriptionsInput,
        )

    def run(self, prompt: str) -> dict:
        # Vacaciones
        if "ciones" in self.input.type_name:
            num = 115
            tipo = "Vacaciones"
        elif "nticipo" in self.input.type_name:
            num = 120
            tipo = "Anticipo de nómina"
        elif "astos" in self.input.type_name:
            num = 331
            tipo = "Nota de Gastos"
        else:
            num = 122
            tipo = "Autorización de Viaje Internacional"
        res = st.session_state.api.do_keen_magic(num)
        print(res)
        res["tipo"] = tipo
        return res

    def text(self, data: dict) -> str:
        return TesisConcept.display(data["tipo"], data["data"])
