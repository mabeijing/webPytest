import pytest

from pytest import FixtureRequest
from typing import Any, Generator

from libs import MixinSession, Bundle


@pytest.fixture(scope="session", autouse=True)
def mixin() -> MixinSession:
    # 默认读取配置，找到root，启动ui，返回mixin本身
    print("")
    print("init MixinSession")
    return MixinSession()


@pytest.fixture()
def bundle(mixin: MixinSession, request: FixtureRequest) -> Generator[Bundle, None, None]:
    # 主要为了找到系统核心对象，和关联测试bundle
    param: dict[str, Any] = request.param
    bundle = Bundle(mixin, param)
    yield bundle
    mixin.api.project.clean()
