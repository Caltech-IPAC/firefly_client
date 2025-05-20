import os
from glob import iglob
from pathlib import Path
from tempfile import TemporaryFile
from typing import Iterable, Optional

from firefly_client.cli.entrypoint import firefly

from firefly_client.cli.utils import context, filetable
from firefly_client.firefly_client import FireflyClient

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
    if len(file) == 1 and file[0] == "-":
        rmt = open_file(str(file[0]), ctx.obj.fc)
    else:
        rmt = open_files(ctx.obj.fc, file, sort, recursive, local_path, remote_path)
    ctx.obj.session.uploaded_files.append(rmt)


def open_file(file: str, fc: FireflyClient) -> str:
    with click.open_file(file, mode="rb") as f:
        d = os.dup(f.fileno())
        os.lseek(d, 0, 0)
        head = os.read(d, 6)
        os.close(d)
        if head == b"SIMPLE":
            rmt = fc.upload_data(f, "FITS")
        else:
            rmt = fc.upload_data(f, "UNKNOWN")
    return rmt


def open_files(
    fc: FireflyClient,
    files: Iterable[str],
    sort: bool,
    recursive: bool,
    local_path: Optional[str],
    remote_path: Optional[str],
) -> str:
    files_set: set[Path] | list[Path] = set()
    for f in files:
        files_set.update(parse_file(f, recursive))
    if len(files_set) != 1:
        if sort:
            files_set = sorted(files_set)

        files_data = filetable(files_set, local_path, remote_path)
        click.secho("Uploading files:", bold=True)
        print(files_data)
        with TemporaryFile(mode="w+t", suffix=".csv") as temp:
            files_data.write_csv(temp)
            rmt = fc.upload_file(temp)
    else:
        rmt = fc.upload_file(files_set.pop())
    return rmt


def parse_file(f: str, recursive: bool) -> set[Path]:
    files: set[Path] = set()
    if "*" in f:
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
            f"Unable to parse path '{f}'. Could not determine whether it is a file, dir, or glob pattern.",
            err=True,
            color=True,
        )
        raise click.Abort()
    return files
