from __future__ import annotations

from typing import Any, TYPE_CHECKING, Literal, Optional
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


class LqeOption(BaseModel):
    id: int = 0
    locales: str = ""

    lqaCount: int = 0
    lqaRate: str = "0.0%"
    lqaSuggestion: str = "30% sampling, sample words >= 500"
    translatorID: int = 48

    lqeSamplingPercentage: str = "100%"
    lqeExcludeIceMatch: str = "true"
    lqeExcludeHundredMatch: str = "false"
    lqeFastTrack: str = "false"
    lqeQualityLevel: Literal["High", "Normal", "Low"] = "High"
    kickOffOption: Literal[1, 2, 3, 4] = 4
    lqeSampleMode: Literal["Time-Based", "Normal"] = "Normal"
    lqeSampleRangeStart: Optional[str] = None
    lqeSampleRangeEnd: Optional[str] = None

    def to_all_locales(self):
        return self.model_dump(exclude={"lqaCount", "lqaRate", "lqaSuggestion", "translatorID"})

    def to_per_locale(self):
        return self.model_dump()


class KickOption(BaseModel):
    locale: str
    option: Literal[1, 2, 3, 4]
    lqe: LqeOption


class KickOffParam(BaseModel):
    kickType: Literal["bylocale", "All"]
    kickOptions: list[KickOption]

    def to_all_locales(self) -> list[dict]:
        return [kick.lqe.to_all_locales() for kick in self.kickOptions]

    def to_per_locale(self) -> list[dict]:
        return [kick.lqe.to_per_locale() for kick in self.kickOptions]


class ComponentCommit(BaseModel):
    componentName: str
    locale: str
    commitMsg: str = ""


class PushParam(BaseModel):
    locales: list[str]
    components: list[ComponentCommit] = []


class Section(BaseModel):
    # 用于将用例参数转化成数据类，参数化驱动流程
    # 不处理接口参数，只处理场景参数，接口参数全部放在系统数据类处理
    projectID: int
    projectName: str
    tmsName: str
    locales: list[str]
    components: list[Component]
    create: CreateParam
    kickOff: KickOffParam
    push: PushParam
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
        componentArray: list[ProductOut] = [bundle.project.getComponentByName(c.componentName) for c in self.components]
        releaseInfos: list[dict[str, Any]] = []
        for component in componentArray:
            if bundle.section.kickOff.kickType == "All":
                msg = f"when allOrByLocale=All, the kickOptions length must 1"
                assert len(bundle.section.kickOff.kickOptions) == 1, msg
                kick = bundle.section.kickOff.kickOptions[0]
                assert kick.locale == "all", f"when allOrByLocale=All, the locales must equal all."
                localeAttributes = bundle.section.kickOff.to_all_locales()
            else:
                for index, kick in enumerate(bundle.section.kickOff.kickOptions):
                    kick.lqe.id = index
                    kick.lqe.locales = kick.locale
                    kick.lqe.kickOffOption = kick.option
                localeAttributes = bundle.section.kickOff.to_per_locale()

            releaseInfo: dict[str, Any] = {
                "releaseID": component.releaseData.releaseID,
                "allOrByLocale": bundle.section.kickOff.kickType,
                "localeAttributes": localeAttributes,
            }
            releaseInfos.append(releaseInfo)
        return releaseInfos

    def regenerateOption(self):
        pass

    def bugfixOption(self):
        pass

    def redoOption(self):
        pass
