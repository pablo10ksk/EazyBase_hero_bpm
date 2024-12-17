import os
from typing import Optional, Tuple
from urllib.parse import urljoin
from datetime import datetime


import requests

from Login import Login
from tools.XyzTool import XyzTool


class Agent:
    def __init__(self, login: Login):
        self.login = login
        self.headers = {"Content-Type": "application/json"}

    def route_prompt(
        self,
        prompt: str,
        all_tools: list[XyzTool],
        historial: list[dict],
    ) -> Tuple[Optional[XyzTool], dict | str]:
        today = datetime.today().date()
        raw_response = requests.get(
            url=self._get_endpoint(),
            json={
                "token": self._get_token(),
                "mapData": {
                    "agent": "router",
                    "args": {
                        "prompt": f"On the date {today.strftime('%Y-%m-%d')}, the user sent us: '{prompt}'",
                        "messages": historial,
                    },
                },
            },
            headers={
                "Content-Type": "application/json",
            },
        )
        res = raw_response.json()
        print("Router:", res)
        response = res["return_execution"]["response"]

        if isinstance(response, str):
            return None, response
        elif isinstance(response, dict):
            tool_name = response.get("tool")
            tool = None
            for t in all_tools:
                if t.name == tool_name:
                    tool = t
                    break
            return tool, response
        else:
            return None, {}

    def _get_endpoint(self):
        endpoint = os.getenv("AGENT_ENDPOINT")
        assert endpoint is not None, "AGENT_ENDPOINT is not set"
        return endpoint

    def _get_token(self):
        return self.login.get_token_agent()

    def _get_user_code(self):
        return self.login.get_user_id()
