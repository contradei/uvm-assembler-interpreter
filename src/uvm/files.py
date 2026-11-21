"""Publish complete output files without truncating previous results."""

import os
from pathlib import Path
import tempfile


def atomic_write(path, data):
    """Write beside the destination and atomically replace it on success."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as file:
            temporary = Path(file.name)
            file.write(data)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
