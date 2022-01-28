import logging
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Union, Tuple

import pywinauto
from rich.pretty import pprint
from pywinauto import Desktop


logger = logging.getLogger(__name__)
BIN_RUNNER = r"C:\Program Files (x86)\Citrix\ICA Client\wfcrun32.exe"


def run_ica(ica_file: Union[Path, str], runner=BIN_RUNNER):
    logger.debug('Using runner from: {}'.format(BIN_RUNNER))

    ica_file = Path(ica_file)
    with tempfile.TemporaryDirectory() as tempdir:
        tmp_ica = Path(tempdir) / 'temp.ica'
        shutil.copy(ica_file, tmp_ica)
        ret = subprocess.call([str(runner), str(tmp_ica)])


def check(key: str, timeout=6000) -> Tuple[bool, str]:
    # windows = Desktop(backend="uia").windows()
    # pprint([w.window_text() for w in windows])

    if key == 'Remote Desktop Manager':
        _start = time.time()
        while time.time() - _start < timeout:
            window = Desktop(backend="uia").window(title='Remote Desktop Manager')
            try:
                logger.debug(f'Found title="{window.window_text()}" (className={window.class_name()})')
                return False, 'Failed due to error dialog'
            except pywinauto.findwindows.ElementNotFoundError:
                # Not found the error dialog
                pass

            window = Desktop(backend="uia").window(
                title_re=r'^Remote Desktop Manager.*',
                class_name='Transparent Windows Client')
            try:
                logger.debug(f'Found title="{window.window_text()}" (className={window.class_name()})')
                return True, 'OK'
            except pywinauto.findwindows.ElementNotFoundError:
                # Not found the opened app
                pass
        return False, 'Failed due to time out'
    else:
        logger.warning(f'No checking rules for "{key}". Assuming successful.')
        return True, 'No checking rules'


if __name__ == '__main__':
    from rich.logging import RichHandler
    logging.basicConfig(
        level=logging.NOTSET,
        format='[%(name)s] %(message)s',
        handlers=[RichHandler(rich_tracebacks=True)]
    )

    check_app()

