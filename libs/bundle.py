from __future__ import annotations
from typing import Any, TYPE_CHECKING

from pydantic import BaseModel

from models import ProjectOut

if TYPE_CHECKING:
    from .mixin_session import MixinSession


class Storage(BaseModel):
    JobID: str = ""
    JobName: str = ""


class Section(BaseModel):
    # 用于将用例参数转化成数据类，参数化驱动流程
    # 关键字在这里拼接
    projectID: int
    projectName: str
    tmsName: str
    locales: list[str]
    components: list[dict[str, Any]]
    kickOffOption: int
    push: int

    def to_create_job(self):
        return {self.tmsName: self.components}


class Bundle:
    # 在用例执行前执行，生成projectModel信息，生成section用例参数，以及当前用例的存储空间
    def __init__(self, mixin: MixinSession, param: dict[str, Any]):
        print("Bundle 被实例化了")
        self._param: dict[str, Any] = param
        self._mixin = mixin

        self.section: Section = Section.model_validate(self._param)  # 参数化
        self.project: ProjectOut = self._mixin.api.project.search_detail(self)  # 系统数据模型
        self.storage: Storage = Storage()  # 用例数据存储区
