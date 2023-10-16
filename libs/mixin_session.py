import atexit
import requests
from pathlib import Path
from typing import Any

import settings
from apis import ApiEntry
from libs import DataBase

# /xxx/webPytest
_ROOT_ = Path(__file__).parent.parent


class MixinSession:
    # 提供路径，配置，session和数据库
    def __init__(self):
        self.root: Path = _ROOT_
        self.config: settings.Config = settings.Config()
        self.api_session = requests.Session()
        self.USERNAME_ID: str = self._apiLogin()
        self.api: ApiEntry = ApiEntry(self)
        self.db: DataBase = DataBase(self.config)
        atexit.register(self._close)
        atexit.register(self.db.closed)

    def _close(self):
        print("退出mixin")

    def _apiLogin(self) -> str:
        url = self.config.URL + "/api/rs/user/userlogin"
        headers = {"Content-Type": "application/json"}
        body = {"username": self.config.USERNAME, "password": self.config.PASSWORD}
        resp = self.api_session.post(url, json=body, headers=headers)
        assert resp.status_code == 200

        result: dict[str, Any] = resp.json()
        assert result.get("return_code") == 200, result
        session_id: str = result["session_id"]
        self.api_session.headers.update(
            {"session": session_id, "Content-Type": "application/json"}
        )
        user_id: int = result["user_id"]
        print("login success.")
        return str(user_id)
