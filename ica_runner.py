import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Union


logger = logging.getLogger(__name__)
BIN_RUNNER = r"C:\Program Files (x86)\Citrix\ICA Client\wfcrun32.exe"


def run_ica(ica_file: Union[Path, str], runner=BIN_RUNNER):
    logger.debug('Using runner from: {}'.format(BIN_RUNNER))

    ica_file = Path(ica_file)
    with tempfile.TemporaryDirectory() as tempdir:
        test_file = Path(tempdir) / 'test.ica'
        shutil.copy(ica_file, test_file)
        ret = subprocess.call([str(runner), str(ica_file)])


if __name__ == '__main__':
    from rich.logging import RichHandler
    logging.basicConfig(
        level=logging.NOTSET,
        format='[%(name)s] %(message)s',
        handlers=[RichHandler(rich_tracebacks=True)]
    )
