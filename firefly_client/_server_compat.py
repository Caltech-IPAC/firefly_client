from packaging.specifiers import SpecifierSet
from packaging.version import Version

# Version specifier for the Firefly server that this version of
# firefly_client is compatible with
COMPATIBLE_SERVER_VERSIONS = '>=2026.1'

FIREFLY_LIB_VERSION_KEY = 'Firefly Library Version'
APP_VERSION_KEY = 'Version'


def get_server_version(version_data: dict) -> str|None:
    version = version_data.get(FIREFLY_LIB_VERSION_KEY)
    if not version: # Firefly isn't used as library but is the base app
        version = version_data.get(APP_VERSION_KEY)

    return version


def is_server_compatible(server_version: str|None) -> bool:
    # TODO: make it robust for non-standard version formats firefly uses
    return (
        server_version is not None
        and Version(server_version) in SpecifierSet(COMPATIBLE_SERVER_VERSIONS)
    )
