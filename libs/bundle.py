from __future__ import annotations
from typing import Any, TYPE_CHECKING

from models import ProjectOut, Section, RecentJob

if TYPE_CHECKING:
    from .mixin_session import MixinSession


class Storage:
    JobID: str = ""
    JobName: str = ""

    RecentJobs: dict[str, RecentJob] = {}


class Bundle:
    # 在用例执行前执行，生成projectModel信息，生成section用例参数，以及当前用例的存储空间
    def __init__(self, mixin: MixinSession, param: dict[str, Any]):
        print("Bundle 被实例化了")
        self._param: dict[str, Any] = param
        self._mixin = mixin

        self.storage: Storage = Storage()  # 用例数据存储区
        self.section: Section = Section.model_validate(self._param)  # 参数化模型
        self.project: ProjectOut = self._mixin.api.project.search_detail(self)  # 系统数据模型
