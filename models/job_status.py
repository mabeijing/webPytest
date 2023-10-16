from typing import Optional
from pydantic import BaseModel, Field


class FileDataStatus(BaseModel):
    filepath: str
    sourceFilepath: str
    commentFlag: int
    bugFixStatus: int = Field(..., description="2:未返回,0:ok")
    taskIDs: Optional[list[int]] = None


class JobOperateStatus(BaseModel):
    locale: str
    status: int = Field(..., description="翻译状态,0:未返回,1:返回,3?,4:bugfix, 5:?, 10:close")
    canDownloadFlag: int = Field(..., description="翻译是否可下载.1:不可下载,0:可下载")
    worldServerProjectID: str
    fileData: Optional[list[FileDataStatus]] = []
    fileDatanil: Optional[list[FileDataStatus]] = []
    canReGenerate: int = Field(..., description="重走后处理,同步source,是否可以重新生成,0:可以,1:不可以")


class JobComponentStatus(BaseModel):
    productID: int
    productName: str
    releaseID: int
    releaseName: str
    commitMsg: str
    data: list[JobOperateStatus]
    snapID: int
