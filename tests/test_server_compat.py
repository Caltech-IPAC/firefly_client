import pytest
from unittest.mock import patch
from firefly_client._server_compat import is_server_compatible


# Locked minimum version for test_is_server_compatible since test cases are based on this
_FIXED_MIN_VERSION = '2026.1'


# Read each row as: is_server_compatible(ver) for MIN=2026.1 → expected
@pytest.mark.parametrize('ver, expected', [
    # All variants within the 2026.1 cycle — DEV/PRE/patch all strip to (2026, 1)
    ('2026.1',                True),   # clean
    ('2026.1-DEV',            True),   # DEV suffix stripped
    ('2026.1-DEV:branch_abc', True),   # branch:commit stripped
    ('2026.1-PRE',            True),   # PRE stripped
    ('2026.1-PRE-3',          True),   # PRE with number stripped
    ('2026.1.2',              True),   # patch digit ignored
    # Newer cycles
    ('2026.2',                True),   # newer minor
    ('2027.1',                True),   # newer major
    # Older cycles
    ('2025.6',                False),  # older cycle
    ('2025.6-PRE-3',          False),  # older cycle, PRE stripped
    ('2024.1-DEV_abc1',       False),  # older cycle, DEV stripped
    # Unknown/unparseable — pass through
    ('not_a_version',         True),   # unparseable → None → pass through
    (None,                    True),   # None → pass through
])
def test_is_server_compatible(ver, expected):
    with patch('firefly_client._server_compat.MIN_SERVER_VERSION', _FIXED_MIN_VERSION):
        assert is_server_compatible(ver) == expected
