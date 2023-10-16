from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
import time

from .baseApi import BaseApi
from models import JobComponentStatus

if TYPE_CHECKING:
    from libs import Bundle


class JobApi(BaseApi):
    def create(self, bundle: "Bundle"):
        url = self.config.URL + "/api/orders"
        data = bundle.project.to_create_job(bundle)
        resp = self.session.post(url, json=data)
        assert resp.status_code == 200
        result: dict[str, Any] = resp.json()
        assert result["returnCode"] == 0

        orderId: str = result["data"]
        bundle.storage.JobID = orderId
        print(f"create job -> {orderId} success.")
        return orderId

    def search_by_status(self, jobName: str = "", applicant: str = "", status: list[int] = None) -> list[
        dict[str, Any]]:
        url = self.config.URL + "/api/orders/workbench/searchbystatus"
        body = {
            "status": status,
            "pageNo": 1,
            "pageSize": 10,
            "jobName": jobName,
            "applicant": applicant,
        }
        resp = self.session.post(url, json=body)
        assert resp.status_code == 200
        result: dict[str, Any] = resp.json()
        assert result["returnCode"] == 0, result
        jobArray: list[dict[str, Any]] = result.get("data", {}).get("rows", [])
        return jobArray

    def job_details(self, jobId: str) -> dict[str, Any]:
        url = self.config.URL + f"/api/orders/{jobId}"
        resp = self.session.get(url)
        assert resp.status_code == 200
        result: dict[str, Any] = resp.json()
        assert result["returnCode"] == 0, result
        details: dict[str, Any] = result.get("data", {})
        return details

    def wait_job_progress_completed(self, bundle: Bundle):
        """
        创建的job不能直接取消。需要等到progess执行完，否则{'message': 'Process not exist', 'returnCode': 1}
        "progress": [   这个是没进度条的， 没有触发ws任务
                    {
                        "productID": 1437,
                        "productName": "discovery",
                        "releaseID": 4354,
                        "releaseName": "0.1",
                        "snapID": 0,
                        "pmReviewData": []
                    }
                ],
        "progress": [   ws创建完任务，等待返回
                    {
                        "productID": 1437,
                        "productName": "discovery",
                        "releaseID": 4354,
                        "releaseName": "0.1",
                        "snapID": 8668,
                        "pmReviewData": [
                            {
                                "status": 1,
                                "locale": "de_DE"
                            }
                        ]
                    }
                ],
        "progress": [   这个是进度条满的，涉及参数component。locales
                    {
                        "productID": 881,
                        "productName": "vsanmgmt",
                        "releaseID": 2650,
                        "releaseName": "235.23.1",
                        "snapID": 8531,
                        "pmReviewData": [
                            {
                                "status": 0,
                                "locale": "zh_TW"
                            }
                        ]
                    },
                    {
                        "productID": 880,
                        "productName": "vsanhealth",
                        "releaseID": 2652,
                        "releaseName": "235.23.1",
                        "snapID": 8530,
                        "pmReviewData": [
                            {
                                "status": 0,
                                "locale": "zh_TW"
                            }
                        ]
                    },
        """
        start_tsp: int = int(time.time())
        current_tsp: int = int(time.time())
        duration: int = self.config.DURATION

        success = False
        while current_tsp - start_tsp <= duration:
            try:
                jobArray = self.search_by_status(bundle.storage.JobName, self.config.USERNAME)
                assert jobArray

                currentJob = None
                for job in jobArray:
                    if job.get("orderName", "") == bundle.storage.JobName:
                        currentJob = job
                        break
                assert currentJob

                progressArray: list[dict[str, Any]] = currentJob.get("progress", [])
                assert progressArray

                componentNameArray: list[str] = [
                    c.get("productName", "")
                    for c in progressArray
                    if c.get("productName", "")
                ]
                assert set(componentNameArray) == set(bundle.section.componentNameArray)

                for progress in progressArray:
                    review_data: list[dict[str, Any]] = progress.get("pmReviewData", [])
                    assert review_data

                    locale_data: list[str] = [d.get("locale", "") for d in review_data]
                    assert set(locale_data) == set(bundle.section.locales)

                    # [0, 1, 2]
                    # 0: OK
                    # 1: NOK
                    locale_status: list[dict[str, Any]] = [
                        d for d in review_data if d.get("status", -1) == 0
                    ]
                    assert locale_status and len(locale_status) == len(bundle.section.locales)

                # 如果没有任何异常，说明验证通过撒
                success = True
                break
            except AssertionError as e:
                time.sleep(5)
                current_tsp: int = int(time.time())
                print(
                    f"duration {current_tsp - start_tsp}s, next check progress after 5 seconds..."
                )

            except Exception as e:
                print(f"execute error => {str(e)}")
                raise AssertionError(e) from e

        current_tsp: int = int(time.time())
        print(f"{bundle.storage.JobName} progress 100% in {current_tsp - start_tsp}s.")
        return success

    def wait_job_status(self, bundle: Bundle, status: list[int]):
        start_tsp: int = int(time.time())
        current_tsp: int = int(time.time())
        duration: int = self.config.DURATION

        success = False
        while current_tsp - start_tsp <= duration:
            try:
                jobArray = self.search_by_status(bundle.storage.JobName, self.config.USERNAME, status)
                assert jobArray

                currentJob = None
                for job in jobArray:
                    if job.get("orderName", "") == bundle.storage.JobName:
                        currentJob = job
                        break
                assert currentJob

                assert currentJob["status"] == 50
                assert currentJob["stepStatus"] == 7

                # 如果没有任何异常，说明验证通过撒
                success = True
                break
            except AssertionError as e:
                time.sleep(5)
                current_tsp: int = int(time.time())
                print(
                    f"duration {current_tsp - start_tsp}s, next check job status after 5 seconds..."
                )

            except Exception as e:
                print(f"execute error => {str(e)}")
                raise AssertionError(e) from e

        current_tsp: int = int(time.time())
        print(
            f"{bundle.storage.JobName} job Completed and stepStatus is TargetGenerated in {current_tsp - start_tsp}s.")
        return success

    def wait_job_pipeline_status(self, bundle: Bundle):
        start_tsp: int = int(time.time())
        current_tsp: int = int(time.time())
        duration: int = self.config.DURATION

        success = False
        while current_tsp - start_tsp <= duration:
            try:
                jobArray = self.search_by_status(bundle.storage.JobName, self.config.USERNAME)
                assert jobArray

                currentJob = None
                for job in jobArray:
                    if job.get("orderName", "") == bundle.storage.JobName:
                        currentJob = job
                        break
                assert currentJob

                # 如果没有任何异常，说明验证通过撒
                success = True
                break
            except AssertionError as e:
                time.sleep(5)
                current_tsp: int = int(time.time())
                print(f"duration {current_tsp - start_tsp}s, next after 5 seconds...")

            except Exception as e:
                print(f"execute error => {str(e)}")
                raise AssertionError(e) from e

        current_tsp: int = int(time.time())
        print(f"{bundle.storage.JobName} progress 100% in {current_tsp - start_tsp}s.")
        return success

    def wait_job_kick_off_available(self, bundle: Bundle) -> bool:
        start_tsp: int = int(time.time())
        current_tsp: int = int(time.time())
        duration: int = self.config.DURATION

        success = False
        while current_tsp - start_tsp <= duration:
            try:
                jobDetails: dict[str, Any] = self.job_details(bundle.storage.JobID)
                jobMenuType: int = jobDetails.get("jobMenuType", -1)
                jobStatus: int = jobDetails.get("status", -1)
                assert jobMenuType == 3
                assert jobStatus == 20
                success = True
                break
            except AssertionError as e:
                time.sleep(5)
                current_tsp: int = int(time.time())
                print(
                    f"duration {current_tsp - start_tsp}s, next check jobMenuType&jobStatus after 5 seconds..."
                )

            except Exception as e:
                print(f"execute error => {str(e)}")
                raise AssertionError(e) from e

        current_tsp: int = int(time.time())
        print(f"{bundle.storage.JobID} kick off status is jobMenuType=3&jobStatus=20")
        return success

    def cancel_job(self, bundle: Bundle):
        # 创建完，即可cancel。由于ws交互，创建完，短时间内无法cancel，需要等ws创建task之后，可以cancel
        # 默认是进度条完成后，进行cancel
        assert self.wait_job_progress_completed(bundle)

        url = f"{self.config.URL}/api/orders/{bundle.storage.JobID}/operate"
        body = {
            "orderID": f"{bundle.storage.JobID}",
            "operationType": 3,
            "comment": "",
            "operatedBy": self.config.USERNAME,
        }

        resp = self.session.post(url, json=body)
        assert resp.status_code == 200
        result: dict[str, Any] = resp.json()
        assert result["returnCode"] == 0, result
        print(f"cancel_job {bundle.storage.JobID} success.")

    def kick_off(self, bundle: Bundle):
        # KickOff前置条件，进度条100%，并且jobStatu==20 && jobMenuType==3
        assert self.wait_job_progress_completed(bundle)
        assert self.wait_job_kick_off_available(bundle)

        url = f"{self.config.URL}/api/orders/{bundle.storage.JobID}/operate"
        body = {
            "orderID": bundle.storage.JobID,
            "operationType": 2,
            "comment": "",
            "operatedBy": self.config.USERNAME,
            "kickOffOption": 1,
            "releaseInfos": bundle.section.kickOffOption(bundle),
        }
        resp = self.session.post(url, json=body)
        assert resp.status_code == 200
        result: dict[str, Any] = resp.json()
        assert result["returnCode"] == 0, result
        print(f"kick_off_job {bundle.storage.JobID} success.")

    def searchTranslationFile(self, bundle: Bundle) -> list[JobComponentStatus]:
        # 可以拿到worldServerProjectID，用于push
        # 响应有3级，1层是product，2层是locale+worldServerProjectID，3层是file
        url = self.config.URL + "/api/orders/searchtranslationfile"
        body = {"orderID": bundle.storage.JobID}
        resp = self.session.post(url, json=body)
        assert resp.status_code == 200
        result: dict[str, Any] = resp.json()
        assert result["returnCode"] == 0, result
        products: list[dict[str, Any]] = result.get("product", [])

        return [JobComponentStatus.model_validate(product) for product in products]

    def wait_job_locale_pushable(self, bundle: Bundle, locales: list[str] = None):
        start_tsp: int = int(time.time())
        current_tsp: int = int(time.time())
        duration: int = self.config.DURATION

        success = False
        while current_tsp - start_tsp <= duration:
            try:
                componentStatusArray: list[
                    JobComponentStatus
                ] = self.searchTranslationFile(bundle)

                for componentStatus in componentStatusArray:
                    assert componentStatus.data
                    for component in componentStatus.data:
                        assert (
                                component.status == 1
                        ), f"{componentStatus.productName}-{component.locale} status is {component.status} not 1"

                # 如果没有任何异常，说明验证通过撒
                success = True
                break
            except AssertionError as e:
                time.sleep(5)
                current_tsp: int = int(time.time())
                print(
                    f"duration {current_tsp - start_tsp}s, next check translation progress after 5 seconds..., {str(e)}"
                )

            except Exception as e:
                print(f"execute error => {str(e)}")
                raise AssertionError(e) from e

        current_tsp: int = int(time.time())
        print(f"{bundle.storage.JobID} translation progress 100% in {current_tsp - start_tsp}s.")
        return success

    def push_online(self, bundle: Bundle, **kwargs: Any):
        # job的状态时InTranslation的时候，就有部分可以操作
        # push的粒度是locale+productName
        # 默认all locale push
        # kwargs commitMsg

        _commitMsg: Optional[str] = kwargs.get("commitMsg", None)
        # _locale: Optional[str] = kwargs.get("locale", None)
        assert self.wait_job_locale_pushable(bundle)

        componentStatusArray: list[JobComponentStatus] = self.searchTranslationFile(bundle)
        data: list[dict[str, Any]] = []
        for componentStatus in componentStatusArray:
            commitMsg: str = _commitMsg if _commitMsg else componentStatus.commitMsg
            productData: list[dict[str, str]] = [
                {
                    "locale": operateStatus.locale,
                    "worldServerProjectID": operateStatus.worldServerProjectID,
                }
                for operateStatus in componentStatus.data
            ]
            data.append(
                {
                    "productID": componentStatus.productID,
                    "releaseID": componentStatus.releaseID,
                    "productData": productData,
                    "commitMsg": commitMsg,
                }
            )

        url = self.config.URL + "/api/orders/translationreview"
        body = {
            "orderID": bundle.storage.JobID,
            "operationType": 0,
            "operatedBy": self.config.USERNAME,
            "data": data,
        }

        resp = self.session.post(url, json=body)
        assert resp.status_code == 200
        result: dict[str, Any] = resp.json()
        assert result["returnCode"] == 0, f"{result}"
        print(f"{bundle.storage.JobID} push online success")
