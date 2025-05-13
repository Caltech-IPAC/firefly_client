"""Firefly CLI configuration objects

This module handles all configuration objects for the Firefly CLI.
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

import base64
import datetime
import json
import os
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from firefly_client.cli.utils import error

from firefly_client.firefly_client import FireflyClient

try:
    import rich_click as click
    from appdirs import AppDirs
    from dotenv import load_dotenv
    from git import exc, Repo
    from mashumaro.mixins.json import DataClassJSONMixin
    from mashumaro.mixins.toml import DataClassTOMLMixin
except ImportError:
    raise ImportError(
        "The Firefly CLI optional packages have not been installed."
        "You can install it with 'pip install firefly_client[cli]'."
    )

# These variables are passed to `AppDirs` to identify the proper state and
# configuration save locations.
APP_NAME = "firefly-cli"
APP_AUTHOR = "IRSA"


@dataclass
class FireflyCliConfig(DataClassTOMLMixin):
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

    servers: Dict[str, str]
    default_server: str

    @classmethod
    def create_default(cls, path: Path) -> "FireflyCliConfig":
        """
        Writes the default configuration to the user's configuration directory.
        and returns the default configuration object.
        """

        default_config = cls(
            servers={
                "irsa": "https://irsa.ipac.caltech.edu/irsaviewer",
                "local": "http://localhost:8080/firefly",
            },
            default_server="irsa",
        )

        config_str = default_config.to_toml()

        with open(path, "w") as f:
            f.write(config_str)

        return default_config

    def save(self, path: Path):
        """
        Saves the configuration to the specified path.
        """

        config_str = self.to_toml()

        with open(path, "w") as f:
            f.write(config_str)

    @classmethod
    def load(cls, path: Path) -> "FireflyCliConfig":
        """
        Loads the configuration from the specified path.
        """

        if (
            path.parent.exists(follow_symlinks=True)
            and path.exists(follow_symlinks=True)
            and path.is_file(follow_symlinks=True)
        ):
            with open(path, "r") as f:
                config_str = f.read()
            config = cls.from_toml(config_str)
        else:
            os.makedirs(path.parent, exist_ok=True)
            config = cls.create_default(path)

        return config


@dataclass
class FireflyToken(DataClassJSONMixin):
    """Firefly CLI token.

    This holds the token data for a CLI token.

    Attributes
    ----------
    host: The hostname the token was generated on.
    user: The username of the current user.
    expiry: The expiration time for the token.
    """

    host: str
    user: str
    expiry: datetime.datetime

    @classmethod
    def default(cls) -> "FireflyToken":
        host = socket.gethostname()
        user = os.getlogin()
        expiry = datetime.datetime.now() + datetime.timedelta(
            weeks=0.0,
            days=5.0,
            hours=8.0,
            minutes=30.0,
            seconds=0.0,
            milliseconds=0.0,
            microseconds=0.0,
        )
        return FireflyToken(host=host, user=user, expiry=expiry)

    def __str__(self) -> str:
        return self.b64encode()

    def b64encode(self) -> str:
        json_str = json.dumps(self.to_dict())
        encoded = base64.b64encode(bytes(json_str, "utf-8"))
        return encoded.decode("utf-8")

    @classmethod
    def b64decode(cls, token: str) -> "FireflyToken":
        decoded_str = base64.b64decode(token).decode()
        return FireflyToken.from_json(decoded_str)


@dataclass
class FireflyCliState(DataClassTOMLMixin):
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

    last_server: str
    last_url: str
    token: str
    expires: datetime.datetime

    @classmethod
    def default(
        cls,
        config: Optional[FireflyCliConfig],
        last_server: Optional[str],
        last_url: Optional[str],
    ) -> "FireflyCliState":
        """
        Checks the environment if the state is valid and returns a new state if it is not.
        """
        load_dotenv()
        token = FireflyToken.default()
        if config is not None and last_server is not None:
            last_url = config.servers[last_server]
        elif config is not None:
            last_server = config.default_server
            last_url = str(config.servers[config.default_server])
        elif last_server is None or last_url is None:
            error("Unable to load the session state. Unknown configuration.")
            raise click.Abort()
        return cls(
            last_server=last_server,
            last_url=last_url,
            token=str(token),
            expires=token.expiry,
        )

    def save(self, path: Path):
        """
        Saves the state to the specified path.
        """

        config_str = self.to_toml()

        with open(path, "w") as f:
            f.write(config_str)

    @classmethod
    def load(cls, path: Path, config: Optional[FireflyCliConfig]) -> "FireflyCliState":
        """
        Loads the state from the specified path.
        """

        if (
            path.parent.exists(follow_symlinks=True)
            and path.exists(follow_symlinks=True)
            and path.is_file(follow_symlinks=True)
        ):
            with open(path, "r") as f:
                state_str = f.read()
            state = cls.from_toml(state_str)
        else:
            os.makedirs(path.parent, exist_ok=True)
            if config is None:
                config = FireflyCliConfig.create_default(path)
            if config.servers[config.default_server] is None:
                error("The default server url is not defined in the config file.")
                raise click.Abort()
            token = FireflyToken.default()
            state: FireflyCliState = cls(
                last_server=config.default_server,
                last_url=str(config.servers[config.default_server]),
                token=str(token),
                expires=token.expiry,
            )
            state.save(path)

        return state


@dataclass
class FireflyCliSession(DataClassTOMLMixin):
    """
    Firefly CLI session class.

    This holds the state of the most recent CLI session.
    """

    uploaded_files: list[str]

    @classmethod
    def default(cls) -> "FireflyCliSession":
        return cls(uploaded_files=[])

    def save(self, path: Optional[Path]):
        path = path if path is not None else self.dir
        with open(path, "w") as f:
            f.write(self.to_toml())

    @classmethod
    def load(cls, path: Optional[Path]) -> "FireflyCliSession":
        """
        Loads the session data.
        """
        if path is None:
            try:
                dir = Repo(
                    os.getcwd(), search_parent_directories=True, expand_vars=True
                ).git_dir
                path = Path(dir)
            except exc.InvalidGitRepositoryError:
                path = Path.home()
            path = path / ".firefly.toml"
        if not path.exists():
            session = cls.default()
            session.dir = path
            session.save(None)
        else:
            with open(path, "r") as f:
                session_str = f.read()
            session = cls.from_toml(session_str)
            session.dir = path
        return session

    @property
    def dir(self):
        if self._dir is None:
            try:
                dir = Repo(
                    os.getcwd(), search_parent_directories=True, expand_vars=True
                ).git_dir
                self._dir = Path(dir)
            except exc.InvalidGitRepositoryError:
                self._dir = Path.home()
        return self._dir

    @dir.setter
    def dir(self, dir: Path):
        self._dir = dir


class FireflyCliContext:
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

    def __init__(
        self,
        config: Optional[FireflyCliConfig],
        state: Optional[FireflyCliState],
        channel: Optional[int | str],
        html_file: str,
        print_url: bool,
    ):
        load_dotenv()
        self.files = AppDirs(APP_NAME, APP_AUTHOR)
        self._config: FireflyCliConfig | None = config
        self._config_file: Path | None = None
        self._state: FireflyCliState | None = state
        self._state_file: Path | None = None
        if channel is not None:
            self._override = str(channel)
        self._html_file = html_file
        self._print_url = print_url
        self._fc = None

    @property
    def fc(self) -> FireflyClient:
        if self._fc is None:
            self._channel = (
                self._override if self._override is not None else self.state.token
            )
            self._fc = FireflyClient.make_client(
                url=self.state.last_url,
                channel_override=self._channel,
                html_file=self._html_file,
                launch_browser=False,
                verbose=False,
            )
            if self._print_url:
                click.echo(
                    f"{click.style('You can access your session with the Firefly server at', fg='white', bold=False)}: {click.style(self._fc.get_firefly_url(self._channel), fg='cyan', bold=True, underline=True)}"
                )
            else:
                click.launch(self._fc.get_firefly_url(self._channel))
        return self._fc

    @property
    def channel(self) -> str:
        return self._channel

    @property
    def config(self) -> FireflyCliConfig:
        if self._config is None:
            if self.config_file.parent.exists(
                follow_symlinks=True
            ) and self.config_file.exists(follow_symlinks=True):
                config = FireflyCliConfig.load(self.config_file)

            else:
                os.makedirs(self.config_file.parent, exist_ok=True)
                config = FireflyCliConfig.create_default(self.config_file)

            self._config = config
        return self._config

    @property
    def state(self) -> FireflyCliState:
        if self._state is None:
            if self.state_file.parent.exists(
                follow_symlinks=True
            ) and self.state_file.exists(follow_symlinks=True):
                state = FireflyCliState.load(self.state_file, self.config)

            else:
                os.makedirs(self.state_file.parent, exist_ok=True)
                state = FireflyCliState.load(self.state_file, self.config)

            self._state = state
        return self._state

    @property
    def config_file(self) -> Path:
        if self._config_file is None:
            if os.environ.get("FIREFLY_CLI_CONFIG_FILE"):
                config_file = Path(os.environ["FIREFLY_CLI_CONFIG_FILE"])
                if config_file.suffix != ".toml":
                    error(
                        "Unable to parse the CLI configuration file. Please specify a valid TOML file path in the 'FIREFLY_CLI_CONFIG_FILE' environment variable."
                    )
                    raise click.Abort()
                self._config_file = config_file
            else:
                config_file = Path(self.files.user_config_dir).joinpath("config.toml")
                self._config_file = config_file
        return self._config_file

    @property
    def state_file(self) -> Path:
        if self._state_file is None:
            if os.environ.get("FIREFLY_CLI_STATE_FILE"):
                state_file = Path(os.environ["FIREFLY_CLI_STATE_FILE"])
                if state_file.suffix != ".json":
                    error(
                        "Unable to parse the CLI state file. Please specify a valid JSON file path in the 'FIREFLY_CLI_STATE_FILE' environment variable."
                    )
                    raise click.Abort()
                self._state_file = state_file
            else:
                self._state_file = Path(self.files.user_state_dir).joinpath(
                    "state.json"
                )
        return self._state_file

    def save_config(self):
        """Saves the configuration file."""
        self.config.save(self.config_file)

    def save_state(self):
        """Save the state file."""
        self.state.save(self.state_file)

    def save(self):
        """Save the configuration and state files"""
        self.save_config()
        self.save_state()

    def connect(self, server: str):
        """Connect to a server"""
        if not server.startswith("http") and server not in self.config.servers:
            error(f"Unknown server {server}")
            raise click.Abort()
        self._fc = None
        if server.startswith("http"):
            last_server = "temp-session"
            last_url = server
            for s, u in self.config.servers.items():
                if server == u:
                    last_server = s
                    last_url = u
            self._state = FireflyCliState.default(
                self.config,
                last_server,
                last_url,
            )
        else:
            self._state = FireflyCliState.default(self.config, server, None)
        self.save_state()
