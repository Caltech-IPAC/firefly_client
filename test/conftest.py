from pytest_container import (
    add_logging_level_options,
    auto_container_parametrize,
    set_logging_level_from_cli_args,
)


def pytest_generate_tests(metafunc):
    auto_container_parametrize(metafunc)


def pytest_addoption(parser):
    add_logging_level_options(parser)


def pytest_configure(config):
    set_logging_level_from_cli_args(config)
