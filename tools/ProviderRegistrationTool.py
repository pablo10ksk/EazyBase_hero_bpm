from pydantic import BaseModel
from tools.XyzTool import XyzTool
from tools.ResponseTool import ResponseTool
from typing import Optional
from uuid import uuid4
from json import dumps, loads
import streamlit as st

class ProviderRegistrationInput(BaseModel):
    error: Optional[str] = None
    validation: Optional[str] = None
    RAZON_SOCIAL_NEW_DS: str | None = None
    TIPO_PROVEEDOR_ID: str | None = None
    PAIS_CD: str | None = None
    CIF_CD: str | None = None
    TELEFONO_CD: str | None = None
    PERSONA_CONTACTO_DS: str | None = None
    DIRECCION_EMAIL_CD: str | None = None
    message_error: Optional[str] = None
    help: Optional[str] = None

class ProviderRegistrationTool(XyzTool):
    input: ProviderRegistrationInput

    def __init__(self):
        super().__init__(
            name="provider_registration",
            description="Alta de Proveedor",
            human_name="Dar de alta un proveedor",
            human_description="Registra un nuevo proveedor en el sistema.",
            schema=ProviderRegistrationInput,
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
        # st.success(text + str(payload))
        if self.input.error is None:
            st.markdown(text)
            provider = dumps({
                "RAZON_SOCIAL_NEW_DS": self.input.RAZON_SOCIAL_NEW_DS,
                "TIPO_PROVEEDOR_ID": self.input.TIPO_PROVEEDOR_ID,
                "PAIS_CD": self.input.PAIS_CD,
                "CIF_CD": self.input.CIF_CD,
                "TELEFONO_CD": self.input.TELEFONO_CD,
                "PERSONA_CONTACTO_DS": self.input.PERSONA_CONTACTO_DS,
                "DIRECCION_EMAIL_CD": self.input.DIRECCION_EMAIL_CD,
            })
            assert provider is not None
            button_key = f"{self.message_id}@provider_registration_tool@boton"
            disabled = st.session_state.buttons_confirm.get(button_key, False)
            st.button(
                "Confirmar",
                key=button_key,
                type="primary",
                icon=":material/check:",
                on_click=self.insert_object,
                args=(provider, button_key),
                disabled=disabled,
            )
            if self.input.help is not None:
                st.markdown(self.input.help)
        else:
            st.error(text)

    def insert_object(self, provider: str, button_key:str) -> None:
        data = loads(provider)
        response = st.session_state.api.hero_insert_object("Solicitud_Proveedor", data, "OnInsert")

        from Actions import execute_tool_programmatically
        execute_tool_programmatically(ResponseTool(), {"type": "ok", "message": f"Se ha dado de alta el Proveedor '**{data['RAZON_SOCIAL_NEW_DS']}**' con número **{response['result']['key']}**. Puede consultarlo en la plataforma."})
        st.session_state.buttons_confirm[button_key] = True