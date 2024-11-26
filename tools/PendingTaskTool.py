from datetime import datetime
from typing import Optional
from uuid import uuid4

import requests
import streamlit as st
from pandas import DataFrame
from pydantic import BaseModel

from Api import get_endpoint
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
        options = self._get_task_options(task_id)
        task = self._get_task_by_id(task_id)
        metadata = self._get_metadata_from_task(task)
        concept, basedata = self._get_concept_from_task(task)
        historial = self._get_historial_from_task(task)
        return {
            "task": task,
            "options": options,
            "metadata": metadata,
            "concept": concept,
            "basedata": basedata,
            "historial": historial,
        }

    def text(self, data: dict) -> str:
        task = data["task"]
        tarea_ds = task["TAREA_DS"]
        # ejecucion_id = task["EJECUCION_ID"]
        etapa_ds = task["ETAPA_DS"]
        proceso_ds = task["PROCESO_DS"]

        res = f"**Tarea '{tarea_ds}'**\n\n"
        # res += f"- **ID de tarea**: {ejecucion_id}\n"
        res += f"- **Etapa**: {etapa_ds}\n"
        res += f"- **Proceso**: {proceso_ds}\n"
        return res

    def render(self, text: str, payload: dict) -> None:
        options = payload["options"]
        metadata = payload["metadata"]
        concept = payload["concept"]
        basedata = payload["basedata"]
        historial = payload["historial"]

        st.markdown(text)

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

                # TODO: call the MakeTaskDecisionTool
                st.button(
                    title,
                    key=f"{str(uuid4())}@{self.message_id}@take_action_{id}",
                    type="primary",
                    use_container_width=True,
                    icon=":material/start:",
                    on_click=lambda in_title, in_id, in_opt: ask_shallow_question(
                        prompt=f"Run the make task decision tool with parameters: task_id = '{in_id}' and option_code = '{in_opt}'",
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

    def _get_task_options(self, task_id: str) -> dict:
        url = get_endpoint("GetTaskOptionsAdvance")
        payload = {
            "token": self.global_payload.token,
            "taskExecId": task_id,
        }
        headers = {"Content-Type": "application/json"}
        res = requests.get(url, headers=headers, json=payload)
        return res.json()

    def _get_all_tasks(self) -> list:
        url = get_endpoint("GetPendingTasks")
        payload = {
            "token": self.global_payload.token,
            "userId": self.global_payload.userId,
            "userTasksFl": "true",
            "groupsTasksFl": "true",
            "pendingTaskId": "",
            "locatorDs": "",
        }
        headers = {"Content-Type": "application/json"}
        return requests.get(url, headers=headers, json=payload).json()

    def _get_task_by_id(self, task_id) -> dict:
        tasks = self._get_all_tasks()
        for task in tasks:
            if task["EJECUCION_ID"] == task_id:
                return task
        assert False, f"Task with id {task_id} not found"

    def _get_concept_from_task(self, task: dict) -> tuple[dict, list[tuple[str, str]]]:
        try:
            conceptobase_cd = task["CONCEPTOBASE_CD"]
            conceptobase_id = task["CONCEPTOBASE_ID"]

            url = get_endpoint("getConceptFromCptId")
            payload = {
                "token": self.global_payload.token,
                "mapData": {
                    "CONCEPTOBASE_CD": conceptobase_cd,
                    "CONCEPTOBASE_ID": conceptobase_id,
                },
            }
            headers = {"Content-Type": "application/json"}
            res = requests.get(url, headers=headers, json=payload).json()
            res = res["retunobj_"]
            concept = res["attributes"]
            basedata = list(res["basedata"].items())

            return concept, basedata
        except:
            return {}, []

    def _get_metadata_from_task(self, task: dict):
        conceptobase_cd = task["CONCEPTOBASE_CD"]
        conceptobase_id = task["CONCEPTOBASE_ID"]

        url = get_endpoint("GetMetadataProcess")
        payload = {
            "token": self.global_payload.token,
            "cptoBaseCd": conceptobase_cd,
            "cptoBaseId": conceptobase_id,
        }
        headers = {"Content-Type": "application/json"}
        res = requests.get(url, headers=headers, json=payload)
        return res.json()[0]

    def _get_historial_from_task(self, task: dict) -> list:
        conceptobase_cd = task["CONCEPTOBASE_CD"]
        conceptobase_id = task["CONCEPTOBASE_ID"]
        proceso_id = task["procId"]

        url = get_endpoint("GetHistExecBPM")
        payload = {
            "token": self.global_payload.token,
            "cptoCd": conceptobase_cd,
            "cptoId": conceptobase_id,
            "procId": proceso_id,
        }
        headers = {"Content-Type": "application/json"}
        res = requests.get(url, headers=headers, json=payload)
        return res.json()
