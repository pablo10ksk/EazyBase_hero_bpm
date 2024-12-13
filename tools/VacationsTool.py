from uuid import uuid4

import streamlit as st

from tools.XyzTool import XyzTool


class VacationsTool(XyzTool):
    def __init__(self):
        super().__init__(
            name="vacations",
            description="Show the vacation periods of the current user.",
            human_name="Vacaciones",
            human_description="Muestra los periodos de vacaciones.",
        )

    def run(self, prompt: str) -> dict:
        return st.session_state.api.do_keen_magic()

    def text(self, data: dict) -> str:
        return ""

    def render(self, text: str, payload: dict) -> None:
        form_id = self.message_id
        keys = []  # List to store keys for all inputs

        with st.form(form_id):
            for input in payload["data"]:
                type = input["controltype"]
                field = input["tipodescri"]
                title = input["title"]

                id = f"{form_id}@{field}"
                keys.append(id)  # Store the key

                match type:
                    case "f":
                        st.date_input(title, value=None, key=id)
                    case "notype":
                        pass
                    case _:
                        st.text_input(title, key=id)

            submitted = st.form_submit_button("Enviar formulario")

        if submitted:
            st.write("### Form Data:")
            for key in keys:
                st.write(f"{key}: {st.session_state.get(key)}")
