from pathlib import Path
from typing import Any


class DirectoryError(Exception):
    def __init__(self, given_dir: Path, *args):
        super().__init__(args)
        self.given_dir = given_dir

    def __str__(self):
        return f"The given Directory or Path: {self.given_dir} is not existing"


class NotIterable(Exception):
    def __init__(self, value: Any, *args):
        super().__init__(args)
        self.value = value

    def __str__(self):
        return f"The given value of type: {type(self.value)} is not iteratable"

class YamlSyntaxError(Exception):
    def __init__(self, exception: Any, *args):
        super().__init__(args)
        self.value = exception

    def __str__(self):
        return f"Syntax Error in your YAML File:\n {self.value}"
