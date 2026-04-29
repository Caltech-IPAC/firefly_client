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


def _parse_version(version_str: str) -> tuple[int, int] | None:
    """Extract (major, minor) from a Firefly version string, ignoring DEV/PRE/patch suffixes.
    Returns None if not parseable.
    """
    try:
        core = version_str.split('-')[0]  # strip DEV/PRE/patch suffix
        parts = core.split('.')
        return (int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        return None


def is_server_compatible(server_version: str | None) -> bool:
    if not server_version:
        return True  # unknown version — pass through for backward compatibility
    
    parsed_server_version = _parse_version(server_version)
    if parsed_server_version is None:
        return True  # unparseable version — pass through
    
    # Python tuples are compared lexicographically (element-by-element), so (2026, 1) >= (2025, 4)
    # evaluates as: 2026 > 2025 → True, without needing to inspect the minor at all
    return parsed_server_version >= _parse_version(MIN_SERVER_VERSION)
