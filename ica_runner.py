import asyncio
import logging
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Union, Tuple

import pywinauto
import rich.console
from pywinauto import Desktop

from context import Context

logger = logging.getLogger(__name__)
BIN_RUNNER = r"C:\Program Files (x86)\Citrix\ICA Client\wfcrun32.exe"


def run_ica(ica_file: Union[Path, str], runner=BIN_RUNNER):
    logger.debug('Using runner from: {}'.format(BIN_RUNNER))

    ica_file = Path(ica_file)
    with tempfile.TemporaryDirectory() as tempdir:
        tmp_ica = Path(tempdir) / 'temp.ica'
        shutil.copy(ica_file, tmp_ica)
        ret = subprocess.call([str(runner), str(tmp_ica)])


async def _check_rdm(ctx: Context, timeout=120) -> Tuple[bool, str]:

    with ctx.console.status("[bold orange]Looking for matching rules...", spinner='dots'):
        _start = time.time()
        while time.time() - _start < timeout:
            w = Desktop(backend="uia").window(title='Citrix Workspace App')
            try:
                logger.debug(f'Found title="{w.window_text()}" (className="{w.class_name()}")')
                if 'did not launch successfully' in ''.join(w.static.texts()):
                    # Try to close the dialog
                    w.CloseButton.click()
                    return False, 'Failed due to detecting the error dialog'
            except pywinauto.findwindows.ElementNotFoundError:
                # Not found the error dialog
                pass

            w = Desktop(backend="uia").window(
                title_re=r'^Remote Desktop Manager.*',
                class_name='Transparent Windows Client')
            try:
                logger.debug(f'Found title="{w.window_text()}" (className="{w.class_name()}")')
                return True, 'OK'
            except pywinauto.findwindows.ElementNotFoundError:
                # Not found the opened app
                pass
            await asyncio.sleep(1)

    return False, 'Failed due to time out'


async def check(ctx: Context, key: str, timeout=120) -> Tuple[bool, str]:
    # windows = Desktop(backend="uia").windows()
    # pprint([w.window_text() for w in windows])

    logger.info(f'Checking launch rules for {key} (timeout={timeout}s)')
    try:
        if key == 'Remote Desktop Manager':
            return await _check_rdm(ctx, timeout)
        else:
            logger.warning(f'No checking rules for "{key}". Assuming successful.')
            return True, 'No checking rules'
    except Exception as e:
        ctx.console.print_exception(show_locals=True)
        return False, str(e)

if __name__ == '__main__':
    from rich.logging import RichHandler
    logging.basicConfig(
        level=logging.NOTSET,
        format='[%(name)s] %(message)s',
        handlers=[RichHandler(rich_tracebacks=True)]
    )

    asyncio.run(
        check(Context(rich.console.Console()), 'Remote Desktop Manager')
    )
