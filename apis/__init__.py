from __future__ import annotations

from typing import TYPE_CHECKING
from .project import ProjectApi
from .job import JobApi

if TYPE_CHECKING:
    from libs import MixinSession

__all__ = ("ApiEntry",)


class ApiEntry:
    def __init__(self, session: "MixinSession"):
        self._mixin_session = session
        self.job: JobApi = JobApi(self._mixin_session)
        self.project: ProjectApi = ProjectApi(self._mixin_session)
