from __future__ import annotations
from typing import Any, TypedDict, Optional, Union
from enum import Enum

from pydantic import BaseModel


class BaseOrderDict(TypedDict):
    basedOrderID: str
    basedOrderName: str
    basedSnapID: int


class RecentJob(BaseModel):
    id: str
    orderName: str
    projectID: int
    projectName: str
    applicant: str
    status: int
    createdTime: str
    updatedTime: str = ""
    createBy: str = ""
    fullJob: str
    snapID: int

    def to_dict(self) -> BaseOrderDict:
        return BaseOrderDict(basedOrderID=self.id, basedOrderName=self.orderName, basedSnapID=self.snapID)


class LocaleStatus(BaseModel):
    status: int
    locale: str


class ReleaseProgress(BaseModel):
    productID: int
    productName: str
    releaseID: int
    releaseName: str
    snapID: int
    pmReviewData: list[LocaleStatus] = []

    def assertReviewData(self):
        for locale in self.pmReviewData:
            assert locale.status == 0, f"{locale.locale} status is {locale.status} not 0."


class JobStatusEnum(int, Enum):
    PackagePreparing = 20
    InTranslation = 30
    Translated = 9999
    Completed = 50
    Error = 60
    Closed = 70
    Canceled = 80
    Panic = 90


class JobStatus(BaseModel):
    id: str
    orderName: str
    projectID: int
    projectName: str
    status: Union[int, JobStatusEnum]
    stepStatus: int
    progress: list[ReleaseProgress] = []
    pipelineStatus: int
    labels: list[int]
    fullJob: str
    basedOrderNames: Optional[str]
    allTranslationBack: int
