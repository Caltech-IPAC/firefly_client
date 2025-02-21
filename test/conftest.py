from pytest_container import add_logging_level_options, set_logging_level_from_cli_args


def pytest_addoption(parser):
    add_logging_level_options(parser)


def pytest_configure(config):
    set_logging_level_from_cli_args(config)
