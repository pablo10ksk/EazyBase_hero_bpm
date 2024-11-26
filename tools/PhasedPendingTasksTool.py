import streamlit as st

from tools.XyzTool import XyzTool


class PhasedPendingTasksTool(XyzTool):

    def __init__(self):
        super().__init__(
            name="phased_pending_tasks",
            description="Displays pending tasks by phases. ONLY use this tool if the user asks by phase (fase) or aggregated (agregadas) or agrupadas.",
            human_name="Listar tareas pendientes por fase",
            human_description="Muestra las tareas pendientes por fases.",
        )

    def run(self, prompt: str) -> dict:
        tasks = st.session_state.api.get_all_tasks_phased()
        num_all, num_today = self._get_nums(tasks)

        return {
            "tasks": tasks,
            "num_all": num_all,
            "num_today": num_today,
        }

    def _get_nums(self, tasks) -> tuple[int, int]:
        num_all = 0
        num_today = 0

        for root_value in tasks.values():
            etapas = root_value["ETAPAS_MAP"]
            for etapa in etapas:
                listado = etapa["TAREA_LST"]
                for l in listado:
                    num_all += int(l["TOTAL_PENDING_NM"])
                    num_today += int(l["PENDING_TODAY_NM"])
        return num_all, num_today

    def text(self, data: dict) -> str:
        all = data["num_all"]
        today = data["num_today"]
        match all:
            case 0:
                return "No tienes tareas pendientes."
            case 1:
                return f"Tienes **1** tarea pendiente (**{today}** para hoy)."
            case _:
                return f"Tienes **{all}** tareas pendientes (**{today}** para hoy)."

    def render(self, text: str, payload: dict) -> None:
        tasks = payload["tasks"]
        st.markdown(text)

        task_items = list(tasks.values())
        for i in range(0, len(task_items), 2):
            cols = st.columns(2)

            for col, root_value in zip(cols, task_items[i : i + 2]):
                with col:
                    name = root_value["PROCESO_DS"]
                    icon = ":material/package_2:"
                    with st.expander(f"**{name}**", icon=icon):
                        etapas = root_value["ETAPAS_MAP"]

                        table = " Nombre | Hoy | Total"
                        table += "\n --- | --- | ---"
                        for etapa in etapas:
                            etapa_name = etapa["ETAPA_DS"]
                            listado = etapa["TAREA_LST"]
                            for l in listado:
                                nombre_l = l["NAME_TAREA_DS"]
                                today_l = l["PENDING_TODAY_NM"]
                                total_l = l["TOTAL_PENDING_NM"]
                                table += f"\n:gray[{etapa_name}] / {nombre_l} | {today_l} | {total_l}"
                        st.markdown(table)
