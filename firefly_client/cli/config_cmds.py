from typing import Optional

from firefly_client.cli.entrypoint import firefly
from firefly_client.cli.utils import check_server, context

try:
    import rich_click as click
except ImportError:
    raise ImportError(
        "The Firefly CLI optional packages have not been installed."
        "You can install it with 'pip install firefly_client[cli]'."
    )


@firefly.group()
def servers():
    """Commands for inspecting and modifying the configuration."""
    pass


@servers.command()
@click.argument("server", type=str, required=True, nargs=1)
@click.pass_context
def get(ctx: click.Context, server: str):
    """Get the URL for a saved server."""
    ctx = context(ctx)
    check_server(ctx, server)
    click.echo(f"{click.style(ctx.obj.config.servers[server], fg='cyan', bold=True)}")


@servers.command()
@click.pass_context
def ls(ctx: click.Context):
    """List saved servers and their URLs"""
    ctx = context(ctx)
    for server, url in ctx.obj.config.servers.items():
        click.echo(
            f"{click.style(server, fg='cyan', bold=True)}: {click.style(url, fg='magenta')}"
        )


@servers.command(name="set")
@click.argument("server", type=str, required=True, nargs=1)
@click.argument("url", type=str, required=True, nargs=1)
@click.pass_context
def set_url(ctx: click.Context, server: str, url: str):
    """Set the URL of a server."""
    ctx = context(ctx)
    check_server(ctx, server)
    ctx.obj.config.servers[server] = url
    ctx.obj.save_config()


@servers.command()
@click.argument("server", type=str, required=True, nargs=1)
@click.argument("url", type=str, required=True, nargs=1)
@click.pass_context
def add(ctx: click.Context, server: str, url: str):
    """Add a server to the saved configuration."""
    ctx = context(ctx)
    if server in ctx.obj.config.servers:
        raise click.BadParameter(
            f"Server '{server}' already defined. Please use 'config set ...'.",
            param_hint="server",
            ctx=ctx,
        )
    ctx.obj.config.servers[server] = url
    ctx.obj.save_config()


@servers.command()
@click.argument("server", type=str, required=False)
@click.pass_context
def default(ctx: click.Context, server: Optional[str]):
    """Get or set the default server."""
    ctx = context(ctx)
    if server is not None:
        check_server(ctx, server)
        ctx.obj.config.default_server = server
        ctx.obj.save_config()
    else:
        click.echo(
            f"{click.style(ctx.obj.config.default_server, fg='cyan', bold=True)}: {click.style(ctx.obj.config.servers[ctx.obj.config.default_server], fg='magenta')}"
        )
