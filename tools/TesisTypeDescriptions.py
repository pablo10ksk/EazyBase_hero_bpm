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
        else:
            num = 120
            tipo = "Anticipo de nómina"
        res = st.session_state.api.do_keen_magic(num)
        res["tipo"] = tipo
        return res

    def text(self, data: dict) -> str:
        tipo = data["tipo"]
        res = f"Para dar de alta **{tipo}** en Tesis, tienes que darme estos datos:\n"
        for field in data["data"]:
            res += f"- **{field['title']}**"
            if field["options"]:
                options = field["options"]

                def clean_option(opt):
                    if "$" in opt:
                        return opt.split("$")[1]
                    return opt

                options = [clean_option(opt) for opt in options]
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
                    options_united = Utils.join_spanish(options)
                    res += f", con posibles valores: {options_united}."
            res += "\n"
        return res
