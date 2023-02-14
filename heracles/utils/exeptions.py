from pathlib import Path


class DirectoryError(Exception):
    def __init__(self, given_dir: Path, *args):
        super().__init__(args)
        self.given_dir = given_dir

    def __str__(self):
        return f"The given Directory or Path: {self.given_dir} is not existing"
