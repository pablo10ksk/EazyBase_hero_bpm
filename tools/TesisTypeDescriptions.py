import streamlit as st
from pydantic import BaseModel

from tools.ExampleQuestion import ExampleQuestion
from tools.SimpleXyzTool import SimpleXyzTool
from tools.utils import Utils


class TesisTypeDescriptionsInput(BaseModel):
    type_name: str


class TesisTypeDescriptionsTool(SimpleXyzTool):
    input: TesisTypeDescriptionsInput

    def __init__(self):
        super().__init__(
            name="tesis_type_description",
            description="",
            human_name="Saber más sobre una acción en Tesis",
            human_description="Por ejemplo, saber qué hace falta para dar de alta un periodo de vacaciones",
            example_questions=[
                ExampleQuestion(
                    label="Campos vacaciones",
                    prompt="Quiero saber más sobre la acción de alta de vacaciones en 'Tesis'",
                    icon="🏖️",
                )
            ],
            schema=TesisTypeDescriptionsInput,
        )

    def run(self, prompt: str) -> dict:
        return st.session_state.api.do_keen_magic()

    def text(self, data: dict) -> str:
        tipo = "vacaciones"
        res = f"Puedes dar de alta **{tipo}** en Tesis:\n"
        for field in data["data"]:
            res += f"- **{field['title']}**"
            if field["options"]:
                options = field["options"]
                options = [f":gray[{opt}]" for opt in options]
                if len(options) > 6:
                    res += "\n\n"
                    res += "\t| | | | |\n"
                    res += "\t|---|---|---|---|\n"
                    num_rows = (len(options) + 3) // 4
                    for i in range(num_rows):
                        row_options = options[i * 4 : (i + 1) * 4]
                        res += "\t| " + " | ".join(row_options) + " |\n"
                else:
                    res += ", con posibles valores: " + Utils.join_spanish(options)
            res += "\n"
        print(res)
        return res
