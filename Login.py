import os
from dataclasses import dataclass
from typing import Optional

import requests


@dataclass
class Login:
    _token: Optional[str] = None
    _userId: Optional[str] = None

    _user: Optional[str] = None
    _password: Optional[str] = None

    def __init__(self):
        pass

    def get_token(self) -> Optional[str]:
        return self._token

    def get_user_id(self) -> Optional[str]:
        return self._userId

    def is_logged_in(self) -> bool:
        return self._token is not None and self._userId is not None

    def login(self, user: str, password: str) -> None:
        self._user = user
        self._password = password
        self.renew_token()

    def renew_token(self) -> None:
        login_url = os.getenv("LOGIN_URL")
        assert login_url is not None, "LOGIN_URL is not set"

        assert self._user is not None, "Cannot renew token without user"
        assert self._password is not None, "Cannot renew token without password"

        response = requests.get(
            url=login_url,
            json={
                "loginDs": self._user,
                "pwdCd": self._password,
            },
            headers={
                "Content-Type": "application/json",
            },
        )
        try:
            json = response.json()
            token = json["TOKEN_CD"]
            user_id = json["USR_CD"]
            self._token = token
            self._userId = user_id
        except:
            self.logout()

    def logout(self) -> None:
        self._token = None
        self._userId = None
