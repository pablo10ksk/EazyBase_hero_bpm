import os
from collections import OrderedDict
from datetime import date, datetime
from json import dumps, loads
from uuid import uuid4

import streamlit as st
from pydantic import BaseModel

from tools.ExampleQuestion import ExampleQuestion
from tools.utils import Utils
from tools.XyzTool import XyzTool


class PendingTasksInput(BaseModel):
    concept_name: str | None


class NEWPendingTasksTool(XyzTool):
    input: PendingTasksInput

    def __init__(self):
        super().__init__(
            name="pending_tasks",
            description=f"Gets the pending tasks for the current user. The user may ask about a concrete type.",
            human_name="Listar tareas pendientes",
            human_description="Muestra una lista de todas las tareas pendientes. Puedes pedir que se muestren agrupadas por fase, o solo las tareas pendientes en un rango de fechas.",
            example_questions=[
                ExampleQuestion(
                    "¿Cuáles son mis tareas pendientes?",
                    "Tareas pendientes",
                ),
                ExampleQuestion(
                    "Muéstrame las tareas de 'Bpm de Proyecto'",
                    "Tareas de tipo",
                ),
            ],
            schema=PendingTasksInput,
        )

    def run(self, prompt: str) -> dict:
        concept_name = self.input.concept_name
        tasks = st.session_state.api.get_pending_tasks()
        is_ok = True
        all_concepts = self._get_all_concepts_set(tasks)

        if concept_name is not None:
            if concept_name in all_concepts:
                tasks = self._filter_tasks_by_concept(tasks, concept_name)
            else:
                tasks = []
                is_ok = False

        last_basedata = None
        for task in tasks:
            task["concept"], basedata = st.session_state.api.get_concept_from_task(task)
            task["metadata"] = st.session_state.api.get_metadata_from_task(task)
            if basedata:
                last_basedata = basedata

        if (
            concept_name is not None
            and last_basedata is not None
            and len(last_basedata) > 0
        ):
            concept_keys = last_basedata

        else:
            concept_keys = []
        concept_keys.extend(
            [
                ("TAREA_DS", "Nombre de la tarea"),
                ("currTask", "Nombre de tarea actual"),
                ("currPhase", "Nombre de fase actual"),
                ("DATE", "Fecha de alta de la tarea"),
            ]
        )
        tasks, filter = self._filter_tasks_by_filters(
            concept_name, tasks, concept_keys, prompt
        )

        return {
            "tasks": tasks,
            "is_ok": is_ok,
            "all_concepts": all_concepts,
            "concept_name": concept_name,
            "filter": filter,
            "concept_keys": concept_keys,
        }

    def _filter_tasks_by_filters(
        self,
        concept_name: str | None,
        tasks: list[dict],
        concept_keys: list[tuple[str, str]],
        prompt: str,
    ) -> tuple[list[dict], dict]:
        today = date.today().isoformat()
        concepts_description = ""
        for key, value in concept_keys:
            concepts_description += f"- **{key}**: {value}\n"
        router_prompt = f"""
        We are within a tool that shows pending tasks. The user has made the following question:
        -------
        {prompt}
        -------

        We already know that the user is asking for pending tasks (DO NOT add filters for 'pending' or 'active' nor anything like that!!!). The user may also ask for tasks (tareas) of a certain type (BPM de Factura Recibida, BPM de <...>). Also ignore those! Now we want to extract the filters that the user has specified. The available filters are:
        ----
        {concepts_description}
        ----

        No filter is mandatory. Only use as keys the bolded fields without any changes.
            
        Return a json object with the filters that the user wants to apply. For example (keys may not correspond):
        
        """

        router_prompt += dumps(
            {
                "IMPORTEBENEFICIOPREV_NM": [
                    {"op": ">=", "value": "1000"},
                    {"op": "<=", "value": "2000"},
                ],
                "IBPME_RESP_ACTUAL_DS": [{"op": "contains", "value": "Grupo"}],
                "IBPME_RESP_ACTUAL_CD": [{"op": "eq", "value": "GRP@1@"}],
                "DATE": [
                    {"op": "<=", "value": "2022-12-31"},
                ],
            }
        )

        router_prompt += f"""\n\nThat is, for the fields that you want to filter, provide a list of operations and values under "op" and "value". The only values for "op" are: ">=", "<=", "contains", and "eq". There are no more operations. Do not use 'eq' for dates; use >= and/or <=. For "value", always fill in strings. 
        
        Regarding dates, for reference, today is {today}. Write the dates in the same format. Do not wrap the answer within ``` marks. Go!"""

        filter = st.session_state.client.regular_call_with_prompt_without_history(
            router_prompt
        )
        try:
            print(filter)
            filter = loads(filter)
        except:
            filter = {}

        for task in tasks:
            task = {
                **task,
                **task["concept"],
                **task["metadata"],
            }
            del task["concept"]
            del task["metadata"]

        tasks = [self._parse_task(task) for task in tasks]

        # del every operation whose value is concept_name
        if concept_name is not None:
            for key, operations in filter.items():
                for current_op in operations:
                    if current_op["value"].strip() == concept_name.strip():
                        operations.remove(current_op)

        # If the field name ends with dt (insensitive), try to convert to date
        # If it ends with nm (insensitive), try to convert to number
        for key, operations in filter.items():
            for current_op in operations:
                op = current_op["op"]
                value = current_op["value"]
                try:
                    current_op["value"] = Utils.try_parse_date(value)
                    if op == ">=":
                        current_op["value"] = datetime.combine(
                            current_op["value"], datetime.min.time()
                        )
                    if op == "<=":
                        current_op["value"] = datetime.combine(
                            current_op["value"], datetime.max.time()
                        )
                except:
                    pass
                if key.lower().endswith("nm"):
                    try:
                        current_op["value"] = float(value)
                    except:
                        pass
        res = []
        for task in tasks:
            if self._apply_filters_to_task(task, filter):
                res.append(task)
        return res, filter

    # tries to parse all values as dates or floats
    def _parse_task(self, task: dict) -> dict:
        res = {}
        for key, value in task.items():
            try:
                res[key] = Utils.try_parse_date(value)
            except:
                try:
                    res[key] = float(value)
                except:
                    res[key] = value
        return res

    def _apply_filters_to_task(self, task: dict, filter: dict) -> bool:
        for key, operations in filter.items():
            for current_op in operations:
                op = current_op["op"]
                value = current_op["value"]
                if not self._apply_operation_to_task(task, key, op, value):
                    return False
        return True

    def _apply_operation_to_task(
        self, task: dict, key: str, op: str, value: str
    ) -> bool:
        try:
            match op:
                case ">=":
                    return task[key] >= value
                case "<=":
                    return task[key] <= value
                case "contains":
                    return value.lower() in task[key].lower()
                case "eq":
                    return self._compare(task[key], value)
                case _:
                    return False
        except:
            return True

    def _compare(self, s1: str, s2: str):
        return (
            isinstance(s1, str)
            and isinstance(s2, str)
            and s1.lower().strip() == s2.lower().strip()
        )

    def _filter_tasks_by_concept(
        self, all_tasks: list[dict], concept_name: str
    ) -> list[dict]:
        # Filter tasks
        tasks = []
        for task in all_tasks:
            if self._compare(task["PROCESO_DS"], concept_name):
                tasks.append(task)

        return tasks

    def text(self, data: dict) -> str:
        tasks = data["tasks"]
        all_concepts = data["all_concepts"]
        is_ok = data["is_ok"]
        concept_name = data["concept_name"]
        all_concepts_bold = [f"**{concept}**" for concept in all_concepts]
        all_concepts_bold = self._join_spanish(all_concepts_bold)

        if not is_ok:
            res = f"No hay tareas pendientes de tipo '{concept_name}'.\n\n"
            res += f"Los tipos disponibles son: {all_concepts_bold}."
            return res

        tipo_parte = f" de tipo {concept_name}" if concept_name else ""

        match len(tasks):
            case 0:
                return f"No tienes tareas pendientes{tipo_parte}."
            case 1:
                return f"Tienes **1** tarea pendiente{tipo_parte}."
            case _:
                return f"Tienes **{len(tasks)}** tareas pendientes{tipo_parte}."

    def render(self, text: str, payload: dict) -> None:
        tasks = payload["tasks"]
        all_concepts = payload["all_concepts"]
        is_ok = payload["is_ok"]
        concept_name = payload["concept_name"]
        filter = payload["filter"]
        concept_keys = payload["concept_keys"]

        explained_filter = self._explain_filter(filter, concept_keys)

        if is_ok:
            st.markdown(text)
            if explained_filter != "":
                st.info(explained_filter)
            n = len(tasks)
            if n > 0:
                st.caption(
                    "Clica en las tareas para abrirlas en el chat o en los enlaces para abrirlas en GENESIS."
                )

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
                            with cols[col_idx]:
                                self._display_task(id, name, link)
        else:
            st.error(text)

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

    def _group_tasks_by_date(self, tasks: list) -> dict[str, list]:
        # Sort tasks by descending date
        tasks.sort(key=lambda x: x["DATE"], reverse=True)

        # Group tasks by date
        res = OrderedDict()
        for task in tasks:
            d = task["DATE"].date()
            date_str = d.strftime("%Y-%m-%d")
            if date_str not in res:
                res[date_str] = []
            res[date_str].append(task)

        # Inside each date, sort by datetime
        for d, tasks_in_date in res.items():
            tasks_in_date.sort(key=lambda x: x["DATE"])

        return res

    def _explain_filter(self, filter: dict, concept_keys: list[tuple[str, str]]) -> str:
        def get_description_key_from_code(code: str) -> str:
            for key, value in concept_keys:
                if key == code:
                    return value
            return code

        res = ""
        for key, operations in filter.items():
            if len(operations) == 0:
                continue
            # res += f"**{key}**: "
            res += f"**{get_description_key_from_code(key)}**: "
            ops = []
            for operation in operations:
                op = operation["op"]
                if op == "eq":
                    op = "="
                value = operation["value"]
                # check if the value is a date
                if isinstance(value, date):
                    value = value.strftime("%Y-%m-%d")
                ops.append(f"{op} {value}")
            # res += ", ".join(ops)
            res += self._join_spanish(ops)
            res += ";\n"
        if res != "":
            return "Filtros aplicados: " + res
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

    def _get_all_concepts_set(self, tasks: list[dict]) -> set[str]:
        res = set()
        for task in tasks:
            res.add(task["PROCESO_DS"])
        return res
