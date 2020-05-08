from .firefly_client import FireflyClient
from .firefly_ws_connections import FFWs
import pkg_resources

__version__ = pkg_resources.get_distribution("firefly_client").version
