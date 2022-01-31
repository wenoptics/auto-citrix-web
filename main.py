import asyncio
import shutil
from pathlib import Path
import logging

import click
import rich.spinner
from playwright.async_api import Page
from rich.logging import RichHandler


import config
from citrix_web import citrix_login, load_apps
from context import Context
import ica_runner
from utils import coro

console = rich.console.Console()
logger = logging.getLogger(__name__)


@click.group()
@click.option('--debug', help='Use debug mode. The browser will be visible', is_flag=True)
# @click.option('-c', '--config-path', help='config ini file path', default='.secrets.ini')
@click.pass_context
def cli(click_ctx, debug: bool = False):
    logging.basicConfig(
        level=logging.NOTSET,
        format='[%(name)s] %(message)s',
        handlers=[RichHandler(rich_tracebacks=True, console=console)]
    )

    click_ctx.obj = {
        'app_ctx': Context(console),
        'is_debug': debug
    }


@cli.command()
@click.option('--app-name', type=str, default='Remote Desktop Manager',
              help='The app name to start')
@click.option('--retry', type=int, default=10,
              help='Retry times. 0 to disable retry')
@click.option('--retry-delay', type=int, default=30,
              help='Retry delay in seconds')
@click.pass_context
@coro
async def start(click_ctx, app_name, retry: int, retry_delay: int) -> None:
    app_ctx = click_ctx.obj['app_ctx']
    in_headless = not click_ctx.obj['is_debug']
    username = config.get_config('USERNAME')
    password = config.get_config('PASSWORD')
    url = config.get_config('CITRIX_URL')
    async with citrix_login(app_ctx, url, username, password, headless=in_headless) as page_app:
        page_app: Page

        app_map = await load_apps(app_ctx, page_app)

        if app_name not in app_map:
            raise ValueError(f'Not found app named "{app_name}"')

        for i in range(retry):

            console.log('-'*20)
            console.log(f'[{i+1}/{retry}] try...')

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
            ica_runner.run_ica(_ica, config.get_config('ICA_RUNNER', sec='config'))
            is_successful, reason = await ica_runner.check(app_ctx, app_name)

            if is_successful:
                console.log(f'App "{app_name}" launched successfully ({reason})')
                break

            console.log(f'Launch failed: {reason}')
            console.log(f'Sleep for {retry_delay} seconds and retry "{app_name}"...')
            await asyncio.sleep(retry_delay)


@cli.command()
@click.pass_context
@coro
async def list_apps(click_ctx):
    app_ctx = click_ctx.obj['app_ctx']
    in_headless = not click_ctx.obj['is_debug']
    username = config.get_config('USERNAME')
    password = config.get_config('PASSWORD')
    url = config.get_config('CITRIX_URL')
    async with citrix_login(app_ctx, url, username, password, headless=in_headless) as page_app:
        app_map = await load_apps(app_ctx, page_app)
        return list(app_map.keys())


if __name__ == '__main__':
    cli()
