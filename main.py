import asyncio
import shutil
from pathlib import Path
import logging

import rich.spinner
from playwright.async_api import Page
from rich.logging import RichHandler

import config

import click

import ica_runner
from citrix_web import citrix_login, load_apps
from context import Context
from ica_runner import run_ica
from utils import coro

console = rich.console.Console()
logger = logging.getLogger(__name__)


@click.group()
# @click.option('-c', '--config-path', help='config ini file path', default='.secrets.ini')
@click.pass_context
def cli(click_ctx):
    logging.basicConfig(
        level=logging.NOTSET,
        format='[%(name)s] %(message)s',
        handlers=[RichHandler(rich_tracebacks=True, console=console)]
    )

    click_ctx.obj = {
        'app_ctx': Context(console)
    }


@cli.command()
@click.option('--app-name', type=str, default='Remote Desktop Manager')
@click.pass_context
@coro
async def start(click_ctx, app_name) -> None:
    app_ctx = click_ctx.obj['app_ctx']
    username = config.get_config('username')
    password = config.get_config('password')
    async with citrix_login(app_ctx, username, password) as page_app:
        page_app: Page

        app_map = await load_apps(app_ctx, page_app)

        if app_name not in app_map:
            raise ValueError(f'Not found app named "{app_name}"')

        for _ in range(10):

            with console.status(f'[bold blue]Downloading app "{app_name}"...', spinner='line') as status:
                async with page_app.expect_download() as download_info:
                    console.log('Locating app...')
                    await app_map[app_name].locator('.storeapp-details-link').click()
                download = await download_info.value
                # waits for download to complete
                console.log(f'Downloading app (from "{download.url}")...')
                path = await download.path()
                console.log('Done')

            console.log(f'App downloaded to "{path}"')
            dst = Path(r'C:\Users\wenop\OneDrive\Desktop')
            _ica = dst / 'start.ica'
            shutil.copy(path, _ica)
            ica_runner.run_ica(_ica)
            is_successful, reason = ica_runner.check(app_name)

            if is_successful:
                break

            console.log(f'Launch failed: {reason}')
            console.log(f'Sleep for some time and retry "{app_name}"...')
            await asyncio.sleep(20)


@cli.command()
@click.pass_context
@coro
async def list_apps(click_ctx):
    app_ctx = click_ctx.obj['app_ctx']
    username = config.get_config('username')
    password = config.get_config('password')
    async with citrix_login(app_ctx, username, password) as page_app:
        app_map = await load_apps(app_ctx, page_app)
        return list(app_map.keys())


if __name__ == '__main__':
    cli()
