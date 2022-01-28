import configparser

settings = configparser.ConfigParser()
settings.read('.secrets.ini')


def get_config(key: str, sec='auth'):
    return settings.get(sec, key)
