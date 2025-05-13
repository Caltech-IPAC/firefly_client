import os
from glob import iglob
from pathlib import Path
from tempfile import TemporaryFile
from typing import Optional

from firefly_client.cli.entrypoint import firefly

from firefly_client.cli.utils import context, filetable

try:
    import rich_click as click
except ImportError:
    raise ImportError(
        "The Firefly CLI optional packages have not been installed."
        "You can install it with 'pip install firefly_client[cli]'."
    )


@firefly.command()
@click.option(
    "--remote-path",
    type=str,
    required=False,
    nargs=1,
    multiple=False,
    short_help="Remote access path to the data",
    help="The path where the Firefly server can access the data. Assumes that the passed files will be at this path if '--local-path' is not specified.",
)
@click.option(
    "--local-path",
    type=str,
    required=False,
    nargs=1,
    multiple=False,
    short_help="Local access path to the data",
    help="The local path segment. This path segment is removed from the paths when sending them to the Firefly server. If '--remote-path' is specified, the local path segment is replaced with the remote path.",
)
@click.option(
    "--sort",
    "-s",
    type=bool,
    nargs=1,
    multiple=False,
    is_flag=True,
    default=False,
    flag_value=True,
    short_help="Sort files",
    help="If specified, the file paths will be alphabetically sorted before being uploaded to the Firefly server.",
)
@click.option(
    "--recursive",
    "-r",
    type=bool,
    nargs=1,
    multiple=False,
    is_flag=True,
    default=False,
    flag_value=True,
    short_help="Whether to recurse directories.",
    help="If specified, all glob patterns and directories will be recursively searched.",
)
@click.argument(
    "file",
    type=click.Path(
        file_okay=True, dir_okay=True, readable=True, allow_dash=True, path_type=str
    ),
    required=True,
    nargs=-1,
)
@click.pass_context
def open(
    ctx: click.Context,
    remote_path: Optional[str],
    local_path: Optional[str],
    sort: bool,
    recursive: bool,
    file: tuple[str, ...],
):
    """Open any supported data on the Firefly server.

    If multiple files, a directory, or a glob pattern is specified, a table of
    files will be uploaded to the Firefly server. Otherwise, the file will be
    parsed and uploaded as is.
    """
    ctx = context(ctx)
    files: set[Path] | list[Path] = set()
    if len(file) == 1 and file[0] == "-":
        with click.open_file(file[0], mode="rb") as f:
            d = os.dup(f.fileno())
            os.lseek(d, 0, 0)
            head = os.read(d, 6)
            os.close(d)
            if head == b"SIMPLE":
                rmt = ctx.obj.fc.upload_data(f, "FITS")
            else:
                rmt = ctx.obj.fc.upload_data(f, "UNKNOWN")
    else:
        for f in file:
            if "*" in file:
                for g in iglob(f, recursive=recursive):
                    p = Path(g)
                    if p.is_file():
                        files.add(p)
            elif Path(f).is_dir():
                for g in iglob("**", root_dir=f, recursive=recursive):
                    p = Path(g)
                    if p.is_file():
                        files.add(p)
            elif Path(f).is_file():
                p = Path(f)
                files.add(p)
            else:
                click.echo(
                    f"Unable to parse path '{file}'. Could not determine whether it is a file, dir, or glob pattern.",
                    err=True,
                    color=True,
                )
                raise click.Abort()
        if len(files) != 1:
            if sort:
                files = sorted(files)

            files_data = filetable(files, local_path, remote_path)
            click.secho("Uploading files:", bold=True)
            print(files_data)
            with TemporaryFile(mode="w+t", suffix=".csv") as temp:
                files_data.write_csv(temp)
                rmt = ctx.obj.fc.upload_file(temp)
        else:
            rmt = ctx.obj.fc.upload_file(files.pop())
