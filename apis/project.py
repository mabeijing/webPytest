from __future__ import annotations
from typing import TYPE_CHECKING

from models import ProjectOut
from .baseApi import BaseApi

if TYPE_CHECKING:
    from libs import Bundle


class ProjectApi(BaseApi):
    def search_detail(self, bundle: "Bundle"):
        url = self.config.URL + "/api/gcc/project/searchdetail"
        body = {"fromFront": True, "projectID": bundle.section.projectID}
        resp = self.session.post(url, json=body)
        result = resp.json()
        project = ProjectOut.model_validate(result)
        return project

    def clean(self):
        pass

    def clone(self):
        pass

    def modify(self):
        pass
