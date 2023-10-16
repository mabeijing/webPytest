from __future__ import annotations
from typing import Any, TYPE_CHECKING

from .baseApi import BaseApi

if TYPE_CHECKING:
    from libs import Bundle


class JobApi(BaseApi):
    def create(self, bundle: "Bundle"):
        url = self.config.URL + "/api/orders"
        data = bundle.project.to_create_jobs(bundle)
        resp = self.session.post(url, json=data)
        assert resp.status_code == 200
        result: dict[str, Any] = resp.json()
        assert result["returnCode"] == 0

        orderId: str = result["data"]
        print(f"create job -> {orderId} success.")
        bundle.storage.JobID = orderId
        return orderId

    def kickOff(self):
        pass
