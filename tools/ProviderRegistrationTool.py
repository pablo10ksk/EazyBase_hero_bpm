from pydantic import BaseModel
from tools.XyzTool import XyzTool
from typing import Optional

import streamlit as st


class ProviderRegistrationInput(BaseModel):
    error: Optional[str] = None
    RAZON_SOCIAL_NEW_DS: str | None = None
    TIPO_PROVEEDOR_ID: str | None = None
    PAIS_CD: str | None = None
    CIF_CD: str | None = None


class ProviderRegistrationTool(XyzTool):
    input: ProviderRegistrationInput

    def __init__(self):
        super().__init__(
            name="provider_registration",
            description="TODO: borrar",
            human_name="Dar de alta un proveedor",
            human_description="Registra un nuevo proveedor en el sistema.",
            schema=ProviderRegistrationInput,
        )

    def run(self, prompt: str) -> dict:
        return st.session_state.api.hero_insert_object("Solicitud_Proveedor", {
            "RAZON_SOCIAL_NEW_DS": self.input.RAZON_SOCIAL_NEW_DS,
            "TIPO_PROVEEDOR_ID": self.input.TIPO_PROVEEDOR_ID,
            "PAIS_CD": self.input.PAIS_CD,
            "CIF_CD": self.input.CIF_CD,
        }, "Insert")

    def text(self, data: dict) -> str:
        if 'code' in data:
            return data['message']
        else:
            return (
                f"Se ha registrado el proveedor {self.input.RAZON_SOCIAL_NEW_DS} con número {data['result']['key']}"
                # f"con NIF {self.input.CIF_CD} en el país {self.input.PAIS_CD}."
            )

    def render(self, text: str, payload: Optional[dict]) -> None:
        if self.input.error is None:
            st.success(text)
        else:
            st.error(text)
