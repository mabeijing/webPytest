from __future__ import annotations
import datetime
from typing import Optional, Any, TYPE_CHECKING
from pydantic import BaseModel

if TYPE_CHECKING:
    from conftest import Bundle


class WSProjectTypeOut(BaseModel):
    tms: str
    wsProjectTypeID: int
    wsProjectTypeName: str


class NodeData(BaseModel):
    nodeID: int
    nodeName: str
    nodeType: str = "build-in"
    description: str = ""
    variables: str
    filesPattern: str = ""
    ruleID: str
    pipLineType: Optional[int]
    nodeIndex: int


class Pipeline(BaseModel):
    pipelineID: int
    pipelineIndex: int
    pipelineName: Optional[str]
    nodeData: list[list[NodeData]]


class VendorOut(BaseModel):
    releaseID: int
    locale: str
    translator: str
    reviewer: str
    lspProvider: str
    lspProviderName: str
    sourceLanguageCode: Optional[str]
    targetLanguageCode: Optional[str]
    translatorID: int
    reviewerID: int


class ReleaseData(BaseModel):
    releaseID: int
    basicProductID: int
    releaseName: str
    productType: int
    supportedLanguages: str
    data: str
    comments: str = ""
    vendors: list[VendorOut]
    pipelineHistorys: Optional[str]
    reviewers: str = ""
    reviewScope: int = 0
    commitMsg: str = ""
    singleCloneFlag: int
    cloneSrcReleaseID: Optional[int]


class ProductData(BaseModel):
    productID: int
    productType: int
    productName: str
    worldServerTMGroup: Optional[str]
    worldServerWorkFlow: Optional[str]
    description: str = ""
    sourcePipeline: Pipeline
    translationPipeline: Pipeline


class ProductOut(BaseModel):
    projectID: int
    productData: ProductData
    releaseData: ReleaseData


class ComponentMember(BaseModel):
    releaseID: Optional[int]
    productID: int
    productName: str
    releaseName: Optional[str]
    componentGroupID: int
    projectID: int
    id: int


class ComponentGroup(BaseModel):
    componentGroupName: str
    projectID: int
    componentMembers: list[ComponentMember]


class ProjectOut(BaseModel):
    projectID: int
    projectName: str
    buName: str
    lqeProductName: str
    lqeReleaseName: str
    wsProjectTypes: list[WSProjectTypeOut]
    supportedLanguages: Optional[str]
    comments: str = ""
    status: int
    applicantID: int
    applicant: str
    reviewers: Optional[str]
    reviewScope: Optional[str]
    products: list[ProductOut]
    orderId: Optional[str] = None
    data: Optional[str] = None
    gabiProductID: str
    componentGroups: list[ComponentGroup]

    def _search_tms(self, tmsName: str) -> WSProjectTypeOut:
        for ws in self.wsProjectTypes:
            if ws.wsProjectTypeName == tmsName:
                return ws
        raise ValueError(f"{tmsName} not in {self.wsProjectTypes}")

    def _search_components(self, components: list[str]) -> list[dict[str, Any]]:
        productNameArray: list[str] = [p.productData.productName for p in self.products]

        products: list[ProductOut] = [
            p for p in self.products if p.productData.productName in components
        ]
        assert len(products) == len(
            components
        ), f"{components} not all in {productNameArray}"

        return [
            {
                "releaseID": p.releaseData.releaseID,
                "releaseName": p.releaseData.releaseName,
                "productID": p.productData.productID,
                "productName": p.productData.productName,
                "resourceLocale": p.releaseData.supportedLanguages,
                "vendors": None,
            }
            for p in products
        ]

    def to_create_jobs(self, bundle: Bundle):
        components = [item["componentName"] for item in bundle.section.components]
        locales = bundle.section.locales
        fullJob = 1
        tmsName = bundle.section.tmsName

        timestamp: str = datetime.datetime.now(
            tz=datetime.timezone(datetime.timedelta(hours=8))
        ).strftime("%Y.%m.%d.%H%M")
        bundle.storage.JobName = f"automationTest[NoTranslate]-{self.applicant}-{timestamp}"

        orderCreateData: dict[str, Any] = {
            "status": "completed",
            "projectID": self.projectID,
            "projectName": self.projectName,
            "orderName": bundle.storage.JobName,
            "description": self.comments,
            "releases": self._search_components(components),
            "processInstanceID": "",
            "applicant": self.applicant,
            "operationType": 1,
            "locales": ",".join(locales),
            "dropSplitFlag": 2,
            "fullJob": "1" if fullJob else "",
        }
        orderCreateData.update(self._search_tms(tmsName).model_dump())
        return orderCreateData

    def to_create_job(
            self,
            components: list[str],
            tmsName: str,
            locales: list[str],
            fullJob: bool = True,
            **kwargs: Any,
    ) -> dict[str, Any]:
        timestamp: str = datetime.datetime.now(
            tz=datetime.timezone(datetime.timedelta(hours=8))
        ).strftime("%Y.%m.%d.%H%M")
        self.jobName = f"automationTest[NoTranslate]-{self.applicant}-{timestamp}"

        orderCreateData: dict[str, Any] = {
            "status": "completed",
            "projectID": self.projectID,
            "projectName": self.projectName,
            "orderName": self.jobName,
            "description": self.comments,
            "releases": self._search_components(components),
            "processInstanceID": "",
            "applicant": self.applicant,
            "operationType": 1,
            "locales": ",".join(locales),
            "dropSplitFlag": 2,
            "fullJob": "1" if fullJob else "",
        }
        orderCreateData.update(self._search_tms(tmsName).model_dump())
        return orderCreateData

    def getComponentByName(self, componentName: str) -> ProductOut:
        for component in self.products:
            if component.productData.productName == componentName:
                return component

        raise AssertionError(f"{componentName} not related in {self.projectName}.")
