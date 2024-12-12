import streamlit as st

from tools.XyzTool import XyzTool


class PhasedPendingTasksTool(XyzTool):

    def __init__(self):
        super().__init__(
            name="phased_pending_tasks",
            description="Displays pending tasks by phases. ONLY use this tool if the user asks by phase (fase) or aggregated (agregadas) or agrupadas and WITH NO filters.",
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
            etapas = root_value["stageLst"]
            for etapa in etapas:
                listado = etapa["taskLst"]
                for l in listado:
                    num_all += int(l["totalPendingNm"])
                    num_today += int(l["pendingTodayNm"])
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
                    sum_totales = 0
                    etapas = root_value["stageLst"]
                    for etapa in etapas:
                        listado = etapa["taskLst"]
                        for l in listado:
                            sum_totales += int(l["totalPendingNm"])

                    name = root_value["processDs"]
                    icon = ":material/package_2:"
                    with st.expander(f"**{name}** :gray[({sum_totales})]", icon=icon):
                        table = " Nombre | Hoy | Total"
                        table += "\n --- | --- | ---"
                        for etapa in etapas:
                            etapa_name = etapa["stageDs"]
                            listado = etapa["taskLst"]
                            for l in listado:
                                nombre_l = l["taskNameDs"]
                                today_l = l["pendingTodayNm"]
                                total_l = l["totalPendingNm"]
                                table += f"\n:gray[{etapa_name}] / {nombre_l} | {today_l} | {total_l}"
                        st.markdown(table)
