import requests

from Api import get_endpoint
from tools.SimpleXyzTool import SimpleXyzTool


class GetAllPendingTasksPhasedTool(SimpleXyzTool):
    def __init__(self):
        super().__init__(
            name="get_all_pending_tasks_phased",
            description="Gets all pending tasks BY PHASES for the current user.",
            human_name="Pending tasks by phases",
            human_description="Displays a list of all pending tasks grouped by phase",
        )

    def run(self, prompt: str) -> dict:
        url = get_endpoint("GetPendingTasksPhased")
        payload = {
            "token": self.global_payload.token,
            "USR_CD": self.global_payload.userId,
        }
        headers = {"Content-Type": "application/json"}

        response = requests.get(url, headers=headers, json=payload)
        res_obj = response.json()
        return {
            "obj": res_obj,
        }

    def text(self, data: dict) -> str:
        res = ""
        obj = data["obj"]
        for key, value in obj.items():
            res += f"# {key}\n"
            description = value["PROCESO_DS"]
            res += f"{description}\n"

            for etapa in value["ETAPAS_MAP"]:
                res += f"## {etapa['ETAPA_DS']}\n"
                for tarea in etapa["TAREA_LST"]:
                    res += f"- {tarea['TAREA_DS']}\n"

        return res
