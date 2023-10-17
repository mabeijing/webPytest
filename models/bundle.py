from __future__ import annotations

from typing import Any, TYPE_CHECKING
from pydantic import BaseModel

if TYPE_CHECKING:
    from libs import Bundle
    from models import ProductOut


class Component(BaseModel):
    componentName: str
    branch: str
    l10nFile: str
    repoUrl: str
    repoName: str
    source: list[tuple] = []
    baseJob: str = ""


class CreateParam(BaseModel):
    JobName: str = ""
    fullJob: bool = True
    splitByComponent: bool = False
    description: str = ""
    siteID: str = ""
    manualID: str = ""
    chapterID: str = ""
    articleID: str = ""


class Section(BaseModel):
    # 用于将用例参数转化成数据类，参数化驱动流程
    # 不处理接口参数，只处理场景参数，接口参数全部放在系统数据类处理
    projectID: int
    projectName: str
    tmsName: str
    locales: list[str]
    components: list[Component]
    create: CreateParam
    kickOff: int
    push: int
    regenerate: int
    redo: int
    bugfix: int
    cancel: int

    def getComponentByName(self, componentName: str) -> Component:
        for c in self.components:
            if c.componentName == componentName:
                return c
        raise ValueError(f"{componentName} not in {self.components}")

    @property
    def componentNameArray(self) -> list[str]:
        return [item.componentName for item in self.components]

    def pushOption(self, bundle: Bundle):
        pass

    def kickOffOption(self, bundle: Bundle) -> list[dict[str, Any]]:
        componentArray: list[ProductOut] = []

        for componentName in self.componentNameArray:
            component = bundle.project.getComponentByName(componentName)
            componentArray.append(component)

        releaseInfos: list[dict[str, Any]] = []
        for component in componentArray:
            releaseInfo: dict[str, Any] = {
                "releaseID": component.releaseData.releaseID,
                "allOrByLocale": "All",
                "localeAttributes": [
                    {
                        "id": 1,
                        "locales": "all",
                        "lqeSamplingPercentage": "100%",
                        "lqeExcludeIceMatch": "true",
                        "lqeExcludeHundredMatch": "false",
                        "lqeFastTrack": "false",
                        "lqeQualityLevel": "High",
                        "kickOffOption": 4,
                        "lqeSampleMode": "Normal",
                        "lqeSampleRangeStart": None,
                        "lqeSampleRangeEnd": None,
                        "attributes.0.kickOffOption": "4",
                    }
                ],
            }
            releaseInfos.append(releaseInfo)
        return releaseInfos

    def regenerateOption(self):
        pass

    def bugfixOption(self):
        pass

    def redoOption(self):
        pass
