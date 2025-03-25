import os
from collections import OrderedDict
from copy import deepcopy
from datetime import date, datetime
from typing import Any
from uuid import uuid4

import streamlit as st
from pydantic import BaseModel

from tools.ExampleQuestion import ExampleQuestion
from tools.XyzTool import XyzTool


class Filters(BaseModel):
    # CLIENTE_DS: str | None = None
    # INSTITUCION_DS: str | None = None
    # OPORTUNIDAD_DS: str | None = None
    # CODIGOPEDIDO_CD: str | None = None
    # TIPOPROYECTO_DS: str | None = None
    # ADMINISTRADOR_DS: str | None = None
    # IBPME_SITUACION_PROC_DS: str | None = None
    # IMPORTEPREVISTO_NM_min: int | None = None
    # IMPORTEPREVISTO_NM_max: int | None = None
    # IMPORTE_NM_min: int | None = None
    # IMPORTE_NM_max: int | None = None
    # PEDIDO_DS: str | None = None
    # DEAL_CD: str | None = None
    # IMPORTEESTIMADO_NM_min: int | None = None
    # IMPORTEESTIMADO_NM_max: int | None = None
    # RESUMEN_DS: str | None = None
    # ESTADO_DS: str | None = None
    # TAREA_DT_min: date | None = None
    # TAREA_DT_max: date | None = None

    # inicio_DT_min: date | None = None
    # inicio_DT_max: date | None = None
    proc_CS: str | None = None
    version_CD: str | None = None
    currTask_DS: str | None = None
    currPhase_DS: str | None = None

    TAREA_CD: str | None = None
    TAREA_DS: str | None = None
    ETAPA_CD: str | None = None
    ETAPA_DS: str | None = None
    PROCESO_DS: str | None = None
    TAREA_DT_min: date | None = None
    TAREA_DT_max: date | None = None


class PendingTasksInput(BaseModel):
    aggregated: bool = False
    filters: Filters


class OldPendingTasksTool(XyzTool):
    input: PendingTasksInput

    def __init__(self):
        today = date.today()
        super().__init__(
            name="pending_tasks",
            description=f"Gets the pending tasks for the current user. If 'aggregated' is set to true, tasks will be presented grouped by phase. You have a series of filters which you may fill in or not. As a reference, today is {today.isoformat()}. When filling in the json, do put the keywords as is (do not translate them).",
            # If the user asks about a specific task name or type (e.g., holidays, lanzamiento, autorizar pago...), put them into the keywords field.
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
            schema=PendingTasksInput,
        )

    def run(self, prompt: str) -> dict:
        is_aggregated = self.input.aggregated
        filters = self.input.filters
        tasks = (
            st.session_state.api.get_all_tasks_phased()
            if is_aggregated
            else self._filter_tasks(st.session_state.api.get_all_tasks(), filters)
        )
        return {
            "phased": is_aggregated,
            "tasks": tasks,
            "filters": filters,
        }

    def text(self, data: dict) -> str:
        return ""

    def render(self, text: str, payload: dict) -> None:
        is_aggregated = payload["phased"]
        tasks = payload["tasks"]
        filters = payload["filters"]
        if is_aggregated:
            self._render_aggregated_tasks(tasks)
        else:
            self._render_tasks(tasks, filters)

    def _render_tasks(
        self,
        tasks: list,
        filters: Filters,
    ) -> None:
        n = len(tasks)
        number_tasks_explanation = self._get_number_tasks_explanation(n)
        filters_explanation = self._get_filters_explanation(filters)
        explanation = f"{number_tasks_explanation} {filters_explanation}"
        st.markdown(f"{explanation.strip()}.")

        if n > 0:
            st.caption(
                "Clica en las tareas para abrirlas en el chat o en los enlaces para abrirlas en GENESIS."
            )

        # for task in tasks:
        #     id = task["EJECUCION_ID"]
        #     name = task["TAREA_DS"]
        #     link = task["externalLinkDs"]
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
                        link = task["externalLinkDs"]
                        with cols[col_idx]:
                            self._display_task(id, name, link)

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

    def _get_filters_explanation(self, filters: Filters) -> str:
        f = filters.model_dump()
        alguno_relleno = any(x is not None for x in f.values())

        if not alguno_relleno:
            return ""

        res = " con los siguientes filtros: "
        textos = []
        for key, value in f.items():
            if value is None:
                continue
            if key.endswith("_min") or key.endswith("_max"):
                is_min = key.endswith("_min")
                is_max = key.endswith("_max")
                key = key[:-4]
            else:
                is_min = False
                is_max = False

            if key.endswith("_NM"):
                if is_min:
                    textos.append(f"{key} mayor o igual a {value}")
                elif is_max:
                    textos.append(f"{key} menor o igual a {value}")
                else:
                    textos.append(f"{key} igual a {value}")
            elif key.endswith("_DT"):
                if is_min:
                    textos.append(f"{key} mayor o igual a {value}")
                elif is_max:
                    textos.append(f"{key} menor o igual a {value}")
                else:
                    textos.append(f"{key} igual a {value}")
            else:
                textos.append(f"{key} igualTEXTO a '{value}'")

        res += self._join_spanish(textos)
        return res

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

    def _filter_tasks(self, tasks_: list, filters: Filters) -> list:
        """matching_tasks = []
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
        """

        # The strategy is the following:
        # deep copy the task lists.
        # Now, iterate throught all the fields of the task. If the field ends with _DT, replace the value of the field with fromisoformat.

        tasks = deepcopy(tasks_)
        for task in tasks:
            for key, asked_value in task.items():
                if key.endswith("_DT"):
                    if asked_value is not None and asked_value != "":
                        task[key] = datetime.fromisoformat(asked_value)

        # Expand the fields of the metadata of the task to the task itself
        for task in tasks:
            task = {**task, **task["metadata"]}
            del task["metadata"]

        filters_items = filters.model_dump()
        res = filter(lambda task: self._is_good_task(task, filters_items), tasks)
        return list(res)

    def _is_good_task(self, task: dict[str, Any], fields: dict[str, Any]) -> bool:
        # For each field in Filters, we check if the field is None. If it is not, we check if the field is in the task, removing _min or _max if necessary.
        # Depending on the type of the field, we check if the value is in the range or if it is equal to the value.
        # If the field is empty, ignore it
        for key, value in fields.items():
            if value is None:
                continue
            if key.endswith("_min") or key.endswith("_max"):
                is_min = key.endswith("_min")
                is_max = key.endswith("_max")
                key = key[:-4]
            else:
                is_min = False
                is_max = False
            if key not in task:
                return False
            task_value = task[key]
            if is_min:
                value = datetime.combine(value, datetime.min.time())
                if task_value < value:
                    return False
            elif is_max:
                value = datetime.combine(value, datetime.max.time())
                if task_value > value:
                    return False
            else:
                if task_value != value:
                    return False
        return True

    def _get_number_tasks_explanation(self, n: int) -> str:
        match n:
            case 0:
                return "No tienes tareas pendientes"
            case 1:
                return "Tienes **1** tarea pendiente"
            case _:
                return f"Tienes **{n}** tareas pendientes"

    def _display_task(self, task_id: str, name: str, link: str) -> None:
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

    def _view_task_callback(self, task_id: str, name: str) -> None:
        from Actions import ask_shallow_question

        ask_shallow_question(
            prompt=f"View the task whose id is '{task_id}'",
            shallow_prompt=f"Ver tarea '{name}'",
        )
