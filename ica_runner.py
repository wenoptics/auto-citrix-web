import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

from rich import print


BIN_RUNNER = r"C:\Program Files (x86)\Citrix\ICA Client\wfcrun32.exe"

print('Using runner from:', BIN_RUNNER)


def run_ica(ica_file: str):
    ica_file = Path(ica_file)
    with tempfile.TemporaryDirectory() as tempdir:
        test_file = Path(tempdir) / 'test.ica'
        shutil.copy(ica_file, test_file)
        ret = subprocess.call([BIN_RUNNER, str(ica_file)])
