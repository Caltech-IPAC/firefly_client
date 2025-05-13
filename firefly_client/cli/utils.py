"""
Utilities for common patters within the CLI logic.
"""

import os
from pathlib import Path
from typing import Optional

import click
import polars as pl
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


def format_path(
    local_path: Optional[str], remote_path: Optional[str], file: Path
) -> Path:
    if remote_path is not None:
        if local_path is not None:
            f = str(file)
            f = f.replace(local_path, remote_path)
            f = os.path.realpath(f)
            return Path(f)
        name = file.name
        f = os.path.realpath(f"{remote_path}/{name}")
        return Path(f)
    elif local_path is not None:
        f = str(file)
        f = f.replace(local_path, "")
        f = os.path.realpath(f)
        return Path(f)
    else:
        return file


def error(msg: str):
    click.echo(
        f"{click.style('ERROR', fg='red', bold=True)}: {click.style(msg, fg='white', bold=False)}"
    )


def warn(msg: str):
    click.echo(
        f"{click.style('WARNING', fg='yellow', bold=True)}: {click.style(msg, fg='white', bold=False)}"
    )


def filetable(
    files: list[Path] | set[Path], local_path: Optional[str], remote_path: Optional[str]
) -> pl.DataFrame:
    """Create a table of files.

    Formats a list or set of files into an uploadable table of files.

    Parameters
    ----------
    files : `list[pathlib.Path]` or `set[pathlib.Path]`
        The files to include in the table
    local_path : `str`, optional
        The local path segment of the file paths
    remote_path : `str`, optional
        The remote access path of the files

    Returns
    -------
    files : `polars.DataFrame`
        A table of files ready for upload to the server
    """
    file_nums: list[int] = []
    file_names: list[str] = []
    file_paths: list[str] = []

    for i, f in enumerate(files):
        f = format_path(local_path, remote_path, f)
        file_nums.append(i)
        file_names.append(f.name)
        file_paths.append(f.as_uri())

    files_data = pl.DataFrame(
        {
            "number": file_nums,
            "name": file_names,
            "path": file_paths,
        }
    )
    return files_data
