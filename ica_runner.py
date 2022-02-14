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


def run_ica(ica_file: Union[Path, str], runner):
    logger.debug('Runner path: {}'.format(runner))

    ica_file = Path(ica_file)
    with tempfile.TemporaryDirectory() as tempdir:
        tmp_ica = Path(tempdir) / 'temp.ica'
        shutil.copy(ica_file, tmp_ica)
        # The return code seems always to be 0
        try:
            _ = subprocess.call([str(runner), str(tmp_ica)], timeout=5)
        except subprocess.TimeoutExpired:
            # Sometimes, by double-clicking the .lnk to launch makes the process stuck forever. Not sure why.
            logger.warning('Timeout while waiting for runner process has not exited. But assume nothing.')


async def _check_rdm(ctx: Context, timeout=120) -> Tuple[bool, str]:
    """Check if there's any positive or negative rules matching"""

    with ctx.console.status("Looking for matching rules...", spinner='line'):
        _start = time.time()
        while time.time() - _start < timeout:
            has_failure = False
            for w in Desktop(backend="uia").windows(class_name='#32770', top_level_only=True):
                # "#32770" is either the opening dialog, or the dialog that reports connection error.
                try:
                    _text = ''.join(w.children_texts())
                    logger.debug(f'Found title="{w.window_text()}"'
                                 f' className="{w.class_name()}" '
                                 f' allText="{_text[:30]}"')
                    if 'did not launch successfully' in _text or 'resource is not available' in _text:
                        # Try to close the dialog
                        for c in filter(lambda i: 'button' in str(i.class_name()).lower(), w.children()):
                            if c.class_name and c.texts() == ['Close']:
                                c.click()
                                break
                        has_failure = True
                except pywinauto.findwindows.ElementNotFoundError:
                    # Not found the error dialog
                    pass
            if has_failure:
                return False, 'Failed due to detecting the error dialog(s)'

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
