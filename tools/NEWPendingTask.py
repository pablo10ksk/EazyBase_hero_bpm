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


class NEWPendingTaskInput(BaseModel):
    task_id: str


class NEWPendingTask(XyzTool):
    input: NEWPendingTaskInput

    def __init__(self):
        super().__init__(
            name="pending_task",
            description="Finds and displays a pending task by its id (an UUID).",
            human_name="Mostrar tarea pendiente",
            human_description="Muestra una tarea y permite tomar una decisión sobre ella.",
            schema=NEWPendingTaskInput,
        )

    def run(self, prompt: str) -> dict:
        task_id = self.input.task_id
        options = self._get_task_options(task_id)
        task = self._get_task_by_id(task_id)
        metadata = self._get_metadata_from_task(task)
        concept = self._get_concept_from_task(task)
        historial = self._get_historial_from_task(task)
        return {
            "task": task,
            "options": options,
            "metadata": metadata,
            "concept": concept,
            "historial": historial,
        }

    def text(self, data: dict) -> str:
        return ""

    def render(self, text: str, payload: dict) -> None:
        task = payload["task"]
        options = payload["options"]
        metadata = payload["metadata"]
        concept = payload["concept"]
        historial = payload["historial"]

        self._render_task(task)

        self._render_historial(historial)

        with st.expander("**Toma de decisión**", icon="🔀", expanded=True):
            self._render_options(options)

        with st.expander("Metadatos", icon="📋"):
            grid(metadata)

        proc = metadata["proc"]
        with st.expander("Propiedades del concepto", icon="🏷️"):
            self._render_concept(concept, proc)

    def _render_concept(self, concept: dict, proc: str) -> None:
        # Get the first 5 keys of the concept
        keys = list(concept.keys())

        # # Render only the first 5 keys
        # concept = {key: concept[key] for key in keys}
        # grid(concept)

        hardcoded = self._get_hardcoded_concept_view(proc)
        if hardcoded:
            self._render_concept_properties(concept, hardcoded)
        else:
            st.caption("No se ha encontrado una vista predefinida para este concepto.")
            grid(concept)

    def _render_concept_properties(
        self, concept: dict, hardcoded: list[tuple[str, str]]
    ) -> None:
        # Create pairs of items from the hardcoded list
        for i in range(0, len(hardcoded), 2):
            cols = st.columns(2)  # Create two columns for each row
            for col, (name, key) in zip(cols, hardcoded[i : i + 2]):
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
        """[
            {
                "EJECUCION_TAREA_ID": "ZchLDB1u2AnrS/OsBYpPV89jP7eZ2fJSmC2oQBspIHamBA==",
                "EJECUCION_TAREA_DT": "2024-02-28",
                "TAREA_CD": "START",
                "TAREA_DS": "Inicio proceso",
                "ETAPA_CD": "INICIO",
                "ETAPA_DS": "Inicio",
                "COMENTARIOS_DS": "",
                "RESPONSABLE_DS": "ugadmin ",
                "OPCION_CD": "INITPROC",
                "OPCION_DS": "Init process",
                "ESTADO_CD": "EJECUTADA_OK",
                "ESTADO_DS": "Ejecutada OK",
                "ANTERIOR_ID": "",
                "FIN_DT": "2024-02-28T23:22:45",
                "TAREA_DT": "2024-02-28T23:22:45",
                "VENCIMIENTO_DT": ""
            },
            {
                "EJECUCION_TAREA_ID": "YshPV0lq3QfrF6b8VtpPUphiNL6S2KsCy3b5R04scyXyVA==",
                "EJECUCION_TAREA_DT": "2024-02-28",
                "TAREA_CD": "ITSEAZY",
                "TAREA_DS": "EazyJob :)",
                "ETAPA_CD": "CENTER",
                "ETAPA_DS": "Tarea central",
                "COMENTARIOS_DS": "",
                "RESPONSABLE_DS": "ugadmin ",
                "OPCION_CD": "",
                "OPCION_DS": "???",
                "ESTADO_CD": "PDTE_FIN",
                "ESTADO_DS": "Pendiente de finalización",
                "ANTERIOR_ID": "ZchLDB1u2AnrS/OsBYpPV89jP7eZ2fJSmC2oQBspIHamBA==",
                "FIN_DT": "",
                "TAREA_DT": "2024-02-28T23:22:45",
                "VENCIMIENTO_DT": ""
            }
        ]"""

        clean_historial = [
            {
                "Tarea": x["TAREA_DS"],
                "Opción": x["OPCION_DS"],
                "Estado": x["ESTADO_DS"],
                "Fecha": x["EJECUCION_TAREA_DT"],
            }
            for x in historial
        ]
        df = DataFrame(clean_historial)
        st.dataframe(df, hide_index=True, use_container_width=True)

    def _render_task(self, task: dict) -> None:
        tarea_ds = task["TAREA_DS"]
        ejecucion_id = task["EJECUCION_ID"]
        etapa_ds = task["ETAPA_DS"]
        proceso_ds = task["PROCESO_DS"]

        st.markdown(
            f"""
            **Tarea: {tarea_ds}**

            - **ID de tarea**: {ejecucion_id}
            - **Etapa**: {etapa_ds}
            - **Proceso**: {proceso_ds}
        """
        )

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

    def _get_concept_from_task(self, task: dict) -> dict:
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
            res = requests.get(url, headers=headers, json=payload)
            return res.json()["retunobj_"]
        except:
            return {}

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

    def _get_hardcoded_concept_view(
        self, concept_name: str
    ) -> Optional[list[tuple[str, str]]]:
        d = {
            "Bpm de Proyecto": [
                ("Cliente", "CLIENTE_DS"),
                ("Institución", "INSTITUCION_DS"),
                ("Oportunidad", "OPORTUNIDAD_DS"),
                ("Código del Proyecto", "CODIGOPEDIDO_CD"),
                ("Tipo de Proyecto", "TIPOPROYECTO_DS"),
                ("Administrador", "ADMINISTRADOR_DS"),
                ("Estado", "IBPME_SITUACION_PROC_DS"),
                ("Importe Previsto (€)", "IMPORTEPREVISTO_NM"),
                ("Importe Total (€)", "IMPORTE_NM"),
                ("Descripción breve", "PEDIDO_DS"),
            ],
            "Proceso de Oportunidades": [
                ("Nombre", "OPORTUNIDAD_DS"),
                ("Código", "DEAL_CD"),
                ("Institución", "INSTITUCION_DS"),
                ("Cliente", "CLIENTE_DS"),
                ("Importe estimado", "IMPORTEESTIMADO_NM"),
                ("Descripción breve", "RESUMEN_DS"),
                ("Estado", "ESTADO_DS"),
                ("Fecha de alta", "ALTA_DT"),
            ],
        }
        return d.get(concept_name)
