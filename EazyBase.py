import os
from dataclasses import dataclass
from json import load

import requests

from Login import Login


@dataclass
class EazyBase:
    login: Login

    def __post_init__(self):
        with open("config.json", "r") as f:
            config = load(f)
            self.company_owner = config["company_"]

    def insert_into_kbase(self, mapdata, metadata: dict):
        url = os.getenv("EAZYBASE_URL")
        assert url is not None, "EAZYBASE_URL is not set"

        json = {
            "mapData": {
                "clientowner_cd": self.company_owner,
                "companyowner_id": self.company_owner,
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
            "token": self.login.global_payload.token,
        }
        response = requests.post(url=url, json=json).json()
        return response["insertObject"]

    # TODO: remove?
    def _unify_to_filed(self, fields, mapdata, base_data: str = ""):
        res = base_data
        for field in fields:
            if field in mapdata and len(mapdata[field]) > 0:
                res += f"<p>{field} : {mapdata[field]}</p>"

        return res
