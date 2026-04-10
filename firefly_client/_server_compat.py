from packaging.version import InvalidVersion, Version


# Minimum version of Firefly server that this version of firefly_client is compatible with
# Must be updated when a new release of firefly_client is made that relies on updates in Firefly server.
# For DEV version of Firefly server, the branch and commit info isn't considered in comparison so can be omitted.
MIN_SERVER_VERSION = '2026.1-DEV' # minimum bound on DEV includes PRE and formal releases

FIREFLY_LIB_VERSION_KEY = 'Firefly Library Version'
APP_VERSION_KEY = 'Version'


def get_server_version(version_data: dict) -> str|None:
    version = version_data.get(FIREFLY_LIB_VERSION_KEY)
    if not version: # Firefly isn't used as library but is the base app
        version = version_data.get(APP_VERSION_KEY)

    return version


def standardize_version(firefly_version_str: str) -> Version|None:
    """Convert a Firefly server version string to a Version object for comparison.
    Returns None if the string is not parseable.
    """
    try:
        return Version(firefly_version_str)
    except InvalidVersion:
        if 'DEV' in firefly_version_str:
            # Firefly version strings after 'DEV' may contain non-standard commit/branch info,
            # e.g. '2024.1-DEV_abc1' or '2024.1-DEV:branch_abc1'. Strip the suffix to make it parseable.
            try:
                return Version(firefly_version_str.partition('DEV')[0] + 'DEV')
            except InvalidVersion:
                pass
    return None


_MIN_VERSION = standardize_version(MIN_SERVER_VERSION)


def is_server_compatible(server_version: str|None) -> bool:
    if not server_version:
        return False
    version = standardize_version(server_version)
    return version is not None and version >= _MIN_VERSION
