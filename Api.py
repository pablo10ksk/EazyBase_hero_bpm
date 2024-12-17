import os
import re
from urllib.parse import urljoin

import requests

from Login import Login
from utils.utils import Utils


class Api:
    def __init__(self, login: Login):
        self.login = login
        self.headers = {"Content-Type": "application/json"}

    def get_all_tasks_phased(self) -> dict:
        res = requests.get(
            url=self._get_endpoint("GetPendingTasksPhased_v2"),
            json={
                "token": self._get_token(),
                "USR_CD": self._get_user_code(),
            },
            headers=self.headers,
        )
        return res.json()

    def get_pending_tasks(self) -> dict:
        tasks = requests.get(
            url=self._get_endpoint("GetPendingTasks_v2"),
            json={
                "token": self._get_token(),
                "USR_CD": self._get_user_code(),
                "userTasksFl": "true",
                "groupsTasksFl": "true",
                "pendingTaskId": "",
                "locatorDs": "",
                "mapData": {"addcpt": True},
            },
            headers=self.headers,
        ).json()
        for task in tasks:
            task["DATE"] = Utils.try_parse_date(task["taskDt"])
        return tasks

    def get_pending_task(self, taskId: str) -> dict:
        tasks = requests.get(
            url=self._get_endpoint("GetPendingTasks_v2"),
            json={
                "token": self._get_token(),
                "USR_CD": self._get_user_code(),
                "userTasksFl": "true",
                "groupsTasksFl": "true",
                "pendingTaskId": taskId,
                "locatorDs": "",
                "mapData": {"addcpt": True},
            },
            headers=self.headers,
        ).json()
        for task in tasks:
            task["DATE"] = Utils.try_parse_date(task["taskDt"])
        return tasks

    def get_reassign_names(self, input: str):
        if not input.strip():
            return []
        return requests.get(
            url=self._get_endpoint("getUserReassignTask"),
            json={
                "token": self._get_token(),
                "filterDs": input,
            },
            headers=self.headers,
        ).json()

    def make_decision(self, task_id: str, option_code: str):
        response = requests.get(
            url=self._get_endpoint_simple("MakeDecision"),
            json={
                "token": self._get_token(),
                "ejecTareaId": task_id,
                "opcionCd": option_code,
            },
            headers=self.headers,
        )

        return {
            "ok": response.ok,
            "data": response.json(),
        }

    def get_metadata_from_task(self, task: dict):
        res = requests.get(
            url=self._get_endpoint("GetMetadataProcess"),
            json={
                "token": self._get_token(),
                "cptoBaseCd": task["baseConceptCd"],
                "cptoBaseId": task["baseConceptId"],
            },
            headers=self.headers,
        )
        # FIXME:
        return {
            "inicio_DT": "",
            "proc_CS": "",
            "version_CD": "",
            "currTask_DS": "",
            "currPhase_DS": "",
        }
        res = res.json()[0]

        return {
            "inicio_DT": res["inicioDt"],
            "proc_CS": res["proc"],
            "version_CD": res["versionCd"],
            "currTask_DS": res["currTask"],
            "currPhase_DS": res["currPhase"],
        }

    def get_concept_from_task(self, task: dict) -> tuple[dict, list[tuple[str, str]]]:
        try:
            res = requests.get(
                url=self._get_endpoint("getConceptFromCptId"),
                json={
                    "token": self._get_token(),
                    "mapData": {
                        "CONCEPTOBASE_CD": task["baseConceptCd"],
                        "CONCEPTOBASE_ID": task["baseConceptId"],
                    },
                },
                headers=self.headers,
            ).json()
            res = res["retunobj_"]
            concept = res["attributes"]
            basedata = list(res["basedata"].items())  # type: list[tuple[str, str]]

            # FIXME: volver a poner todos
            # basedata is of type (key, value)
            # we want to remove provisionally all the keys that end with _DT
            basedata = [x for x in basedata if not x[0].endswith("_DT")]

            return concept, basedata
        except:
            return {}, []

    def get_historial_from_task(self, task: dict) -> list:
        res = requests.get(
            url=self._get_endpoint_simple("GetHistExecBPM"),
            json={
                "token": self._get_token(),
                "cptoCd": task["baseConceptCd"],
                "cptoId": task["baseConceptId"],
                "procId": task["procId"],
            },
            headers=self.headers,
        )
        return res.json()

    def get_task_options(self, task_id: str) -> dict:
        res = requests.get(
            url=self._get_endpoint_simple("GetTaskOptionsAdvance"),
            json={
                "token": self._get_token(),
                "taskExecId": task_id,
            },
            headers=self.headers,
        )
        return res.json()

    def do_keen_magic(self, tipo_num: int):
        res = requests.get(
            url=self._get_endpoint("doKeenMagic"),
            json={
                "token": self._get_token(),
                "mapData": {
                    "ACTION": "getcontentcreate",
                    "TIPO_CD": tipo_num,
                },
            },
            headers=self.headers,
        )
        return res.json()

    def insert_magic(self, tipo_num: int, args: dict):
        descri = args
        descri["TITULO_DS"] = "Test"

        # Itera sobre todos los key, y si el valor
        # tiene la forma AAAA-MM-DD, transfórmalo a AAAAMMDDHHMMSS
        for key in descri:
            value = descri[key]
            if re.match(r"\d{4}-\d{2}-\d{2}", value):
                descri[key] = value.replace("-", "") + "000000"

        res = requests.get(
            url=self._get_endpoint("doKeenMagic"),
            json={
                "token": self._get_token(),
                "mapData": {
                    "ACTION": "insertcatalog",
                    "TIPO_CD": tipo_num,  # 115
                    "TAG_CD": (
                        "SOLIC_VACACIONES" if tipo_num == 115 else "ANTICIPO_NOMINA"
                    ),  # "SOLIC_VACACIONES",
                    "DESCRI": descri,
                    # {
                    #     # "INICIO_DT": "20241215000000",
                    #     # "FIN_DT": "20241216000000",
                    #     # "MOTIVO_CD": "Vacaciones",
                    #     "TITULO_DS": "Test",
                    # },
                },
            },
            headers=self.headers,
        )
        return res.json()["data"]

    def get_tesis_types(self):
        return [
            {"name": "Vacaciones"},
            {"name": "Anticipo de nómina"},
        ]

    def _get_endpoint(self, slug: str):
        endpoint = os.getenv("API_ENDPOINT")
        assert endpoint is not None, "API_ENDPOINT is not set"
        return urljoin(endpoint + "ibpmev2/", slug)

    def _get_endpoint_simple(self, slug: str):
        endpoint = os.getenv("API_ENDPOINT")
        assert endpoint is not None, "API_ENDPOINT is not set"
        return urljoin(endpoint + "ibpme/", slug)

    def _get_token(self):
        return self.login.get_token()

    def _get_user_code(self):
        return self.login.get_user_id()
