from pathlib import Path
import os
from heracless.utils.exceptions import DirectoryError

def path_exists(path: Path, create_path: bool):
    if not os.path.exists(path):
        if not create_path:
            raise DirectoryError(path)
        else:
            if not os.path.exists(path.parent):
                os.makedirs(path.parent)
            os.mknod(path)