"""
Utilities for common patters within the CLI logic.
"""

import click

from firefly_client.cli.config import FireflyCliContext


def context(ctx: click.Context) -> click.Context:
    """Verifies the command context

    Parameters
    ----------
    ctx : `click.Context`
        The command context

    Raises
    ------
    `RuntimeError` :
        When the context is not initialized properly.

    Returns
    -------
    ctx : `click.Context`
        The verified context object
    """
    if not isinstance(ctx.obj, FireflyCliContext):
        raise RuntimeError(
            "Uh Oh! Something isn't right here... Please run the command again."
        )
    else:
        return ctx


def check_server(ctx: click.Context, server: str):
    """Checks whether a server exists or not in the configuration.

    Parameters
    ----------
    ctx : `click.Context`
        The context object holding the servers dict.
    server : `str`
        The name of the server

    Raises
    ------
    `click.BadParameter`
        Raised when the server is not found.
    """
    if server not in ctx.obj.config.servers:
        raise click.BadParameter(
            f"Server '{server}' not found.", param_hint="server", ctx=ctx
        )
