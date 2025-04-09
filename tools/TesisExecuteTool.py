import re 
from typing import Literal
from pydantic import BaseModel
from tools.XyzTool import XyzTool
from tools.ResponseTool import ResponseTool
from typing import Optional
from uuid import uuid4
from json import dumps, loads
import streamlit as st

class TesisExecutionInput(BaseModel):
    error: Optional[str] = None
    validation: Optional[str] = None
    template: Optional[str] = None
    type_cd: Optional[str] = None
    args: Optional[dict] = None
    message_error: Optional[str] = None

class TesisExecutionTool(XyzTool):
    input: TesisExecutionInput

    def __init__(self):
        super().__init__(
            name="tesis2_execute",
            description="Versión 2 de la ejecución de una petición a tesis/CrearNet",
            human_name="Ejecución de una petición a tesis/CrearNet",
            human_description="ejecución de una petición a tesis/CrearNet.",
            schema=TesisExecutionInput,
        )

    def run(self, prompt: str) -> dict:
        return {}  

    def text(self, data: dict) -> str:
        if self.input.error is not None:
            return self.input.error
        else:
            assert self.input.validation is not None
            return self.input.validation

    def render(self, text: str, payload: Optional[dict]) -> None:
        if self.input.error is None:
            st.markdown(text)
            str_args = dumps(self.input.args)
            assert str_args is not None
            button_key = f"{self.message_id}@str_args_tesis_tool@boton"
            disabled = st.session_state.buttons_confirm.get(button_key, False)
            st.button(
                "Confirmar",
                key=button_key,
                type="primary",
                icon=":material/check:",
                on_click=self.process_info,
                args=(str_args, button_key),
                disabled=disabled,
            )
        else:
            st.error(text)

    def process_info(self, str_args: str, button_key:str) -> None:
        from Actions import execute_tool_programmatically

        args = loads(str_args)
        # Solicitud insertar solicitud
        result = st.session_state.api.insert_magic(
            tipo_num=self.input.type_cd,
            args=args,
        )

        # Procesar resultado
        match = re.search(r"(\d+)", result)
        print(match)
        if match:
            ref_num = match.group(1)
            # Actualizar la respuesta con el template de salida
            assert self.input.template is not None
            text = self.input.template.replace("ref_num", ref_num)
            execute_tool_programmatically(ResponseTool(), {"type": "ok", "message": text})
            st.session_state.buttons_confirm[button_key] = True
        else:
            assert self.input.message_error is not None
            execute_tool_programmatically(ResponseTool(), {"type": "error", "message": self.input.message_error})