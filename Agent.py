import os
from datetime import datetime
from typing import Optional, Tuple
from urllib.parse import urljoin

import requests

from Login import Login
from tools.XyzTool import XyzTool


class Agent:
    MAIN_ROUTER = "router"

    def __init__(self, login: Login):
        self.login = login
        self.headers = {"Content-Type": "application/json"}

    def route_prompt(
        self,
        prompt: str,
        tools: list[XyzTool],
        historial: list[dict],
    ) -> Tuple[Optional[XyzTool], dict | str]:
        res = self._run_router(self.MAIN_ROUTER, prompt, historial)
        response = res["return_execution"]["response"]

        if isinstance(response, str):
            return None, response
        elif isinstance(response, dict):
            tool_name = response.get("tool")
            tool = None
            for t in tools:
                if t.name == tool_name:
                    tool = t
                    break
            return tool, response
        else:
            return None, {}

    def _run_router(
        self,
        router_code: str,
        prompt: str,
        historial: list[dict],
        additional_args: dict = {},
    ) -> dict:
        # today = datetime.today().date()
        raw_response = requests.get(
            url=self._get_endpoint(),
            json={
                "token": self._get_token(),
                "mapData": {
                    "agent": router_code,
                    "args": {
                        # "prompt": f"On the date {today.strftime('%Y-%m-%d')}, the user sent us: '{prompt}'",
                        "prompt": prompt,
                        "messages": historial,
                        **additional_args,
                    },
                },
            },
            headers={
                "Content-Type": "application/json",
            },
        )

        res = raw_response.json()
        print(f"Router {router_code}: {res}")
        return res

    def _get_endpoint(self):
        endpoint = os.getenv("AGENT_ENDPOINT")
        assert endpoint is not None, "AGENT_ENDPOINT is not set"
        return endpoint

    def _get_token(self):
        return self.login.get_token_agent()

    def _get_user_code(self):
        return self.login.get_user_id()
