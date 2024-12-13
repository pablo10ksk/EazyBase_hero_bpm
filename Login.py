import os
from dataclasses import dataclass
from typing import Optional

import requests


@dataclass
class Login:
    _token: Optional[str] = None
    _tokenAgent: Optional[str] = None
    _userId: Optional[str] = None

    _user: Optional[str] = None
    _password: Optional[str] = None

    def __init__(self):
        pass

    def get_token(self) -> Optional[str]:
        return self._token

    def get_token_agent(self) -> Optional[str]:
        return self._tokenAgent

    def get_user_id(self) -> Optional[str]:
        return self._userId

    def is_logged_in(self) -> bool:
        return self._token is not None and self._userId is not None

    def login(self, user: str, password: str) -> None:
        self._user = user
        self._password = password
        self.renew_token()

    def renew_token(self) -> None:
        assert self._user is not None, "Cannot renew token without user"
        assert self._password is not None, "Cannot renew token without password"

        api_login_url = os.getenv("API_LOGIN_URL")
        assert api_login_url is not None, "API_LOGIN_URL is not set"

        agent_login_url = os.getenv("AGENT_LOGIN_URL")
        assert agent_login_url is not None, "AGENT_LOGIN_URL is not set"

        api_login = self._login_request(api_login_url, self._user, self._password)
        # FIXME: recuperar original
        # agent_login = self._login_request(agent_login_url, self._user, self._password)
        agent_login = self._login_request(agent_login_url, "paint", "a)2921C9FI")

        if api_login is None or agent_login is None:
            print(
                f"Api_login {"is " if api_login is None else "is not "}None, Agent_login {"is " if agent_login is None else "is not "}None"
            )
            self.logout()
            return
        api_token, cd = api_login
        agent_token, _ = agent_login

        self._token = api_token
        self._tokenAgent = agent_token
        self._userId = cd

    def _login_request(
        self, url: str, user: str, password: str
    ) -> Optional[tuple[str, str]]:
        response = requests.get(
            url=url,
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
            return (token, user_id)
        except Exception as e:
            return None

    def logout(self) -> None:
        self._token = None
        self._tokenAgent = None
        self._userId = None
