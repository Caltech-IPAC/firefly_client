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

import os
from typing import Optional

from firefly_client.cli.config import FireflyCliContext
from firefly_client.cli.utils import context

try:
    import rich_click as click
    from rich_click import rich_click as rc
except ImportError:
    raise ImportError(
        "The Firefly CLI optional packages have not been installed."
        "You can install it with 'pip install firefly_client[cli]'."
    )

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
rc.WIDTH = (
    int(os.getenv("TERMINAL_WIDTH", ""))
    if os.getenv("TERMINAL_WIDTH") is not None
    and os.getenv("TERMINAL_WIDTH", "").isnumeric()
    else None
)
rc.MAX_WIDTH = int(rc.WIDTH) if rc.WIDTH is not None else None
rc.COLOR_SYSTEM = "auto"  # Set to None to disable colors
rc.FORCE_TERMINAL = (
    True
    if os.getenv("GITHUB_ACTIONS") or os.getenv("FORCE_COLOR") or os.getenv("PY_COLORS")
    else None
)

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
rc.GROUP_ARGUMENTS_OPTIONS = (
    False  # Show arguments with options instead of in own panel
)
rc.OPTION_ENVVAR_FIRST = False  # Show env vars before option help text instead of avert
rc.TEXT_MARKUP = "ansi"  # One of: "rich", "markdown", "ansi", None.
rc.USE_MARKDOWN_EMOJI = True  # Parse emoji codes in markdown :smile:
rc.COMMAND_GROUPS = {}  # Define sorted groups of panels to display subcommands
rc.OPTION_GROUPS = {}  # Define sorted groups of panels to display options and arguments
rc.USE_CLICK_SHORT_HELP = False  # Use click's default function to truncate help text
rc.TEXT_MARKUP = "rich"
rc.STYLE_COMMANDS_TABLE_PAD_EDGE = True
rc.STYLE_OPTIONS_TABLE_SHOW_LINES = False


@click.group()
@click.option("--channel", type=int, required=False, multiple=False, nargs=1)
@click.option(
    "--html-file",
    type=str,
    nargs=1,
    required=False,
    default="irsaviewer.html",
    multiple=False,
    show_default=True,
)
@click.option(
    "--print-url",
    type=bool,
    nargs=1,
    multiple=False,
    is_flag=True,
    default=False,
    flag_value=True,
)
@click.pass_context
def firefly(
    ctx: click.Context,
    channel: Optional[int],
    html_file: str = "irsaviewer.html",
    print_url: bool = False,
):
    """CLI tool for interacting with Firefly servers."""

    if not click:
        raise ImportError(
            "The Firefly CLI optional packages have not been installed."
            "You can install it with 'pip install firefly_client[cli]'."
        )

    ctx.obj = FireflyCliContext(None, None, channel, html_file, print_url)


@firefly.command()
@click.argument("server", type=str, required=False, nargs=1)
@click.pass_context
def connect(ctx: click.Context, server: Optional[str]):
    """Connect to a firefly server"""
    ctx = context(ctx)
    if server is not None:
        ctx.obj.connect(server)
    else:
        ctx.obj.connect(ctx.obj.config.default_server)
