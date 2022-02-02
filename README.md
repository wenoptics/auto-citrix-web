# AutoCitrixWeb

Some automations to help fix some crappy technology.

e.g.
 - Auto login to Citrix app store
 - Auto skip the pointless "security" check
 - Download and launch the ICA apps with retries until the app opens

## Usages

### 1. List your available apps

```bash
poetry run python ./main.py list-apps
```

```text
[01/31/22 12:00:02] DEBUG    [asyncio] Using proactor: IocpProactor                                                                                              proactor_events.py:625
[01/31/22 12:00:03] DEBUG    [citrix_web] Navigating to https://ctxstore.***.***/***/index.html                                                                      citrix_web.py:37
[01/31/22 12:00:04] DEBUG    [citrix_web] Page loaded.                                                                                                                 citrix_web.py:39
[01/31/22 12:00:05] DEBUG    [citrix_web] Applied user inputs.                                                                                                         citrix_web.py:44
[12:00:05] Waiting for login response...                                                                                                                               citrix_web.py:51
                                                                                                                                                                       citrix_web.py:52
           
           You may need to respond to the login SSO request...
           
           
[01/31/22 12:00:32] DEBUG    [citrix_web] Log on button clicked.                                                                                                       citrix_web.py:54
[12:00:32] Skip Check applied.                                                                                                                                         citrix_web.py:58
[12:00:34] Available apps (7): ['Google Chrome', 'NICE DCV 2016', 'Nice DCV 2019', 'PuTTY', 'Remote Desktop', 'Remote Desktop Manager', 'Ultra VNC viewer']            citrix_web.py:81

Process finished with exit code 0
```

### 2. Launch app with retries

e.g.

```bash
poetry run python ./main.py start --app-name="Remote Desktop Manager"
```

More options:

```bash
poetry run python ./main.py start --help
```

```text
Usage: main.py start [OPTIONS]

Options:
  --app-name TEXT        The app name to start
  --retry INTEGER        Retry times. 0 to disable retry
  --retry-delay INTEGER  Retry delay in seconds
  --help                 Show this message and exit.
```

### 3. Debug mode

Debug mode will disable the `headless` on browser, so that you can
 see what's happening.

e.g.
```bash
poetry run python ./main.py --debug list-apps
```

## Limitations

- Only tested on Windows
- You may need to write your own `check` rules for the retry to work. You may use
  [the existing `_check_rdm()`](./ica_runner.py) as an example.
