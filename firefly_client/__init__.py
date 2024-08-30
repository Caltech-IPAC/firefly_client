from importlib.metadata import PackageNotFoundError, version

from .firefly_client import FireflyClient
from .ffws import FFWs
from .env import Env
from .range_values import RangeValues

try:
    __version__ = version("firefly_client")
except PackageNotFoundError:
    # package is not installed
    __version__ = None
