import dataclasses

import rich


@dataclasses.dataclass
class Context:
    console: rich.console.Console
