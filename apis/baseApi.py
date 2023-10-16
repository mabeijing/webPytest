from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from libs import MixinSession


# 接口方法类
class BaseApi:
    def __init__(self, session: "MixinSession"):
        self._mixin_session = session
        self.config = self._mixin_session.config
        self.session = self._mixin_session.api_session
