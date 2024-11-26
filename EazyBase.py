import os
from dataclasses import dataclass
from json import load

import requests
import streamlit as st

from Login import Login


@dataclass
class EazyBase:
    login: Login

    def __post_init__(self):
        with open("config.json", "r") as f:
            config = load(f)
            self.company_owner = config["company_"]

    def insert_into_kbase(self, mapdata, metadata: dict):
        return st.session_state.api.insert_into_kbase(
            self.company_owner, mapdata, metadata
        )

    # TODO: remove?
    def _unify_to_filed(self, fields, mapdata, base_data: str = ""):
        res = base_data
        for field in fields:
            if field in mapdata and len(mapdata[field]) > 0:
                res += f"<p>{field} : {mapdata[field]}</p>"

        return res
