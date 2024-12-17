from typing import Literal

import streamlit as st
from pydantic import BaseModel

from tools.SimpleXyzTool import SimpleXyzTool
from utils.TesisConcept import TesisConcept


class TesisTypeExecutionInput(BaseModel):
    type_cd: str
    missing_data: str | None = None
    error_data: Literal[0, 1]
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
        is_error = self.input.error_data == 1
        fields = st.session_state.api.do_keen_magic(self.input.type_cd)

        if is_error:
            res = self.input.missing_data
        else:
            estructura = TesisConcept.get_mapping(fields["data"])
            print(estructura)
            # Quiero dar de alta un anticipo de nómina de 800 euros en a coruña en el departamento general
            new_prompt = f"""
            El usuario ha mandado este formulario de esta manera
            -----
            {str(self.input.args)}
            -----

            Sin embargo la estructura que me hace falta es 
            -----
            {estructura}
            """
            corrected_args = st.session_state.agent._run_router(
                "tesis_structure_execution",
                new_prompt,
                [],
            )
            print("Corrected args:", corrected_args)
            corrected_args = corrected_args["return_execution"]["response"]
            res = st.session_state.api.insert_magic(
                tipo_num=self.input.type_cd,
                args=corrected_args,
            )

        return {
            "is_error": is_error,
            "data": res,
            "fields": fields if is_error else None,
        }

    def text(self, data: dict) -> str:
        is_error = data["is_error"]
        res = data["data"]

        if is_error:
            nombre = (
                "Vacaciones" if self.input.type_cd == "115" else "Anticipo de nómina"
            )
            fields = TesisConcept.display(nombre, data["fields"]["data"])
            return f"{res}\n\n{fields}"
        else:
            return str(res)
