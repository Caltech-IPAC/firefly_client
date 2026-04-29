from packaging.version import InvalidVersion, Version


# Minimum Firefly server version this firefly_client is compatible with.
# Bump this only when a client release depends on a server-side change that
# breaks client functionality without it. Behavioral improvements don't count.
#
# Recent PR dependency log — explaining the dependency and whether it is an API break:
#   firefly_client#79 → firefly#1936 (2026.1): _confirm_version() needs version endpoint        [still works without it]
#   firefly_client#78 → firefly#1910 (2026.1): show_xyplot/chart() needs activating chart view  [still works without it]
#   firefly_client#75 → firefly#1825 (2025.4): show_data() needs external upload action         [fails without it] ← CURRENT
MIN_SERVER_VERSION = '2025.4'

FIREFLY_VERSION_KEY = 'Firefly Version'


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
        return True  # unknown version — pass through for backward compatibility
    version = standardize_version(server_version)
    return version is None or version >= _MIN_VERSION
