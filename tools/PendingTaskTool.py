import os
from datetime import datetime
from uuid import uuid4

import streamlit as st
from pandas import DataFrame
from pydantic import BaseModel

from personSelector import autocomplete
from tools.XyzTool import XyzTool
from ui.grid import grid


class PendingTaskInput(BaseModel):
    task_id: str


class PendingTaskTool(XyzTool):
    input: PendingTaskInput

    def __init__(self):
        super().__init__(
            name="pending_task",
            description="Finds and displays a pending task by its id (an UUID).",
            human_name="Mostrar tarea pendiente",
            human_description="Muestra una tarea y permite tomar una decisión sobre ella.",
            schema=PendingTaskInput,
        )

    def run(self, prompt: str) -> dict:
        task_id = self.input.task_id
        options = st.session_state.api.get_task_options(task_id)
        task = self._get_task_by_id(task_id)
        metadata = st.session_state.api.get_metadata_from_task(task)
        concept, basedata = st.session_state.api.get_concept_from_task(task)
        historial = st.session_state.api.get_historial_from_task(task)
        link = task["externalLinkDs"]

        return {
            "task": task,
            "options": options,
            "metadata": metadata,
            "concept": concept,
            "basedata": basedata,
            "historial": historial,
            "link": link,
        }

    def text(self, data: dict) -> str:
        task = data["task"]
        tarea_ds = task["taskDs"]
        # ejecucion_id = task["EJECUCION_ID"]
        # FIXME: recuperar etapa_DS
        etapa_ds = "TODO ETAPA DS"
        # etapa_ds = task["ETAPA_DS"]
        processDs = task["processDs"]

        res = f"**Tarea '{tarea_ds}'**\n\n"
        # res += f"- **ID de tarea**: {ejecucion_id}\n"
        res += f"- **Etapa**: {etapa_ds}\n"
        res += f"- **Proceso**: {processDs}\n"
        return res

    def render(self, text: str, payload: dict) -> None:
        options = payload["options"]
        metadata = payload["metadata"]
        concept = payload["concept"]
        basedata = payload["basedata"]
        historial = payload["historial"]
        link = payload["link"]

        col1, col2 = st.columns([4, 2])
        with col1:
            st.markdown(text)
        with col2:
            external_link_url = os.getenv("EXTERNAL_LINK_URL")
            assert external_link_url is not None, "EXTERNAL_LINK_URL is not set"
            full_link = external_link_url + link
            st.link_button("Abrir en GENESIS", url=full_link, icon=":material/link:")
        self._render_historial(historial)

        with st.expander("**Concepto**", icon="🏷️", expanded=True):
            self._render_concept(concept, basedata)

        with st.expander("**Toma de decisión**", icon="🔀", expanded=True):
            self._render_options(options)

        with st.expander("**Metadatos**", icon="📋"):
            grid(metadata)

    def _render_concept(self, concept: dict, basedata: list[tuple[str, str]]) -> None:
        if basedata:
            self._render_concept_properties(concept, basedata)
        else:
            st.caption("No se ha encontrado una vista predefinida para este concepto.")
            grid(concept)

    def _render_concept_properties(
        self, concept: dict, concept_view: list[tuple[str, str]]
    ) -> None:
        # Create pairs of items from the hardcoded list
        for i in range(0, len(concept_view), 2):
            cols = st.columns(2)  # Create two columns for each row
            for col, (key, name) in zip(cols, concept_view[i : i + 2]):
                with col:
                    st.caption(name)
                    value = concept.get(key, "")
                    # Check if the key ends with _DT to parse it as a date
                    if key.endswith("_DT") and value:
                        try:
                            parsed_date = datetime.strptime(value[:8], "%Y%m%d").date()
                            value = parsed_date.strftime("%d/%m/%Y")
                        except ValueError:
                            value = "Invalid date"
                    st.text(value)

    def _render_historial(self, historial: list) -> None:
        clean_historial = [
            {
                "Tarea": step["TAREA_DS"],
                "Opción": step["OPCION_DS"],
                "Estado": step["ESTADO_DS"],
                "Fecha": step["EJECUCION_TAREA_DT"],
            }
            for step in historial
        ]
        df = DataFrame(clean_historial)
        st.dataframe(df, hide_index=True, use_container_width=True)

    def _render_options(self, options: list) -> None:
        st.caption("Puedes tomar una decisión sobre esta tarea.")
        from Actions import ask_shallow_question

        n = len(options)
        columns = st.columns(n)
        for idx, decision in enumerate(options):
            with columns[idx]:
                title = decision["optionDs"]
                description = decision["optionComments"].strip()
                id = decision["optionCd"]

                reasignable = decision["reassignFl"] == 1
                transferable = decision["transferFl"] == 1

                st.button(
                    title,
                    key=f"{str(uuid4())}@{self.message_id}@take_action_{id}",
                    type="primary",
                    use_container_width=True,
                    icon=":material/start:",
                    on_click=lambda in_title, in_id, in_opt: ask_shallow_question(
                        prompt=f"Run the make task decision tool with parameters: task_id = '{in_id}', option_code = '{in_opt}' and option_name = '{in_title}'.",
                        shallow_prompt=f"Toma la decisión '{in_title}'.",
                    ),
                    args=(title, self.input.task_id, id),
                )
                if description:
                    st.caption(f"_{description.strip()}_")

                if reasignable or transferable:
                    autocomplete(
                        key=f"{self.message_id}@{str(uuid4())}@{id}@autocomplete",
                        label="Transferir o reasignar a...",
                    )

    def _get_task_by_id(self, task_id) -> dict:
        tasks = st.session_state.api.get_pending_tasks()
        for task in tasks:
            if task["taskExecutionId"] == task_id:
                return task
        assert False, f"Task with id {task_id} not found"
