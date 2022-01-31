import configparser
from pathlib import Path

settings = configparser.ConfigParser()
cfg_path = Path('.secrets.ini').resolve()
settings.read(cfg_path)


def get_config(key: str, sec='auth'):
    val = settings.get(sec, key)
    if val is None:
        raise ValueError(f'Config key={key} not found in section "{sec}". File: "{cfg_path}"')
    return val
