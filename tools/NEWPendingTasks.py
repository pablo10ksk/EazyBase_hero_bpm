import os
from collections import OrderedDict
from datetime import date, datetime, timedelta
from uuid import uuid4

import requests
import streamlit as st
from pydantic import BaseModel

from Api import get_endpoint
from tools.ExampleQuestion import ExampleQuestion
from tools.XyzTool import XyzTool


class NEWPendingTasksInput(BaseModel):
    aggregated: bool = False
    minimum_date: date | None = date.today() - timedelta(days=30)
    maximum_date: date | None = None
    keywords: list[str] = []


class NEWPendingTasks(XyzTool):
    input: NEWPendingTasksInput

    def __init__(self):
        today = date.today()
        super().__init__(
            name="pending_tasks",
            description=f"Gets *ALL* the pending tasks for the current user. If 'aggregated' is set to true, tasks will be presented grouped by phase. You can specify in which range of dates you want them with minimum_date..maximum_date. You can leave either of them empty. By default, the minimum date is 30 days ago. As a reference, today is {today.isoformat()}. If the user asks about a specific task name or type (e.g., holidays, lanzamiento, autorizar pago...), put them into the keywords field. Do not translate the keywords.",
            human_name="Listar tareas pendientes",
            human_description="Muestra una lista de todas las tareas pendientes. Puedes pedir que se muestren agrupadas por fase, o solo las tareas pendientes en un rango de fechas.",
            example_questions=[
                ExampleQuestion(
                    "¿Cuáles son mis tareas pendientes?",
                    "Tareas pendientes",
                ),
                ExampleQuestion(
                    "Muéstrame las tareas pendientes agregadas",
                    "Tareas agregadas",
                ),
            ],
            schema=NEWPendingTasksInput,
        )

    def run(self, prompt: str) -> dict:
        is_aggregated = self.input.aggregated
        min_d = self.input.minimum_date
        max_d = self.input.maximum_date
        keywords = self.input.keywords
        tasks = (
            self._get_all_tasks_phased()
            if is_aggregated
            else self._get_all_tasks(min_d, max_d, keywords)
        )
        return {
            "phased": is_aggregated,
            "tasks": tasks,
            "min_date": min_d,
            "max_date": max_d,
            "keywords": keywords,
            "associatedMetadata": (
                {
                    task["EJECUCION_ID"]: self._get_metadata_from_task(task)
                    for task in tasks
                }
                if not is_aggregated
                else {}
            ),
        }

    def text(self, data: dict) -> str:
        return ""

    def render(self, text: str, payload: dict) -> None:
        is_aggregated = payload["phased"]
        tasks = payload["tasks"]
        min_d = payload["min_date"]
        max_d = payload["max_date"]
        keywords = payload["keywords"]
        associated_metadata = payload["associatedMetadata"]
        if is_aggregated:
            self._render_aggregated_tasks(tasks)
        else:
            self._render_tasks(tasks, min_d, max_d, keywords, associated_metadata)

    def _render_tasks(
        self,
        tasks: list,
        min_d: date | None,
        max_d: date | None,
        keywords: list[str],
        associated_metadata: dict,
    ) -> None:
        n = len(tasks)
        number_tasks_explanation = self._get_number_tasks_explanation(n)
        date_range_explanation = self._get_date_range_explanation(min_d, max_d)
        keywords_explanation = self._get_keywords_explanation(keywords)
        explanation = f"{number_tasks_explanation} {date_range_explanation} {keywords_explanation}"
        st.markdown(f"{explanation.strip()}.")

        if n > 0:
            st.caption(
                "Clica en las tareas para abrirlas en el chat o en los enlaces para abrirlas en GENESIS."
            )

        # for task in tasks:
        #     id = task["EJECUCION_ID"]
        #     name = task["TAREA_DS"]
        #     link = task["EXTERNAL_LINK_DS"]
        #     date = task["TAREA_DT"]
        #     self._display_task(id, name, link, date)

        grouped_tasks = self._group_tasks_by_date(tasks)
        for date, tasks in grouped_tasks.items():
            st.markdown(f"**{date}**")
            num_columns = 3
            rows = (len(tasks) + num_columns - 1) // num_columns
            for row_idx in range(rows):
                cols = st.columns(num_columns)
                for col_idx in range(num_columns):
                    task_idx = row_idx * num_columns + col_idx
                    if task_idx < len(tasks):
                        task = tasks[task_idx]
                        id = task["EJECUCION_ID"]
                        name = task["TAREA_DS"]
                        link = task["EXTERNAL_LINK_DS"]
                        metadata = associated_metadata.get(id)
                        assert metadata is not None, f"Metadata not found for task {id}"
                        with cols[col_idx]:
                            self._display_task(id, name, link, metadata)

    def _get_keywords_explanation(self, keywords: list[str]) -> str:
        if keywords:
            k_str = self._join_spanish([f"'{k}'" for k in keywords])
            if len(keywords) == 1:
                return f"que contengan el término {k_str}"
            else:
                return f" que contengan los términos {k_str}"
        return ""

    def _join_spanish(self, l: list[str]) -> str:
        """Une una lista con comas excepto el último que va con un 'y'"""
        if len(l) == 0:
            return ""
        elif len(l) == 1:
            return l[0]
        elif len(l) == 2:
            return l[0] + " y " + l[1]
        else:
            return ", ".join(l[:-1]) + " y " + l[-1]

    def _get_date_range_explanation(
        self, min_d: date | None, max_d: date | None
    ) -> str:
        if min_d is None and max_d is None:
            return ""
        elif min_d is None and max_d is not None:
            return f"hasta el {max_d.isoformat()}"
        elif max_d is None and min_d is not None:
            return f"desde el {min_d.isoformat()}"
        assert min_d is not None and max_d is not None
        return f"entre el {min_d.isoformat()} y el {max_d.isoformat()}"

    def _group_tasks_by_date(self, tasks: list) -> dict[str, list]:
        # Sort tasks by descending date
        tasks.sort(key=lambda x: x["DATE"], reverse=True)

        # Group tasks by date
        res = OrderedDict()
        for task in tasks:
            date = task["DATE"].date()
            date_str = date.strftime("%Y-%m-%d")
            if date_str not in res:
                res[date_str] = []
            res[date_str].append(task)

        # Inside each date, sort by datetime
        for date, tasks_in_date in res.items():
            tasks_in_date.sort(key=lambda x: x["DATE"])

        return res

    def _render_aggregated_tasks(self, data: dict) -> None:
        st.markdown("Tienes las siguientes tareas agrupadas por fase:")
        for root_key, root_value in data.items():
            name = root_value["PROCESO_DS"]
            # full_name = f"{name} ({root_key})"
            st.markdown(f"**{name}**")
            etapas = root_value["ETAPAS_MAP"]

            # for etapa in etapas:
            #     etapa_name = etapa["ETAPA_DS"]
            #     with st.expander(etapa_name):
            #         table = "Nombre | Pending | Total"
            #         table += "\n--- | --- | ---"
            #         listado = etapa["TAREA_LST"]
            #         for l in listado:
            #             nombre_l = l["NAME_TAREA_DS"]
            #             today_l = l["PENDING_TODAY_NM"]
            #             total_l = l["TOTAL_PENDING_NM"]
            #             table += f"\n{nombre_l} | {today_l} | {total_l}"
            #         st.markdown(table)

            table = "Etapa | Nombre | Hoy | Total"
            table += "\n--- | --- | --- | ---"
            for etapa in etapas:
                etapa_name = etapa["ETAPA_DS"]
                listado = etapa["TAREA_LST"]
                for l in listado:
                    nombre_l = l["NAME_TAREA_DS"]
                    today_l = l["PENDING_TODAY_NM"]
                    total_l = l["TOTAL_PENDING_NM"]
                    table += f"\n{etapa_name} | {nombre_l} | {today_l} | {total_l}"
            st.markdown(table)

    def _get_all_tasks(
        self, min_d: date | None, max_d: date | None, keywords: list[str]
    ) -> list:
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
        tasks = requests.get(url, headers=headers, json=payload).json()
        matching_tasks = []
        for task in tasks:
            # Parse the task date
            task["DATE"] = datetime.fromisoformat(task["TAREA_DT"])

            # Adjust min_d and max_d to be datetime objects
            if min_d is not None:
                min_d_datetime = datetime.combine(
                    min_d, datetime.min.time()
                )  # Start of the day
            else:
                min_d_datetime = None

            if max_d is not None:
                max_d_datetime = datetime.combine(
                    max_d, datetime.max.time()
                )  # End of the day
            else:
                max_d_datetime = None

            # Compare dates
            if min_d_datetime is not None and task["DATE"] < min_d_datetime:
                continue
            if max_d_datetime is not None and task["DATE"] > max_d_datetime:
                continue

            num_matching_keywords = 0
            # pon keywords en minusculas
            keywords = [keyword.lower() for keyword in keywords]
            # Busca en TAREA_CD, TAREA_DS, ETAPA_CD, ETAPA_DS, PROCESO_DS
            string_keys = ["TAREA_CD", "TAREA_DS", "ETAPA_CD", "ETAPA_DS", "PROCESO_DS"]
            haystack = " ".join([str(task[key]) for key in string_keys]).lower()
            for keyword in keywords:
                if keyword in haystack:
                    num_matching_keywords += 1
            if len(keywords) > 0 and num_matching_keywords == 0:
                continue

            matching_tasks.append(task)
        return matching_tasks

    def _get_all_tasks_phased(self) -> list:
        url = get_endpoint("GetPendingTasksPhased")
        payload = {
            "token": self.global_payload.token,
            "USR_CD": self.global_payload.userId,
        }
        headers = {"Content-Type": "application/json"}
        return requests.get(url, headers=headers, json=payload).json()

    def _get_number_tasks_explanation(self, n: int) -> str:
        match n:
            case 0:
                return "No tienes tareas pendientes"
            case 1:
                return "Tienes **1** tarea pendiente"
            case _:
                return f"Tienes **{n}** tareas pendientes"

    def _display_task(self, task_id: str, name: str, link: str, metadata: dict) -> None:
        external_link_url = os.getenv("EXTERNAL_LINK_URL")
        assert external_link_url is not None, "EXTERNAL_LINK_URL is not set"
        full_link = external_link_url + link

        col1, col2 = st.columns([1, 5])
        uuid = uuid4()
        with col1:
            st.markdown(f"[:material/link:]({full_link})")
        with col2:
            st.button(
                key=f"{uuid}@{self.message_id}@prompt_view_task_{task_id}",
                label=name,
                on_click=self._view_task_callback,
                args=(task_id, name),
                use_container_width=True,
            )
            st.json(metadata)

    def _view_task_callback(self, task_id: str, name: str) -> None:
        from Actions import ask_shallow_question

        ask_shallow_question(
            prompt=f"View the task whose id is '{task_id}'",
            shallow_prompt=f"Ver tarea '{name}'",
        )

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
