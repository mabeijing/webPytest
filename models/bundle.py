from __future__ import annotations

from typing import Any
from pydantic import BaseModel


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
