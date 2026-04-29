import pytest
from unittest.mock import patch
from firefly_client._server_compat import (
    standardize_version, is_server_compatible
)


@pytest.mark.parametrize('ver,expected_str', [
    ('2026.1',                 '2026.1'),      # standard release
    ('2026.1-DEV',             '2026.1.dev0'), # plain DEV
    ('2026.1-DEV:branch_abc1', '2026.1.dev0'), # DEV with branch:commit suffix
    ('2024.1-DEV_abc1',        '2024.1.dev0'), # DEV with underscore suffix
    ('2026.1-PRE-3',           '2026.1rc3'),   # PRE with number
    ('2026.1-PRE',             '2026.1rc0'),   # PRE without number
    ('not_a_version',          'None'),        # unparseable
])
def test_standardize_version(ver, expected_str):
    assert str(standardize_version(ver)) == expected_str


# Locked minimum version for test_is_server_compatible since test cases are based on this
_FIXED_MIN_VERSION = standardize_version('2026.1-DEV')


@pytest.mark.parametrize('ver,expected', [
    ('2026.1-DEV',            True),   # exact minimum
    ('2026.1-DEV:branch_abc', True),   # DEV with suffix at minimum version
    ('2026.1-PRE-3',          True),   # pre-release of same version cycle
    ('2026.1',                True),   # formal release >= minimum
    ('2027.1',                True),   # clearly newer
    ('2025.6-PRE-3',          False),  # pre-release of older version cycle
    ('2025.6',                False),  # below minimum
    ('2024.1-DEV_abc1',       False),  # old DEV
    ('not_a_version',         True),   # unparseable — unknown, pass through
    (None,                    True),   # None — unknown, pass through
])
def test_is_server_compatible(ver, expected):
    with patch('firefly_client._server_compat._MIN_VERSION', _FIXED_MIN_VERSION):
        assert is_server_compatible(ver) == expected
