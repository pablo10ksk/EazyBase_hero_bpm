import os
from urllib.parse import urljoin

import requests

from Login import Login
from tools.utils import Utils


class Api:
    def __init__(self, login: Login):
        self.login = login
        self.headers = {"Content-Type": "application/json"}

    def get_all_tasks_phased(self) -> dict:
        return requests.get(
            url=self._get_endpoint("GetPendingTasksPhased_v2"),
            json={
                "token": self._get_token(),
                "USR_CD": self._get_user_code(),
            },
            headers=self.headers,
        ).json()

    def get_pending_tasks(self) -> dict:
        tasks = requests.get(
            url=self._get_endpoint("GetPendingTasks_v2"),
            json={
                "token": self._get_token(),
                "userId": self._get_user_code(),
                "userTasksFl": "true",
                "groupsTasksFl": "true",
                "pendingTaskId": "",
                "locatorDs": "",
                "mapData": {"addcpt": True},
            },
            headers=self.headers,
        ).json()
        for task in tasks:
            task["DATE"] = Utils.try_parse_date(task["TAREA_DT"])
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
            url=self._get_endpoint("MakeDecision"),
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
                "cptoBaseCd": task["CONCEPTOBASE_CD"],
                "cptoBaseId": task["CONCEPTOBASE_ID"],
            },
            headers=self.headers,
        )
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
                        "CONCEPTOBASE_CD": task["CONCEPTOBASE_CD"],
                        "CONCEPTOBASE_ID": task["CONCEPTOBASE_ID"],
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
            url=self._get_endpoint("GetHistExecBPM"),
            json={
                "token": self._get_token(),
                "cptoCd": task["CONCEPTOBASE_CD"],
                "cptoId": task["CONCEPTOBASE_ID"],
                "procId": task["procId"],
            },
            headers=self.headers,
        )
        return res.json()

    def get_task_options(self, task_id: str) -> dict:
        res = requests.get(
            url=self._get_endpoint("GetTaskOptionsAdvance"),
            json={
                "token": self._get_token(),
                "taskExecId": task_id,
            },
            headers=self.headers,
        )
        return res.json()

    def insert_into_kbase(self, company_owner, mapdata, metadata: dict):
        url = os.getenv("EAZYBASE_URL")
        assert url is not None, "EAZYBASE_URL is not set"

        response = requests.post(
            url=url,
            json={
                "token": self._get_token(),
                "mapData": {
                    "clientowner_cd": company_owner,
                    "companyowner_id": company_owner,
                    "kbasefather_cd": mapdata["kbasefather_cd"],
                    "hasprocess_fl": "0",
                    "kbasename_cd": mapdata["kbasename_cd"],
                    "kbasedescription_ds": mapdata["kbasedescription_ds"],
                    "kbasename_ds": mapdata["kbasename_ds"],
                    "hasoutcome_cd": "0",
                    "hasrequirements_cd": "0",
                    "process_id": "",
                    "alert_to_ds": "",
                    "metadata_": metadata,
                },
            },
            headers=self.headers,
        ).json()
        return response["insertObject"]

    def _get_endpoint(self, slug: str):
        endpoint = os.getenv("API_ENDPOINT")
        assert endpoint is not None, "API_ENDPOINT is not set"
        return urljoin(endpoint, slug)

    def _get_token(self):
        return self.login.get_token()

    def _get_user_code(self):
        return self.login.get_user_id()
