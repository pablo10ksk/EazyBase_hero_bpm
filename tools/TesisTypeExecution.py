import re
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
            human_name="Ejecutar una acción en ClearNet",
            human_description="Por ejemplo, dar de alta un periodo de vacaciones",
            schema=TesisTypeExecutionInput,
        )

    def run(self, prompt: str) -> dict:
        # is_error = self.input.error_data == 1
        is_error = self.input.error_data == 1 or (
            self.input.missing_data is not None
            and self.input.missing_data.strip() != ""
        )
        fields = st.session_state.api.do_keen_magic(self.input.type_cd)

        if is_error:
            res = self.input.missing_data
        else:
            estructura = TesisConcept.get_mapping(fields["data"])
            print(estructura)
            titulo = "TITULO_DS = 'Test'" if 'TITULO_DS' not in self.input.args else "TITULO_DS = '" + self.input.args['TITULO_DS'] + "'."
            # Quiero dar de alta un anticipo de nómina de 800 euros en a coruña en el departamento general
            new_prompt = f"""
            El usuario ha mandado este formulario de esta manera
            -----
            {str(self.input.args)}
            -----

            Sin embargo la estructura que me hace falta es 
            -----
            {titulo}
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
        nombre = TesisConcept.get_name(self.input.type_cd)

        if is_error:
            fields = TesisConcept.display(nombre, data["fields"]["data"])
            return f"**Me faltan estos datos:** {res}\n\n{fields}"
        else:
            # res = "Se ha insertado el contenido. Ref: '1333127', Cod Externo: ''"
            # return res
            match = re.search(r"(\d+)", res)
            if match:
                ref_num = match.group(1)
                text = f"Se ha creado un contenido de **{nombre}** en ClearNet con número de referencia **{ref_num}**. Puede consultarlo en la plataforma."
                return text
            else:
                return "Error"
           
