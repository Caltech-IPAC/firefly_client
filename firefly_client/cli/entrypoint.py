"""
Firefly CLI entry point.

This module provides the entry point for the Firefly CLI, as well as the
configuration and context objects.
"""

###############################################################################
# The following code leaves the the convention of using NumpyDoc long         #
# docstrings for the module and classes, and uses the NumpyDoc short          #
# docstrings. These docstrings are also referred to as PandaDoc docstrings.   #
# as they are used in the Pandas library.                                     #
#                                                                             #
# The departure from the convention is intentional, as `click` and `pydantic` #
# only support short docstrings for automatically parsing help text.          #
# Unfortinately, NumpyDoc short docstrings can only support either typing     #
# comments or help text, but not both.                                        #
###############################################################################

import datetime
import json
import os
from enum import StrEnum
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import ParseResult, urlparse

from firefly_client import FireflyClient

try:
    import rich_click as click
    import tomlkit
    from appdirs import AppDirs
    from dotenv import load_dotenv
    from pydanclick import from_pydantic
    from pydantic import AliasChoices, BaseModel, Field, ValidationError
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from rich_click import rich_click as rc
except ImportError:
    raise ImportError(
        "Please install the click package to use the Firefly CLI. "
        "You can install it with 'pip install firefly_client[cli]'."
    )

# These variables are passed to `AppDirs` to identify the proper state and
# configuration save locations.
APP_NAME = "firefly-cli"
APP_AUTHOR = "IRSA"

# Global configurations for `rich_click`
# A full list of options can be found at:
#     https://ewels.github.io/rich-click/documentation/formatting_and_styles/
# Default styles
rc.STYLE_OPTION = "bold cyan"
rc.STYLE_ARGUMENT = "bold cyan"
rc.STYLE_COMMAND = "bold cyan"
rc.STYLE_SWITCH = "bold green"
rc.STYLE_METAVAR = "bold yellow"
rc.STYLE_METAVAR_APPEND = "dim yellow"
rc.STYLE_METAVAR_SEPARATOR = "dim"
rc.STYLE_HEADER_TEXT = ""
rc.STYLE_EPILOG_TEXT = ""
rc.STYLE_FOOTER_TEXT = ""
rc.STYLE_USAGE = "yellow"
rc.STYLE_USAGE_COMMAND = "bold"
rc.STYLE_DEPRECATED = "red"
rc.STYLE_HELPTEXT_FIRST_LINE = ""
rc.STYLE_HELPTEXT = "dim"
rc.STYLE_OPTION_HELP = ""
rc.STYLE_OPTION_DEFAULT = "dim"
rc.STYLE_OPTION_ENVVAR = "dim yellow"
rc.STYLE_REQUIRED_SHORT = "red"
rc.STYLE_REQUIRED_LONG = "dim red"
rc.STYLE_OPTIONS_PANEL_BORDER = "dim"
rc.STYLE_OPTIONS_PANEL_BOX = "ROUNDED"
rc.ALIGN_OPTIONS_PANEL = "left"
rc.STYLE_OPTIONS_TABLE_SHOW_LINES = False
rc.STYLE_OPTIONS_TABLE_LEADING = 0
rc.STYLE_OPTIONS_TABLE_PAD_EDGE = False
rc.STYLE_OPTIONS_TABLE_PADDING = (0, 1)
rc.STYLE_OPTIONS_TABLE_BOX = ""
rc.STYLE_OPTIONS_TABLE_ROW_STYLES = None
rc.STYLE_OPTIONS_TABLE_BORDER_STYLE = None
rc.STYLE_COMMANDS_PANEL_BORDER = "dim"
rc.STYLE_COMMANDS_PANEL_BOX = "ROUNDED"
rc.ALIGN_COMMANDS_PANEL = "left"
rc.STYLE_COMMANDS_TABLE_SHOW_LINES = False
rc.STYLE_COMMANDS_TABLE_LEADING = 0
rc.STYLE_COMMANDS_TABLE_PAD_EDGE = False
rc.STYLE_COMMANDS_TABLE_PADDING = (0, 1)
rc.STYLE_COMMANDS_TABLE_BOX = ""
rc.STYLE_COMMANDS_TABLE_ROW_STYLES = None
rc.STYLE_COMMANDS_TABLE_BORDER_STYLE = None
rc.STYLE_COMMANDS_TABLE_COLUMN_WIDTH_RATIO = (None, None)
rc.STYLE_ERRORS_PANEL_BORDER = "red"
rc.STYLE_ERRORS_PANEL_BOX = "ROUNDED"
rc.ALIGN_ERRORS_PANEL = "left"
rc.STYLE_ERRORS_SUGGESTION = "dim"
rc.STYLE_ERRORS_SUGGESTION_COMMAND = "blue"
rc.STYLE_ABORTED = "red"
rc.WIDTH = int(os.getenv("TERMINAL_WIDTH")) if os.getenv("TERMINAL_WIDTH") else None
rc.MAX_WIDTH = int(os.getenv("TERMINAL_WIDTH")) if os.getenv("TERMINAL_WIDTH") else rc.WIDTH # noqa
rc.COLOR_SYSTEM = "auto"  # Set to None to disable colors
rc.FORCE_TERMINAL = True if os.getenv("GITHUB_ACTIONS") or os.getenv("FORCE_COLOR") or os.getenv("PY_COLORS") else None

# Fixed strings
rc.HEADER_TEXT = None
rc.FOOTER_TEXT = None
rc.DEPRECATED_STRING = "(Deprecated) "
rc.DEFAULT_STRING = "[default: {}]"
rc.ENVVAR_STRING = "[env var: {}]"
rc.REQUIRED_SHORT_STRING = "*"
rc.REQUIRED_LONG_STRING = "[required]"
rc.RANGE_STRING = " [{}]"
rc.APPEND_METAVARS_HELP_STRING = "({})"
rc.ARGUMENTS_PANEL_TITLE = "Arguments"
rc.OPTIONS_PANEL_TITLE = "Options"
rc.COMMANDS_PANEL_TITLE = "Commands"
rc.ERRORS_PANEL_TITLE = "Error"
rc.ERRORS_SUGGESTION = None  # Default: Try 'cmd -h' for help. Set to False to disable.
rc.ERRORS_EPILOGUE = None
rc.ABORTED_TEXT = "Aborted."

# Behaviours
rc.SHOW_ARGUMENTS = True  # Show positional arguments
rc.SHOW_METAVARS_COLUMN = True  # Show a column with the option metavar (eg. INTEGER)
rc.APPEND_METAVARS_HELP = False  # Append metavar (eg. [TEXT]) after the help text
rc.GROUP_ARGUMENTS_OPTIONS = False  # Show arguments with options instead of in own panel
rc.OPTION_ENVVAR_FIRST = False  # Show env vars before option help text instead of avert
rc.TEXT_MARKUP = "ansi"  # One of: "rich", "markdown", "ansi", None.
rc.USE_MARKDOWN_EMOJI = True  # Parse emoji codes in markdown :smile:
rc.COMMAND_GROUPS = {} # Define sorted groups of panels to display subcommands
rc.OPTION_GROUPS = {} # Define sorted groups of panels to display options and arguments
rc.USE_CLICK_SHORT_HELP = False  # Use click's default function to truncate help text
rc.TEXT_MARKUP = 'rich'
rc.STYLE_COMMANDS_TABLE_PAD_EDGE = True
rc.STYLE_OPTIONS_TABLE_SHOW_LINES = False




class FireflyCliConfig(BaseSettings):
    """
    Firefly CLI configuration class.

    This holds the configuration for the Firefly CLI.

    Attributes
    ----------
        servers: A list of saved Firefly servers.
        default_server: The default server to use. If not set, either the first
                        server in the list or the server specified in the
                        FIREFLY_URL environment variable will be used.
    """

    model_config = SettingsConfigDict(
        title="Firefly CLI Configuration",
        case_sensitive=False,
        env_prefix="FIREFLY_CLI_",
        env_file=".env",
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
        cli_parse_args=True,
    )

    servers: Dict[str, ParseResult]
    default_server: Optional[str] = Field(
        validation_alias=AliasChoices("i", "instance", "url", "URL")
    )

    @classmethod
    def create_default(cls, path: Path) -> "FireflyCliConfig":
        """
        Writes the default configuration to the user's configuration directory.
        and returns the default configuration object.
        """

        default_config = cls(
            servers={
                "irsa": urlparse("https://irsa.ipac.caltech.edu/irsaviewer"),
                "local": urlparse("http://localhost:8080/firefly"),
            },
            default_server="irsa",
        )

        config_str = tomlkit.dumps(default_config.model_dump(), sort_keys=True)

        with open(path, "w") as f:
            f.write(config_str)

        return default_config

    def save(self, path: Path):
        """
        Saves the configuration to the specified path.
        """

        config_str = tomlkit.dumps(self.model_dump(), sort_keys=True)

        with open(path, "w") as f:
            f.write(config_str)

    @classmethod
    def load(cls, path: Path) -> "FireflyCliConfig":
        """
        Loads the configuration from the specified path.
        """

        if path.parent.exists(
            follow_symlinks=True
        ) and path.exists(follow_symlinks=True):
            with open(path, "r") as f:
                config_str = f.read()
            config_dict = tomlkit.loads(config_str)
            config = FireflyCliConfig.model_validate(config_dict)

        else:
            os.makedirs(path.parent, exist_ok=True)
            config = FireflyCliConfig.create_default(path)

        return config

class FireflyCliState(BaseModel):
    """
    Firefly CLI state class.

    This holds the persistent state for the Firefly CLI.

    Attributes
    ----------
        last_server: The last server used.
        last_url: The last URL used.
        token: The last token used.
        expires: The token expiration time.
    """

    last_server: Optional[str] = None
    last_url: Optional[str] = None
    token: Optional[str] = None
    expires: Optional[datetime.datetime] = None

    @classmethod
    def default(cls) -> "FireflyCliState":
        """
        Checks the environment if the state is valid and returns a new state if it is not.
        """
        load_dotenv()
        return cls()

    @staticmethod
    def _handle_invalid_state(current_state: Optional["FireflyCliState"] = None, new_state: Optional["FireflyCliState"] = None) -> "FireflyCliState":
        class AllChoices(StrEnum):
            exit = "e"
            reset = "r"
            adopt = "a"
            previous = "p"

        click.secho("Uh oh! The state seems to have been corrupted!", bold=True, fg="white")
        if current_state is None and new_state is None:
            click.secho("You can either exit now to manually fix the state or reset to an empty state.", fg="white")
            choices_prompt = "Would you like to [e]xit or [r]eset to an empty state?"
            choices = [AllChoices.exit, AllChoices.reset]
        elif current_state is None and new_state is not None:
            click.secho("You can either forcibly adopt the new state, or reset to an empty state.", fg="white")
            click.echo()
            click.secho("New state:", bold=True, fg="yellow")
            click.echo(new_state.model_dump())
            click.echo()
            choices_prompt = "Would you like to [a]dopt the new state, or [r]eset to an empty state?"
            choices = [AllChoices.adopt, AllChoices.reset]
        elif new_state is None and current_state is not None:
            click.secho("You can either keep the previous state, or reset to an empty state.", fg="white")
            click.echo()
            click.secho("Previous state:", bold=True, fg="yellow")
            click.echo(current_state.model_dump())
            click.echo()
            choices_prompt = "Would you like to keep the [p]revious state, or [r]eset to an empty state?"
            choices = [AllChoices.previous, AllChoices.reset]
        else:
            assert current_state is not None and new_state is not None
            click.secho("You can either keep the previous state, adopt the new state, or reset to an empty state.", fg="white")
            click.echo()
            click.secho("Previous state:", bold=True, fg="yellow")
            click.echo(current_state.model_dump())
            click.echo()
            click.secho("New state:", bold=True, fg="yellow")
            click.echo(new_state.model_dump())
            click.echo()
            choices_prompt = "Would you like to keep the [p]revious state, [a]dopt the new state, or [r]eset to an empty state?"
            choices = [AllChoices.previous, AllChoices.adopt, AllChoices.reset]

        rollback: str = click.prompt(
            choices_prompt,
            type=click.Choice(choices, case_sensitive=False),
            default=AllChoices.reset,
            show_choices=True,
            show_default=True,
        )

        match AllChoices(rollback.lower()):
            case AllChoices.previous:
                assert current_state is not None
                return current_state
            case AllChoices.adopt:
                assert new_state is not None
                return new_state
            case AllChoices.reset:
                return FireflyCliState()
            case AllChoices.exit:
                click.secho("Exiting...", bold=True, fg="white")
                raise click.Abort()

    def update(
        self,
        state: Optional["FireflyCliState"] = None,
        path: Optional[Path | str] = None,
        last_server: Optional[str] = None,
        last_url: Optional[str] = None,
        token: Optional[str] = None,
        expires: Optional[datetime.datetime | datetime.timedelta] = None,
        **kwargs
    ):
        """
        Updates the state with the current client information.
        """

        if state is not None:
            current_state = self
            try:
                self = FireflyCliState.model_validate(state.model_dump().update(self.model_dump()))
            except ValidationError:
                self = self._handle_invalid_state(current_state, state)
            return state

        if path is not None:
            state = FireflyCliState.load(Path(path))
            current_state = self
            try:
                self = FireflyCliState.model_validate(state.model_dump().update(self.model_dump()))
            except ValidationError:
                self = self._handle_invalid_state(current_state, state)
            return state

        if last_server is not None:
            self.last_server = last_server
        if last_url is not None:
            self.last_url = last_url
        if token is not None:
            self.token = token
        if expires is not None:
            if isinstance(expires, datetime.timedelta):
                if self.expires is None:
                    expires = datetime.datetime.now() + expires
                else:
                    expires = self.expires + expires
            self.expires = expires

    def save(self, path: Path):
        """
        Saves the state to the specified path.
        """

        config_str = json.dumps(self.model_dump())

        with open(path, "w") as f:
            f.write(config_str)

    @classmethod
    def load(cls, path: Path) -> "FireflyCliState":
        """
        Loads the state from the specified path.
        """

        if path.parent.exists(
            follow_symlinks=True
        ) and path.exists(follow_symlinks=True):
            with open(path, "r") as f:
                state_str = f.read()
            state_dict = json.loads(state_str)
            try:
                state = FireflyCliState.model_validate(state_dict)
            except ValidationError:
                state = cls._handle_invalid_state()
        else:
            os.makedirs(path.parent, exist_ok=True)
            config = FireflyCliConfig.create_default(path)
            state = FireflyCliState(last_server=config.default_server, last_url=config.servers[config.default_server], token=None, expires=None)

        return state


class FireflyCliContext(BaseModel):
    """
    Firefly CLI context class.

    This holds the configuration context for the Firefly CLI.
    The configuration is loaded from the user's configuration directory
    and can be modified by the user.

    Attributes
    ----------
        config_file: The path specified by the environment variable FIREFLY_CLI_CONFIG_FILE, if present.
        state_file: The path specified by the environment variable FIREFLY_CLI_STATE_FILE, if present.
        files: The application directories.
        config: The current configuration.
        state: The current state, if any.
    """

    files: AppDirs

    def __init__(self):
        load_dotenv()
        self.files = AppDirs(app_name, app_author)
        self.state = None

    @property
    def config(self) -> FireflyCliConfig:
        if self.config_file.parent.exists(
            follow_symlinks=True
        ) and self.config_file.exists(follow_symlinks=True):
            with open(self.config_file, "r") as f:
                config_str = f.read()
            config_dict = tomlkit.loads(config_str)
            config = FireflyCliConfig.model_validate(config_dict)

        else:
            os.makedirs(self.config_file.parent, exist_ok=True)
            config = FireflyCliConfig.create_default(self.config_file)

        return config

    @property
    def state(self) ->

    @property
    def config_file(self) -> Path:
        if os.environ.get("FIREFLY_CLI_CONFIG_FILE"):
            config_file = Path(os.environ["FIREFLY_CLI_CONFIG_FILE"])
            if config_file.suffix != ".toml":
                click.echo(
                    f"{click.style('ERROR', fg='red', bold=True)}: Unable to parse the CLI configuration file."
                    "Please specify a valid TOML file path in the 'FIREFLY_CLI_CONFIG_FILE' environment variable."
                )
                raise click.Abort()
            return config_file
        else:
            return Path(self.files.user_config_dir).joinpath("config.toml")

    @property
    def state_file(self) -> Path:
        if os.environ.get("FIREFLY_CLI_STATE_FILE"):
            state_file = Path(os.environ["FIREFLY_CLI_STATE_FILE"])
            if state_file.suffix != ".json":
                click.echo(
                    f"{click.style('ERROR', fg='red', bold=True)}: Unable to parse the CLI state file."
                    "Please specify a valid JSON file path in the 'FIREFLY_CLI_STATE_FILE' environment variable."
                )
                raise click.Abort()
            return state_file
        else:
            return Path(self.files.user_config_dir).joinpath("config.toml")


@click.command()
@from_pydantic("config", FireflyCliConfig)
def firefly(ctx: click.Context, config: FireflyCliConfig):
    """Entry point for the Firefly CLI."""

    if not click:
        raise ImportError(
            "Please install the click package to use the Firefly CLI. "
            "You can install it with 'pip install firefly_client[cli]'."
        )

    ctx.obj = FireflyCliContext()
