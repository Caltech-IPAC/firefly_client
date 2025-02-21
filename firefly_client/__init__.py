from importlib.metadata import PackageNotFoundError, version

from .env import Env
from .ffws import FFWs
from .range_values import RangeValues
from .firefly_client import FireflyClient


try:
    __version__ = version("firefly_client")
except PackageNotFoundError:
    # package is not installed
    __version__ = None

__all__ = ["Env", "FFWs", "FireflyClient", "RangeValues"]
