import os
from dataclasses import dataclass

import requests

from GlobalPayload import GlobalPayload


@dataclass
class Login:
    global_payload: GlobalPayload

    def __init__(self):
        self.global_payload = GlobalPayload(token="", userId="")

    def get_token(self) -> str:
        return self.global_payload.token

    def is_logged_in(self) -> bool:
        return self.get_token() != ""

    def login(self, user: str, password: str) -> None:
        login_url = os.getenv("LOGIN_URL")
        assert login_url is not None, "LOGIN_URL is not set"

        response = requests.get(
            url=login_url,
            json={
                "loginDs": user,
                "pwdCd": password,
            },
            headers={
                "Content-Type": "application/json",
            },
        )
        try:
            json = response.json()
            token = json["TOKEN_CD"]
            user_id = json["USR_CD"]
            self.global_payload.token = token
            self.global_payload.userId = user_id
        except:
            self.logout()

    def logout(self) -> None:
        self.global_payload.token = ""
        self.global_payload.userId = ""
